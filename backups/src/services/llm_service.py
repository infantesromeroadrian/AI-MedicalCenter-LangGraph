from openai import OpenAI
import json
import asyncio
from typing import Dict, List, Any, Optional
import logging
import os
import time
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from src.config.config import GROQ_API_KEY, OPENAI_API_KEY, LLM_MODEL, DEFAULT_TEMPERATURE, MAX_TOKENS, LLM_PROVIDER

logger = logging.getLogger(__name__)

class LLMService:
    """Service to handle interactions with LLM models."""
    
    def __init__(self, model: str = LLM_MODEL, temperature: float = DEFAULT_TEMPERATURE):
        """Initialize the LLM service with a model."""
        self.model = model
        self.temperature = temperature
        self.provider = LLM_PROVIDER
        
        # Check if we have valid API keys for chosen provider
        if self.provider == "openai" and not OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY not set. Cannot proceed without valid API keys.")
            raise ValueError("OPENAI_API_KEY environment variable is required but not set")
        elif self.provider == "groq" and not GROQ_API_KEY:
            logger.error("GROQ_API_KEY not set. Cannot proceed without valid API keys.")
            raise ValueError("GROQ_API_KEY environment variable is required but not set")
        else:
            self.client = self._initialize_client()
            logger.info(f"LLMService initialized with provider: {self.provider}, model: {model}")
        
    def _initialize_client(self):
        """Initialize the OpenAI client configured to use the appropriate API."""
        try:
            if self.provider == "groq":
                return OpenAI(
                    api_key=GROQ_API_KEY,
                    base_url="https://api.groq.com/openai/v1"
                )
            else:  # Default to OpenAI
                return OpenAI(
                    api_key=OPENAI_API_KEY
                )
        except Exception as e:
            logger.error(f"Failed to initialize client: {e}")
            raise
    
    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((ConnectionError, TimeoutError))
    )
    async def generate_response(self, 
                          system_prompt: str, 
                          user_prompt: str, 
                          temperature: Optional[float] = None) -> str:
        """Generate a response from the LLM based on system and user prompts with retry logic."""
        try:
            temp = temperature if temperature is not None else self.temperature
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            # Create a coroutine to run in an event loop
            async def call_api():
                # Use a loop.run_in_executor to run the synchronous API call in a separate thread
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=temp
                    )
                )
                return response.choices[0].message.content
            
            # Execute the coroutine with retry logic
            result = await call_api()
            return result

        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            raise RuntimeError(f"Failed to generate response from LLM: {str(e)}")
    
    async def classify_specialty(self, query: str) -> Dict[str, Any]:
        """Classify which medical specialty is most appropriate for a given query."""
        system_prompt = """You are a medical triage AI that determines which medical specialty is most appropriate 
        for handling a patient query. Analyze the query and return a JSON object with the following fields:
        - recommended_specialty: The most appropriate medical specialty
        - confidence: A number between 0 and 1 indicating your confidence in this recommendation
        - reasoning: Brief explanation for your recommendation
        - alternative_specialties: List of other potentially relevant specialties
        
        Available specialties: cardiology, neurology, pediatrics, oncology, dermatology, psychiatry, 
        internal_medicine, emergency_medicine
        
        IMPORTANT: Your response must be a valid JSON object and nothing else.
        """
        
        user_prompt = f"Patient query: {query}\n\nPlease classify which medical specialty should handle this query. Return ONLY a JSON object."
        
        try:
            # Call the LLM for classification
            response = await self.generate_response(system_prompt, user_prompt, temperature=0.1)
                
            # Log the raw response for debugging
            logger.debug(f"Raw classification response: {response[:100]}...")
            
            # Try to detect if the response isn't valid JSON and extract JSON
            if not response.strip().startswith('{'):
                # Find the first occurrence of '{' and the last occurrence of '}'
                start = response.find('{')
                end = response.rfind('}')
                
                if start >= 0 and end > start:
                    # Extract the JSON portion
                    json_portion = response[start:end+1]
                    logger.warning(f"Extracted JSON from non-JSON response: {json_portion[:50]}...")
                    response = json_portion
                else:
                    raise json.JSONDecodeError("No JSON object found in response", response, 0)
            
            # Parse JSON response
            classification = json.loads(response)
            
            # Validate the required fields
            required_fields = ["recommended_specialty", "confidence", "reasoning"]
            for field in required_fields:
                if field not in classification:
                    logger.warning(f"Missing required field '{field}' in classification response")
                    # Raise exception for missing fields instead of fallback
                    raise ValueError(f"LLM response missing required field: {field}")
            
            if "alternative_specialties" not in classification:
                classification["alternative_specialties"] = []
                
            return classification
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing specialty classification JSON: {e}")
            logger.error(f"Raw response causing error: {response[:200]}")
            raise ValueError(f"Failed to parse LLM response as JSON: {str(e)}")
        except Exception as e:
            logger.error(f"Error in specialty classification: {e}")
            raise RuntimeError(f"Failed to classify medical specialty: {str(e)}") 
from openai import OpenAI
import json
import asyncio
from typing import Dict, List, Any, Optional
import logging
import os
import time
import hashlib
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

from src.config.config import GROQ_API_KEY, OPENAI_API_KEY, LLM_MODEL, DEFAULT_TEMPERATURE, MAX_TOKENS, LLM_PROVIDER

logger = logging.getLogger(__name__)

class LLMResponseCache:
    """Sistema de cache simple para respuestas LLM."""
    
    def __init__(self, max_size: int = 100):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.access_times: Dict[str, float] = {}
    
    def _get_key(self, system_prompt: str, user_prompt: str, temperature: float) -> str:
        """Generar clave de cache basada en los prompts."""
        content = f"{system_prompt}|{user_prompt}|{temperature}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, system_prompt: str, user_prompt: str, temperature: float) -> Optional[str]:
        """Obtener respuesta del cache si existe."""
        key = self._get_key(system_prompt, user_prompt, temperature)
        
        if key in self.cache:
            self.access_times[key] = time.time()
            logger.debug(f"Cache hit for key: {key[:8]}...")
            return self.cache[key]["response"]
        
        return None
    
    def set(self, system_prompt: str, user_prompt: str, temperature: float, response: str):
        """Almacenar respuesta en cache."""
        key = self._get_key(system_prompt, user_prompt, temperature)
        
        # Limpiar cache si está lleno
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        self.cache[key] = {
            "response": response,
            "timestamp": time.time()
        }
        self.access_times[key] = time.time()
        logger.debug(f"Cache stored for key: {key[:8]}...")
    
    def _evict_oldest(self):
        """Eliminar la entrada más antigua del cache."""
        if not self.access_times:
            return
            
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        del self.cache[oldest_key]
        del self.access_times[oldest_key]
        logger.debug(f"Evicted oldest cache entry: {oldest_key[:8]}...")

class LLMService:
    """Service to handle interactions with LLM models."""
    
    def __init__(self, model: str = LLM_MODEL, temperature: float = DEFAULT_TEMPERATURE):
        """Initialize the LLM service with a model."""
        self.model = model
        self.temperature = temperature
        self.provider = LLM_PROVIDER
        
        # Métricas de performance
        self.total_requests = 0
        self.total_tokens_used = 0
        self.average_response_time = 0.0
        self.error_count = 0
        
        # Sistema de cache
        self.cache = LLMResponseCache()
        
        # Validar y configurar cliente
        self._validate_api_keys()
        self.client = self._initialize_client()
        
        logger.info(f"LLMService initialized with provider: {self.provider}, model: {model}")
        
    def _validate_api_keys(self):
        """Validar que las claves API necesarias estén disponibles."""
        if self.provider == "openai" and not OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY not set. Cannot proceed without valid API keys.")
            raise ValueError("OPENAI_API_KEY environment variable is required but not set")
        elif self.provider == "groq" and not GROQ_API_KEY:
            logger.error("GROQ_API_KEY not set. Cannot proceed without valid API keys.")
            raise ValueError("GROQ_API_KEY environment variable is required but not set")
        
    def _initialize_client(self):
        """Initialize the OpenAI client configured to use the appropriate API."""
        try:
            if self.provider == "groq":
                return OpenAI(
                    api_key=GROQ_API_KEY,
                    base_url="https://api.groq.com/openai/v1",
                    timeout=60.0
                )
            else:  # Default to OpenAI
                return OpenAI(
                    api_key=OPENAI_API_KEY,
                    timeout=60.0
                )
        except Exception as e:
            logger.error(f"Failed to initialize client: {e}")
            raise
    
    @retry(
        wait=wait_exponential(multiplier=2, min=4, max=20),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((ConnectionError, TimeoutError, OSError))
    )
    async def generate_response(self, 
                          system_prompt: str, 
                          user_prompt: str, 
                          temperature: Optional[float] = None,
                          use_cache: bool = True) -> str:
        """Generate a response from the LLM based on system and user prompts with retry logic."""
        start_time = time.time()
        temp = temperature if temperature is not None else self.temperature
        
        try:
            # Verificar cache primero
            if use_cache:
                cached_response = self.cache.get(system_prompt, user_prompt, temp)
                if cached_response:
                    logger.debug("Returning cached response")
                    return cached_response
            
            # Verificar conectividad antes de hacer llamada costosa
            if not await self._check_connectivity():
                return self._get_offline_response(user_prompt)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            async def call_api():
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=temp,
                        max_tokens=MAX_TOKENS
                    )
                )
                return response
            
            # Ejecutar llamada a API
            response = await call_api()
            result = response.choices[0].message.content
            
            # Actualizar métricas
            response_time = time.time() - start_time
            self._update_metrics(response, response_time)
            
            # Guardar en cache
            if use_cache:
                self.cache.set(system_prompt, user_prompt, temp, result)
            
            logger.debug(f"LLM response generated in {response_time:.2f}s")
            return result

        except Exception as e:
            self.error_count += 1
            logger.error(f"Error generating LLM response: {e}")
            
            # Intentar respuesta offline antes de fallar completamente
            if "Connection" in str(e) or "network" in str(e).lower():
                logger.warning("Network error detected, attempting offline response")
                return self._get_offline_response(user_prompt)
            
            raise RuntimeError(f"Failed to generate response from LLM: {str(e)}")
    
    def _update_metrics(self, response, response_time: float):
        """Actualizar métricas de performance."""
        self.total_requests += 1
        
        # Actualizar tiempo promedio de respuesta
        if self.average_response_time == 0:
            self.average_response_time = response_time
        else:
            self.average_response_time = (self.average_response_time + response_time) / 2
        
        # Contar tokens si está disponible
        if hasattr(response, 'usage') and response.usage:
            self.total_tokens_used += response.usage.total_tokens
    
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
            # Usar cache para clasificaciones
            response = await self.generate_response(system_prompt, user_prompt, temperature=0.1, use_cache=True)
                
            logger.debug(f"Raw classification response: {response[:100]}...")
            
            # Limpiar respuesta para asegurar JSON válido
            response = self._clean_json_response(response)
            
            # Parse JSON response
            classification = json.loads(response)
            
            # Validar campos requeridos
            classification = self._validate_classification_response(classification)
                
            return classification
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing specialty classification JSON: {e}")
            logger.error(f"Raw response causing error: {response[:200]}")
            raise ValueError(f"Failed to parse LLM response as JSON: {str(e)}")
        except Exception as e:
            logger.error(f"Error in specialty classification: {e}")
            raise RuntimeError(f"Failed to classify medical specialty: {str(e)}")
    
    def _clean_json_response(self, response: str) -> str:
        """Limpiar respuesta para asegurar JSON válido."""
        response = response.strip()
        
        # Si la respuesta no empieza con '{', buscar el JSON
        if not response.startswith('{'):
            start = response.find('{')
            end = response.rfind('}')
            
            if start >= 0 and end > start:
                response = response[start:end+1]
                logger.warning(f"Extracted JSON from non-JSON response")
            else:
                raise json.JSONDecodeError("No JSON object found in response", response, 0)
        
        return response
    
    def _validate_classification_response(self, classification: Dict[str, Any]) -> Dict[str, Any]:
        """Validar y completar la respuesta de clasificación."""
        required_fields = ["recommended_specialty", "confidence", "reasoning"]
        
        for field in required_fields:
            if field not in classification:
                logger.warning(f"Missing required field '{field}' in classification response")
                raise ValueError(f"LLM response missing required field: {field}")
        
        if "alternative_specialties" not in classification:
            classification["alternative_specialties"] = []
        
        # Validar confianza está en rango correcto
        if not 0 <= classification["confidence"] <= 1:
            classification["confidence"] = max(0, min(1, classification["confidence"]))
            logger.warning("Confidence score was out of range [0,1], adjusted")
        
        return classification
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de performance del servicio LLM."""
        return {
            "total_requests": self.total_requests,
            "total_tokens_used": self.total_tokens_used,
            "average_response_time": round(self.average_response_time, 3),
            "error_count": self.error_count,
            "error_rate": round(self.error_count / max(1, self.total_requests) * 100, 2),
            "cache_stats": {
                "cache_size": len(self.cache.cache),
                "max_cache_size": self.cache.max_size
            },
            "provider": self.provider,
            "model": self.model
        }
    
    def clear_cache(self):
        """Limpiar el cache de respuestas."""
        cache_size = len(self.cache.cache)
        self.cache.cache.clear()
        self.cache.access_times.clear()
        logger.info(f"Cleared LLM cache, removed {cache_size} entries")
    
    def reset_metrics(self):
        """Resetear métricas de performance."""
        self.total_requests = 0
        self.total_tokens_used = 0
        self.average_response_time = 0.0
        self.error_count = 0
        logger.info("LLM performance metrics reset")
    
    async def health_check(self) -> Dict[str, Any]:
        """Verificar salud del servicio LLM."""
        try:
            # Test simple
            test_response = await self.generate_response(
                "You are a test assistant.", 
                "Respond with only 'OK'", 
                temperature=0.0, 
                use_cache=False
            )
            
            is_healthy = "OK" in test_response.upper()
            
            return {
                "healthy": is_healthy,
                "provider": self.provider,
                "model": self.model,
                "test_response": test_response[:50],
                "metrics": self.get_performance_metrics()
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "healthy": False,
                "provider": self.provider,
                "model": self.model,
                "error": str(e),
                "metrics": self.get_performance_metrics()
            }
    
    async def _check_connectivity(self) -> bool:
        """Verificar conectividad básica con la API."""
        try:
            # Test simple de conectividad
            loop = asyncio.get_event_loop()
            
            # Timeout muy corto para test rápido
            test_client = OpenAI(
                api_key=self.client.api_key,
                base_url=self.client.base_url if hasattr(self.client, 'base_url') else None,
                timeout=5.0  # Timeout muy corto
            )
            
            await loop.run_in_executor(
                None,
                lambda: test_client.models.list()
            )
            return True
            
        except Exception as e:
            logger.warning(f"Connectivity check failed: {e}")
            return False
    
    def _get_offline_response(self, user_prompt: str) -> str:
        """Generar respuesta offline cuando no hay conectividad."""
        
        # Detectar idioma
        is_spanish = any(char in user_prompt.lower() for char in ["á", "é", "í", "ó", "ú", "ñ", "¿", "¡"])
        
        if is_spanish:
            offline_response = """Lo siento, actualmente estoy experimentando problemas de conectividad con los servicios de IA. 

Por favor:
- Verifica tu conexión a internet
- Intenta nuevamente en unos minutos
- Si el problema persiste, contacta al administrador del sistema

IMPORTANTE: Si tienes una emergencia médica, llama al 911 o acude al hospital más cercano inmediatamente.

Para consultas no urgentes, puedes intentar reformular tu pregunta cuando el servicio esté disponible."""
        else:
            offline_response = """I'm sorry, I'm currently experiencing connectivity issues with AI services.

Please:
- Check your internet connection  
- Try again in a few minutes
- If the problem persists, contact the system administrator

IMPORTANT: If you have a medical emergency, call 911 or go to the nearest hospital immediately.

For non-urgent questions, you can try rephrasing your question when the service is available."""
        
        logger.info("Returned offline response due to connectivity issues")
        return offline_response 
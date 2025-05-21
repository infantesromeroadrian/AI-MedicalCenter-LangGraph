import json
from typing import Dict, List, Any, Optional, TypedDict, Annotated, Literal
import logging
from pydantic import BaseModel, Field
import asyncio

from src.agents.agent_factory import AgentFactory
from src.agents.base_agent import BaseMedicalAgent, AgentState
from src.models.data_models import UserQuery, ConsensusResponse, AgentResponse
from src.utils.helpers import detect_medical_emergencies
from src.services.llm_service import LLMService

logger = logging.getLogger(__name__)

class MedicalGraphState(TypedDict):
    """State for the medical agent graph."""
    user_query: UserQuery
    emergency_status: Dict[str, Any]
    specialty_recommendation: Dict[str, Any]
    agent_responses: Dict[str, AgentResponse]
    consensus_response: Optional[ConsensusResponse]


class MedicalAgentGraph:
    """
    Implementation that coordinates multiple medical specialty agents.
    
    The workflow:
    1. Triage - Check for emergencies and determine appropriate specialties
    2. Expert consultation - Get responses from appropriate medical specialists
    3. Consensus building - Combine responses into a unified answer
    """
    
    def __init__(self):
        """Initialize the medical agent coordinator."""
        self.llm_service = LLMService()
        self.agent_factory = AgentFactory(llm_service=self.llm_service)
        self.specialty_agents = {}
    
    async def check_emergency(self, state: MedicalGraphState) -> MedicalGraphState:
        """Check if the query describes a medical emergency."""
        user_query = state["user_query"]
        
        # Check for emergency keywords
        emergency_status = detect_medical_emergencies(user_query.query)
        
        logger.info(f"Emergency check result: {emergency_status['is_emergency']}")
        
        return {
            **state,
            "emergency_status": emergency_status
        }
    
    async def determine_specialty(self, state: MedicalGraphState) -> MedicalGraphState:
        """Determine which medical specialty is most appropriate for the query."""
        user_query = state["user_query"]
        
        # If user specified a specialty, use that
        if user_query.specialty and user_query.specialty in self.agent_factory._registry:
            specialty_recommendation = {
                "recommended_specialty": user_query.specialty,
                "confidence": 1.0,
                "reasoning": "User specified this specialty directly",
                "alternative_specialties": []
            }
        else:
            # Otherwise, use the LLM to classify the specialty
            specialty_recommendation = await self.llm_service.classify_specialty(user_query.query)
        
        logger.info(f"Determined specialty: {specialty_recommendation['recommended_specialty']}")
        
        return {
            **state,
            "specialty_recommendation": specialty_recommendation
        }
    
    async def consult_specialists(self, state: MedicalGraphState) -> MedicalGraphState:
        """Consult with the appropriate medical specialist agents."""
        user_query = state["user_query"]
        specialty_recommendation = state["specialty_recommendation"]
        
        # Ensure we have the needed agents
        main_specialty = specialty_recommendation["recommended_specialty"]
        alternative_specialties = specialty_recommendation.get("alternative_specialties", [])
        
        # Limit to top 2 alternatives to prevent too many calls
        specialties_to_consult = [main_specialty] + alternative_specialties[:2]
        
        # Get unique specialties
        specialties_to_consult = list(set(specialties_to_consult))
        
        # Filter out unsupported specialties to prevent errors
        valid_specialties = []
        for specialty in specialties_to_consult:
            try:
                if specialty not in self.specialty_agents:
                    self.specialty_agents[specialty] = self.agent_factory.create_agent(specialty)
                valid_specialties.append(specialty)
            except ValueError as e:
                logger.warning(f"Skipping unsupported specialty '{specialty}': {e}")
        
        # Gather responses from each relevant specialist
        agent_responses = {}
        
        # Process concurrently for efficiency
        tasks = []
        for specialty in valid_specialties:
            agent = self.specialty_agents[specialty]
            tasks.append(agent.process_query(user_query.query, user_query.context))
        
        # Wait for all agent responses
        responses = await asyncio.gather(*tasks)
        
        # Map responses to specialties
        for idx, specialty in enumerate(valid_specialties):
            agent_responses[specialty] = responses[idx]
        
        logger.info(f"Received responses from {len(agent_responses)} agents")
        
        return {
            **state,
            "agent_responses": agent_responses
        }
    
    async def build_consensus(self, state: MedicalGraphState) -> MedicalGraphState:
        """Build a consensus response from multiple specialist responses."""
        agent_responses = state["agent_responses"]
        specialty_recommendation = state["specialty_recommendation"]
        emergency_status = state["emergency_status"]
        
        # Get the primary specialty response
        primary_specialty = specialty_recommendation["recommended_specialty"]
        
        # Handle the case where the primary specialty doesn't have a response
        if primary_specialty not in agent_responses:
            logger.warning(f"Primary specialty {primary_specialty} doesn't have a response. Using fallback.")
            # Find an alternative if available
            if agent_responses:
                # Use the first available specialty as primary
                primary_specialty = list(agent_responses.keys())[0]
                logger.info(f"Using {primary_specialty} as fallback primary specialty")
            else:
                # Create a dummy response if no specialties responded
                logger.warning("No specialty agents provided responses, using internal medicine fallback")
                primary_specialty = "internal_medicine"
                # Create a generic fallback response for the query
                agent_responses[primary_specialty] = AgentResponse(
                    specialty=primary_specialty,
                    response="I apologize, but I don't have enough specialized information to answer your question accurately. " +
                            "Please consult with a healthcare provider for personalized advice.",
                    confidence=0.3,
                    recommendations=["Consult with a healthcare provider for accurate diagnosis", 
                                   "Consider seeking a second opinion if symptoms persist"],
                    sources=None
                )
                
        primary_response = agent_responses[primary_specialty].response
        
        # Get contributing specialties and their insights
        contributing_specialties = []
        additional_insights = {}
        
        for specialty, response in agent_responses.items():
            if specialty != primary_specialty:
                contributing_specialties.append(specialty)
                # Extract a summary of the insight from this specialty
                additional_insights[specialty] = response.response
        
        # Gather all recommendations from all specialists
        all_recommendations = []
        for specialty, response in agent_responses.items():
            if response.recommendations:
                all_recommendations.extend(response.recommendations)
        
        # Add emergency warning if detected
        if emergency_status["is_emergency"]:
            all_recommendations.insert(0, emergency_status["recommendation"])
        
        # Create the consensus response
        consensus_response = ConsensusResponse(
            primary_specialty=primary_specialty,
            primary_response=primary_response,
            contributing_specialties=contributing_specialties,
            additional_insights=additional_insights,
            patient_recommendations=all_recommendations
        )
        
        logger.info(f"Built consensus response with primary specialty: {primary_specialty}")
        
        return {
            **state,
            "consensus_response": consensus_response
        }
    
    async def process_query(self, query: str, specialty: Optional[str] = None, 
                     context: Optional[Dict[str, Any]] = None) -> ConsensusResponse:
        """
        Process a medical query through a sequential workflow.
        
        Args:
            query: The user's medical question
            specialty: Optional specific medical specialty to target
            context: Optional additional context for the query
            
        Returns:
            A consensus response from the medical agents
        """
        try:
            logger.info(f"Processing query: '{query}' with specialty: {specialty}")
            
            # Create the user query model
            user_query = UserQuery(
                query=query,
                specialty=specialty,
                context=context
            )
            
            # Initialize the graph state
            state: MedicalGraphState = {
                "user_query": user_query,
                "emergency_status": {},
                "specialty_recommendation": {},
                "agent_responses": {},
                "consensus_response": None
            }
            
            # Execute workflow steps sequentially
            state = await self.check_emergency(state)
            state = await self.determine_specialty(state)
            state = await self.consult_specialists(state)
            state = await self.build_consensus(state)
            
            logger.info("Workflow execution completed successfully")
            
            if state["consensus_response"] is None:
                logger.error("Workflow completed but consensus_response is None")
                raise ValueError("No consensus response generated")
                
            return state["consensus_response"]
        except Exception as e:
            logger.error(f"Error executing medical agent workflow: {e}", exc_info=True)
            # Return a fallback response
            fallback_response = ConsensusResponse(
                primary_specialty="internal_medicine",
                primary_response="I apologize, but I encountered an error processing your medical query. " +
                               "Please retry your question or contact a healthcare provider directly."
            )
            logger.info("Returning fallback response due to error")
            return fallback_response 
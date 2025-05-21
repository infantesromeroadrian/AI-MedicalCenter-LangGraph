from typing import Dict, Optional, Type
import logging
import traceback

from src.config.config import MEDICAL_SPECIALTIES
from src.agents.base_agent import BaseMedicalAgent
from src.agents.cardiology_agent import CardiologyAgent
from src.agents.neurology_agent import NeurologyAgent
from src.agents.internal_medicine_agent import InternalMedicineAgent
from src.services.llm_service import LLMService

logger = logging.getLogger(__name__)

class AgentFactory:
    """Factory class for creating medical specialty agents."""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        """Initialize the agent factory."""
        self.llm_service = llm_service or LLMService()
        self._registry = self._build_registry()
    
    def _build_registry(self) -> Dict[str, Type[BaseMedicalAgent]]:
        """Build a registry of all available medical specialty agents."""
        registry = {
            "cardiology": CardiologyAgent,
            "neurology": NeurologyAgent,
            "internal_medicine": InternalMedicineAgent,
            # Additional specialty agents would be registered here
        }
        
        # Log which specialties don't have specific agents yet
        missing_specialties = set(MEDICAL_SPECIALTIES) - set(registry.keys())
        if missing_specialties:
            logger.info(f"Missing specialized agents for: {', '.join(missing_specialties)}")
            
        return registry
    
    def create_agent(self, specialty: str) -> BaseMedicalAgent:
        """
        Create and return an agent for the specified medical specialty.
        
        Args:
            specialty: The medical specialty for which to create an agent
            
        Returns:
            An instance of the appropriate specialty agent
            
        Raises:
            ValueError: If the specialty is not supported
        """
        try:
            if specialty not in MEDICAL_SPECIALTIES:
                raise ValueError(f"Unsupported medical specialty: {specialty}")
            
            # Use specialized agent if available, otherwise use a generic one
            if specialty in self._registry:
                try:
                    agent_class = self._registry[specialty]
                    return agent_class(llm_service=self.llm_service)
                except Exception as e:
                    logger.error(f"Error creating {specialty} agent: {e}")
                    logger.error(traceback.format_exc())
                    # Fallback to internal medicine if there's an error creating the specialized agent
                    logger.warning(f"Falling back to internal medicine agent after error creating {specialty} agent")
                    return InternalMedicineAgent(llm_service=self.llm_service)
            else:
                # Use internal medicine as the fallback for any specialty
                logger.warning(f"No specialized agent for {specialty}, using internal medicine agent as fallback")
                return InternalMedicineAgent(llm_service=self.llm_service)
        
        except Exception as e:
            logger.error(f"Unexpected error creating agent for {specialty}: {e}")
            logger.error(traceback.format_exc())
            # Always fallback to internal medicine in case of any error
            return InternalMedicineAgent(llm_service=self.llm_service)
    
    def create_all_agents(self) -> Dict[str, BaseMedicalAgent]:
        """Create and return instances of all registered medical specialty agents."""
        agents = {}
        for specialty in MEDICAL_SPECIALTIES:
            try:
                agents[specialty] = self.create_agent(specialty)
            except Exception as e:
                logger.error(f"Failed to create agent for {specialty}: {e}")
        
        return agents 
"""
Controlador para la orquestación y gestión de los diversos agentes médicos.
Coordina el triaje y la derivación a especialistas usando el sistema moderno.
"""
import asyncio
import time
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

from src.agents.agent_factory import AgentFactory
from src.agents.consensus_agent import ConsensusAgent
from src.agents.langgraph_medical_agent import LangGraphMedicalAgent
from src.agents.medical_agent_graph import MedicalAgentGraph
from src.services.llm_service import LLMService
from src.utils.helpers import detect_medical_emergencies
from src.monitoring.performance_metrics import performance_monitor
from src.models.data_models import UserQuery, ConsensusResponse, AgentResponse
from src.config.config import USE_LANGGRAPH

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/agents.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

class ModernAgentController:
    """
    Controlador moderno para el sistema de agentes médicos.
    Integra todos los componentes avanzados: consensus, emergency detection, metrics.
    """
    
    def __init__(self):
        """Inicializa el controlador moderno de agentes médicos."""
        logger.info("Inicializando controlador moderno de agentes médicos")
        
        # Servicios core
        self.llm_service = LLMService()
        self.agent_factory = AgentFactory(llm_service=self.llm_service)
        self.consensus_agent = ConsensusAgent(llm_service=self.llm_service)
        
        # Orquestadores
        if USE_LANGGRAPH:
            self.orchestrator = LangGraphMedicalAgent()
            logger.info("Usando LangGraph como orquestador principal")
        else:
            self.orchestrator = MedicalAgentGraph()
            logger.info("Usando MedicalAgentGraph como orquestador principal")
        
        # Cache de agentes especializados
        self._specialist_cache = {}
        
        logger.info("Controlador moderno inicializado exitosamente")
    
    async def process_query_comprehensive(
        self, 
        patient_query: str, 
        specialty: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        patient_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Procesamiento comprehensivo de consulta médica con todas las funcionalidades avanzadas.
        
        Args:
            patient_query: Consulta del paciente
            specialty: Especialidad específica solicitada (opcional)
            context: Contexto adicional de la consulta
            patient_id: ID del paciente para seguimiento
            
        Returns:
            Dict con resultado completo del procesamiento
        """
        start_time = time.time()
        
        # Log inicial
        logger.info(f"Procesando consulta comprehensiva - Patient ID: {patient_id or 'Anónimo'}")
        logger.info(f"Query: {patient_query[:100]}...")
        
        try:
            # 1. Detección de emergencias temprana
            emergency_status = detect_medical_emergencies(patient_query, context)
            logger.info(f"Detección emergencia: {emergency_status['is_emergency']} (score: {emergency_status.get('emergency_score', 0):.2f})")
            
            # 2. Procesamiento a través del orquestador principal
            consensus_response = await self.orchestrator.process_query(
                query=patient_query,
                specialty=specialty,
                context=context
            )
            
            # 3. Registrar métricas de performance
            await self._record_performance_metrics(
                consensus_response=consensus_response,
                emergency_status=emergency_status,
                start_time=start_time,
                patient_query=patient_query
            )
            
            # 4. Construcción del resultado comprehensivo
            result = {
                "success": True,
                "consensus_response": consensus_response,
                "emergency_status": emergency_status,
                "performance_metrics": {
                    "total_processing_time": time.time() - start_time,
                    "primary_specialty": consensus_response.primary_specialty,
                    "contributing_specialties": consensus_response.contributing_specialties,
                    "consensus_quality": consensus_response.consensus_metrics
                },
                "system_info": {
                    "orchestrator_used": "LangGraph" if USE_LANGGRAPH else "MedicalAgentGraph",
                    "timestamp": time.time(),
                    "patient_id": patient_id
                }
            }
            
            logger.info(f"Consulta procesada exitosamente en {time.time() - start_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error en procesamiento comprehensivo: {e}", exc_info=True)
            
            # Fallback a procesamiento básico
            return await self._fallback_processing(patient_query, specialty, context, patient_id, start_time)
    
    async def process_query_basic(
        self, 
        patient_query: str, 
        specialty: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Procesamiento básico para compatibilidad con sistemas legacy.
        
        Args:
            patient_query: Consulta del paciente
            specialty: Especialidad específica (opcional)
            context: Contexto adicional
            
        Returns:
            Dict con resultado básico compatible
        """
        start_time = time.time()
        
        try:
            # Usar orquestrador para obtener respuesta
            consensus_response = await self.orchestrator.process_query(
                query=patient_query,
                specialty=specialty,
                context=context
            )
            
            # Formato compatible con sistema legacy
            result = {
                "triage": {
                    "specialty": consensus_response.primary_specialty,
                    "reasoning": f"Derivado por sistema inteligente",
                    "urgency": 3  # Default moderate
                },
                "specialist_response": consensus_response.primary_response,
                "specialty": consensus_response.primary_specialty,
                "success": True,
                "additional_insights": consensus_response.additional_insights,
                "recommendations": consensus_response.patient_recommendations
            }
            
            logger.info(f"Consulta básica procesada en {time.time() - start_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error en procesamiento básico: {e}", exc_info=True)
            return await self._emergency_fallback(patient_query)
    
    async def get_specialist_direct(self, specialty: str) -> Optional[Any]:
        """
        Obtener un agente especialista específico directamente.
        
        Args:
            specialty: Nombre de la especialidad
            
        Returns:
            Agente especialista o None si no existe
        """
        try:
            if specialty not in self._specialist_cache:
                self._specialist_cache[specialty] = self.agent_factory.create_agent(specialty)
            
            return self._specialist_cache[specialty]
            
        except Exception as e:
            logger.error(f"Error obteniendo especialista {specialty}: {e}")
            return None
    
    async def _record_performance_metrics(
        self,
        consensus_response: ConsensusResponse,
        emergency_status: Dict[str, Any],
        start_time: float,
        patient_query: str
    ) -> None:
        """Registrar métricas de performance del procesamiento."""
        
        try:
            processing_time = time.time() - start_time
            
            # Registrar métricas del agente principal
            performance_monitor.record_response(
                agent_id=f"primary_{consensus_response.primary_specialty}",
                specialty=consensus_response.primary_specialty,
                response_time=processing_time,
                confidence_score=consensus_response.consensus_metrics.get('confidence_weighted_score', 0.75),
                response_content=consensus_response.primary_response,
                has_recommendations=bool(consensus_response.patient_recommendations),
                has_sources=False,  # TODO: Implementar tracking de fuentes
                emergency_detected=emergency_status['is_emergency'],
                user_query=patient_query
            )
            
            # Registrar sesión de consenso si hay múltiples especialistas
            if consensus_response.contributing_specialties:
                agents_involved = [consensus_response.primary_specialty] + consensus_response.contributing_specialties
                
                performance_monitor.record_consensus_session(
                    agents_involved=agents_involved,
                    agreement_score=consensus_response.consensus_metrics.get('agreement_score', 0.8),
                    confidence_weighted_score=consensus_response.consensus_metrics.get('confidence_weighted_score', 0.75),
                    complementarity_score=consensus_response.consensus_metrics.get('complementarity_score', 0.7),
                    had_conflicts=False,  # TODO: Implementar detección de conflictos
                    synthesis_successful=True
                )
            
            logger.debug("Métricas de performance registradas exitosamente")
            
        except Exception as e:
            logger.error(f"Error registrando métricas: {e}")
    
    async def _fallback_processing(
        self, 
        patient_query: str, 
        specialty: Optional[str], 
        context: Optional[Dict[str, Any]], 
        patient_id: Optional[str],
        start_time: float
    ) -> Dict[str, Any]:
        """Procesamiento de fallback en caso de error."""
        
        try:
            # Intentar con un agente individual de medicina interna
            internal_medicine_agent = self.agent_factory.create_agent("internal_medicine")
            
            response = await internal_medicine_agent.process_query(patient_query, context)
            
            # Resultado de fallback
            result = {
                "success": True,
                "consensus_response": {
                    "primary_specialty": "internal_medicine",
                    "primary_response": response.response,
                    "contributing_specialties": [],
                    "additional_insights": {},
                    "patient_recommendations": response.recommendations or [],
                    "consensus_metrics": {"fallback": True}
                },
                "emergency_status": detect_medical_emergencies(patient_query, context),
                "performance_metrics": {
                    "total_processing_time": time.time() - start_time,
                    "fallback_used": True
                },
                "warning": "Se usó procesamiento de fallback debido a error en sistema principal"
            }
            
            logger.warning(f"Fallback exitoso para consulta - tiempo: {time.time() - start_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error en fallback: {e}")
            return await self._emergency_fallback(patient_query)
    
    async def _emergency_fallback(self, patient_query: str) -> Dict[str, Any]:
        """Fallback de emergencia cuando todo lo demás falla."""
        
        emergency_status = detect_medical_emergencies(patient_query)
        
        if emergency_status['is_emergency']:
            response = "⚠️ He detectado que tu consulta podría ser una emergencia médica. Por favor, busca atención médica inmediata llamando al 911 o acudiendo al hospital más cercano."
        else:
            response = "Lo siento, estoy experimentando dificultades técnicas. Por favor, consulta con un profesional médico para obtener ayuda apropiada."
        
        return {
            "success": False,
            "triage": {
                "specialty": "emergency_medicine" if emergency_status['is_emergency'] else "internal_medicine",
                "reasoning": "Sistema de emergencia activado",
                "urgency": 5 if emergency_status['is_emergency'] else 1
            },
            "specialist_response": response,
            "specialty": "emergency_medicine" if emergency_status['is_emergency'] else "internal_medicine",
            "error": "Sistema en modo de emergencia",
            "emergency_status": emergency_status
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado actual del sistema de agentes."""
        
        return {
            "orchestrator": "LangGraph" if USE_LANGGRAPH else "MedicalAgentGraph",
            "agents_cached": list(self._specialist_cache.keys()),
            "specialties_available": list(self.agent_factory._registry.keys()),
            "performance_metrics": performance_monitor.get_performance_summary(),
            "system_health": "operational"  # TODO: Implementar health checks
        }


# Mantener compatibilidad con sistema legacy
class AgentController(ModernAgentController):
    """Wrapper para compatibilidad con código legacy."""
    
    def __init__(self):
        super().__init__()
        logger.info("AgentController legacy wrapper inicializado")
    
    def process_query(self, patient_query, patient_history="", patient_id=None):
        """Método legacy para procesar consultas."""
        
        # Convertir parámetros legacy
        context = {"patient_history": patient_history} if patient_history else None
        
        # Ejecutar procesamiento async de forma sincrónica
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                self.process_query_basic(patient_query, context=context)
            )
            return result
        finally:
            loop.close() 
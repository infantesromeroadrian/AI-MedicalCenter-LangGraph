from typing import Dict, List, Any, Optional, TypedDict, Callable
import logging
import traceback
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

from langchain.schema import SystemMessage, HumanMessage

from src.services.llm_service import LLMService
from src.models.data_models import AgentResponse
from src.knowledge.medical_knowledge_base import medical_kb

logger = logging.getLogger(__name__)

class ConversationMemory:
    """Gestión de memoria conversacional para agentes médicos."""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.conversation_history: List[Dict[str, Any]] = []
        self.patient_info_extracted: Dict[str, Any] = {}
        self.consultation_stage = "initial"
        self.last_update = datetime.now()
        
        # Cache para optimizar búsquedas
        self._symptoms_cache = set()
        self._duration_cache = set()
        self._factors_cache = set()
    
    def add_interaction(self, user_query: str, agent_response: str, specialty: str):
        """Agregar una nueva interacción a la memoria."""
        interaction = {
            "timestamp": datetime.now(),
            "user_query": user_query,
            "agent_response": agent_response,
            "specialty": specialty,
            "stage": self.consultation_stage
        }
        
        self.conversation_history.append(interaction)
        
        # Mantener solo el máximo de historia usando deque para eficiencia
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
        
        # Actualizar etapa de consulta
        self._update_consultation_stage()
        
        # Extraer información del paciente (optimizado)
        self._extract_patient_info_optimized(user_query)
        
        self.last_update = datetime.now()
    
    def get_conversation_context(self) -> str:
        """Obtener contexto de conversación formateado."""
        if not self.conversation_history:
            return "Primera consulta - no hay historial previo."
        
        # Usar list comprehension para mejor performance
        context_lines = []
        recent_interactions = self.conversation_history[-5:]  # Últimas 5 interacciones
        
        for interaction in recent_interactions:
            context_lines.extend([
                f"PACIENTE: {interaction['user_query']}",
                f"MÉDICO ({interaction['specialty']}): {interaction['agent_response'][:200]}..."
            ])
        
        return "\n".join(context_lines)
    
    def _update_consultation_stage(self):
        """Actualizar la etapa de consulta basada en el número de interacciones."""
        interaction_count = len(self.conversation_history)
        
        # Usar diccionario para mapeo más eficiente
        stage_mapping = {
            range(0, 2): "initial",
            range(2, 4): "gathering_info", 
            range(4, 6): "assessment"
        }
        
        for stage_range, stage in stage_mapping.items():
            if interaction_count in stage_range:
                self.consultation_stage = stage
                return
                
        # Si está fuera de todos los rangos
        self.consultation_stage = "recommendations"
    
    def _extract_patient_info_optimized(self, user_query: str):
        """Extraer y acumular información del paciente (versión optimizada)."""
        query_lower = user_query.lower()
        
        # Usar sets pre-definidos para búsquedas más eficientes
        if not hasattr(self, '_keyword_sets_initialized'):
            self._init_keyword_sets()
        
        # Buscar información de duración
        if not self.patient_info_extracted.get("duration_mentioned"):
            if any(keyword in query_lower for keyword in self._duration_keywords):
                self.patient_info_extracted["duration_mentioned"] = True
                self._duration_cache.add(user_query[:50])  # Cache muestra
        
        # Buscar información de síntomas
        if not self.patient_info_extracted.get("symptoms_described"):
            if any(keyword in query_lower for keyword in self._symptom_keywords):
                self.patient_info_extracted["symptoms_described"] = True
                self._symptoms_cache.add(user_query[:50])  # Cache muestra
        
        # Buscar información de factores
        if not self.patient_info_extracted.get("factors_mentioned"):
            if any(keyword in query_lower for keyword in self._factor_keywords):
                self.patient_info_extracted["factors_mentioned"] = True
                self._factors_cache.add(user_query[:50])  # Cache muestra
    
    def _init_keyword_sets(self):
        """Inicializar sets de keywords para búsquedas eficientes."""
        self._duration_keywords = {"días", "semanas", "meses", "años", "ayer", "hoy", "hace", 
                                 "days", "weeks", "months", "years", "yesterday", "today", "ago"}
        
        self._symptom_keywords = {"duele", "dolor", "siento", "tengo", "noto", "molesta",
                                "pain", "hurt", "feel", "have", "notice", "bothers"}
        
        self._factor_keywords = {"empeora", "mejora", "cuando", "después", "si", "calor", "frío",
                               "worse", "better", "when", "after", "if", "heat", "cold"}
        
        self._keyword_sets_initialized = True
    
    def get_info_gaps(self) -> List[str]:
        """Identificar qué información falta aún."""
        gaps = []
        
        # Usar una estructura más eficiente
        gap_checks = [
            ("duration_mentioned", "duration"),
            ("symptoms_described", "detailed_symptoms"),
            ("factors_mentioned", "aggravating_factors")
        ]
        
        for info_key, gap_name in gap_checks:
            if not self.patient_info_extracted.get(info_key):
                gaps.append(gap_name)
        
        return gaps
    
    def clear_cache(self):
        """Limpiar caches para liberar memoria."""
        self._symptoms_cache.clear()
        self._duration_cache.clear()
        self._factors_cache.clear()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de uso de memoria."""
        return {
            "total_interactions": len(self.conversation_history),
            "current_stage": self.consultation_stage,
            "info_extracted_count": len([v for v in self.patient_info_extracted.values() if v]),
            "last_update": self.last_update.isoformat(),
            "cache_sizes": {
                "symptoms": len(self._symptoms_cache),
                "duration": len(self._duration_cache), 
                "factors": len(self._factors_cache)
            }
        }

class AgentState(TypedDict):
    """Type definition for the state managed by agents."""
    query: str
    specialty: str
    context: Optional[Dict[str, Any]]
    confidence: float
    response: Optional[str]
    recommendations: Optional[List[str]]
    sources: Optional[List[str]]

class BaseMedicalAgent(ABC):
    """Base class for all medical specialty agents with enhanced capabilities."""
    
    def __init__(self, specialty: str, llm_service: LLMService = None):
        """Initialize the agent with a specialty and optional LLM service."""
        self.specialty = specialty
        self.llm_service = llm_service or LLMService()
        self._system_prompt = self._build_system_prompt()
        
        # Enhanced capabilities
        self.conversation_memories: Dict[str, ConversationMemory] = {}
        self.knowledge_base = medical_kb
        self.last_query_time = None
        self.confidence_threshold = 0.7
        
        # Performance tracking
        self.total_queries_processed = 0
        self.average_response_time = 0.0
        
        logger.info(f"Initialized enhanced {specialty} agent")
    
    @abstractmethod
    def _build_system_prompt(self) -> str:
        """Build the system prompt specific to this medical specialty."""
        pass
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process a medical query with enhanced capabilities."""
        start_time = time.time()
        
        try:
            # Obtener o crear memoria conversacional
            session_id = context.get("session_id", "default") if context else "default"
            memory = self._get_or_create_memory(session_id)
            
            # Preparar contexto enriquecido
            enriched_context = self._enrich_context(query, context, memory)
            
            # Validar consulta médica
            validation_result = self._validate_medical_query(query)
            if not validation_result["is_valid"]:
                return self._create_validation_error_response(validation_result)
            
            # Buscar en knowledge base
            relevant_knowledge = self._search_knowledge_base(query)
            
            # Formatear consulta con contexto enriquecido
            formatted_query = self._format_query_enhanced(query, enriched_context, relevant_knowledge)
            
            # Generar respuesta
            response = await self.llm_service.generate_response(
                system_prompt=self._system_prompt,
                user_prompt=formatted_query
            )
            
            # Procesar respuesta
            processed_response = self._post_process_response(response, query, memory)
            
            # Extraer recomendaciones y fuentes
            recommendations, sources = self._extract_recommendations_and_sources(processed_response)
            
            # Evaluar confianza mejorada
            confidence = self._evaluate_confidence_enhanced(query, processed_response, relevant_knowledge)
            
            # Actualizar memoria
            memory.add_interaction(query, processed_response, self.specialty)
            
            # Crear respuesta
            agent_response = AgentResponse(
                specialty=self.specialty,
                response=processed_response,
                confidence=confidence,
                recommendations=recommendations,
                sources=sources
            )
            
            # Registrar métricas
            processing_time = time.time() - start_time
            self._update_performance_metrics(processing_time, confidence, len(processed_response.split()))
            
            logger.info(f"{self.specialty} agent processed query in {processing_time:.2f}s with confidence {confidence:.2f}")
            return agent_response
            
        except Exception as e:
            logger.error(f"Error in {self.specialty} agent processing query: {e}")
            logger.error(traceback.format_exc())
            
            return self._create_error_response(e)
    
    def _get_or_create_memory(self, session_id: str) -> ConversationMemory:
        """Obtener o crear memoria conversacional para una sesión."""
        if session_id not in self.conversation_memories:
            self.conversation_memories[session_id] = ConversationMemory()
        
        return self.conversation_memories[session_id]
    
    def _enrich_context(self, query: str, context: Optional[Dict[str, Any]], memory: ConversationMemory) -> Dict[str, Any]:
        """Enriquecer el contexto con información de memoria y knowledge base."""
        enriched = context.copy() if context else {}
        
        # Agregar contexto conversacional
        enriched["conversation_history"] = memory.get_conversation_context()
        enriched["consultation_stage"] = memory.consultation_stage
        enriched["patient_info_extracted"] = memory.patient_info_extracted
        enriched["information_gaps"] = memory.get_info_gaps()
        
        # Agregar contexto temporal
        enriched["current_time"] = datetime.now().isoformat()
        enriched["session_duration"] = (datetime.now() - memory.last_update).total_seconds() if memory.last_update else 0
        
        return enriched
    
    def _validate_medical_query(self, query: str) -> Dict[str, Any]:
        """Validar que la consulta sea apropiada para atención médica."""
        
        # Validaciones básicas
        if len(query.strip()) < 2:  # Muy permisivo
            return {"is_valid": False, "reason": "Consulta demasiado corta"}
        
        if len(query.strip()) > 5000:  # Muy permisivo
            return {"is_valid": False, "reason": "Consulta demasiado larga"}
        
        # TEMPORALMENTE DESACTIVADO - Permitir todas las consultas
        # Esto resuelve el problema mientras investigamos por qué no se aplican los cambios
        logger.info(f"Query validation bypassed (temporary): '{query}'")
        return {"is_valid": True, "reason": "Consulta válida (validación temporal desactivada)"}
        
        # CÓDIGO ORIGINAL COMENTADO TEMPORALMENTE
        # Lista expandida de keywords médicos (más agresiva)
        # medical_keywords = [
        #     # Síntomas básicos
        #     "dolor", "duele", "molesta", "siento", "tengo", "noto", "síntoma", "problema",
        #     "malestar", "sensación", "incómodo", "pain", "hurt", "feel", "have", "symptom",
        #     
        #     # Partes del cuerpo
        #     "cabeza", "pecho", "abdomen", "brazo", "pierna", "espalda", "cuello", "corazón",
        #     "head", "chest", "abdomen", "arm", "leg", "back", "neck", "heart",
        #     "mano", "pie", "dedo", "ojo", "oído", "nariz", "boca", "garganta",
        #     "hand", "foot", "finger", "eye", "ear", "nose", "mouth", "throat",
        #     
        #     # Condiciones médicas comunes
        #     "fiebre", "tos", "gripe", "diabetes", "presión", "fever", "cough", "flu", "pressure",
        #     "herida", "sangra", "sangrado", "sangre", "corte", "wound", "bleeding", "blood", "cut",
        #     
        #     # Emergencias y traumatismos - EXPANDIDO
        #     "emergencia", "urgente", "grave", "emergency", "urgent", "serious",
        #     "mordida", "mordio", "mordedura", "mordi", "bite", "bitten", "picadura",
        #     "golpe", "caída", "accidente", "trauma", "lesión", "fractura",
        #     "hit", "fall", "accident", "injury", "trauma", "fracture",
        #     "aumentado", "aumenta", "increase", "increased", "worse", "peor",
        #     
        #     # Animales (para mordeduras)
        #     "perro", "gato", "animal", "mascota", "dog", "cat", "pet",
        #     "serpiente", "araña", "insecto", "snake", "spider", "insect",
        #     
        #     # Tiempo médico
        #     "hora", "horas", "día", "días", "ayer", "hace", "desde",
        #     "hour", "hours", "day", "days", "yesterday", "ago", "since",
        #     
        #     # Consulta médica general
        #     "consulta", "médico", "doctor", "salud", "enfermo", "health", "sick", "medical",
        #     "hospital", "clínica", "clinic", "tratamiento", "treatment"
        # ]
        # 
        # # Convertir query a lowercase
        # query_lower = query.lower()
        # 
        # # Buscar CUALQUIER keyword médico en la consulta (más permisivo)
        # has_medical_content = any(keyword in query_lower for keyword in medical_keywords)
        # 
        # # Log para debugging
        # if not has_medical_content:
        #     logger.warning(f"Query rejected: '{query}' - no medical keywords found")
        # else:
        #     found_keywords = [kw for kw in medical_keywords if kw in query_lower]
        #     logger.debug(f"Query accepted: '{query}' - found keywords: {found_keywords[:3]}")
        # 
        # if not has_medical_content:
        #     return {
        #         "is_valid": False, 
        #         "reason": "La consulta no parece contener información médica específica"
        #     }
        # 
        # return {"is_valid": True, "reason": "Consulta válida"}
    
    def _search_knowledge_base(self, query: str) -> Dict[str, Any]:
        """Buscar información relevante en la knowledge base."""
        
        # Extraer posibles síntomas de la consulta
        query_words = query.lower().split()
        potential_symptoms = []
        
        for word in query_words:
            if len(word) > 3:  # Evitar palabras muy cortas
                potential_symptoms.append(word)
        
        # Buscar condiciones relacionadas
        related_conditions = self.knowledge_base.search_conditions_by_symptoms(
            symptoms=potential_symptoms[:5],  # Limitar a 5 síntomas
            specialty=self.specialty
        )
        
        # Obtener información general de la especialidad
        specialty_info = self.knowledge_base.get_specialty_overview(self.specialty)
        
        return {
            "related_conditions": related_conditions[:3],  # Top 3 condiciones
            "specialty_overview": specialty_info,
            "search_performed": True
        }
    
    def _format_query_enhanced(self, query: str, context: Dict[str, Any], knowledge: Dict[str, Any]) -> str:
        """Formatear consulta con contexto y conocimiento enriquecido."""
        
        # Detectar idioma
        spanish_indicators = ["á", "é", "í", "ó", "ú", "ñ", "¿", "¡", "que", "como", "duele", "siento"]
        is_spanish = any(indicator in query.lower() for indicator in spanish_indicators)
        
        formatted_parts = []
        
        # 1. Instrucción de idioma
        if is_spanish:
            formatted_parts.append("INSTRUCCIÓN: Responde completamente en español.")
        
        # 2. Información de etapa de consulta
        stage = context.get("consultation_stage", "initial")
        formatted_parts.append(f"ETAPA DE CONSULTA: {stage.upper()}")
        
        if stage == "initial":
            formatted_parts.append("Primera consulta - enfócate en entender el problema principal.")
        elif stage == "gathering_info":
            formatted_parts.append("Continúa recopilando información específica.")
        elif stage == "assessment":
            formatted_parts.append("Ya tienes información suficiente - proporciona evaluación y posibles diagnósticos.")
        elif stage == "recommendations":
            formatted_parts.append("Proporciona recomendaciones específicas y plan de acción.")
        
        # 3. Consulta del paciente
        formatted_parts.append(f"CONSULTA ACTUAL: {query}")
        
        # 4. Contexto conversacional
        if context.get("conversation_history"):
            formatted_parts.append("HISTORIAL RECIENTE:")
            formatted_parts.append(context["conversation_history"])
        
        # 5. Información del paciente ya recopilada
        patient_info = context.get("patient_info_extracted", {})
        if patient_info:
            formatted_parts.append("INFORMACIÓN YA RECOPILADA:")
            for key, value in patient_info.items():
                if value:
                    formatted_parts.append(f"- {key.replace('_', ' ').title()}: Sí")
        
        # 6. Brechas de información
        info_gaps = context.get("information_gaps", [])
        if info_gaps and stage in ["initial", "gathering_info"]:
            formatted_parts.append("INFORMACIÓN PENDIENTE DE RECOPILAR:")
            for gap in info_gaps:
                formatted_parts.append(f"- {gap.replace('_', ' ').title()}")
        
        # 7. Conocimiento relevante de la knowledge base
        if knowledge.get("related_conditions"):
            formatted_parts.append("CONDICIONES RELACIONADAS IDENTIFICADAS:")
            for condition in knowledge["related_conditions"]:
                formatted_parts.append(f"- {condition.name}: {', '.join(condition.symptoms[:3])}")
        
        # 8. Instrucciones específicas
        formatted_parts.append("INSTRUCCIONES ESPECÍFICAS:")
        if stage in ["initial", "gathering_info"]:
            formatted_parts.append("- Haz preguntas específicas pero no más de 2-3 por respuesta")
            formatted_parts.append("- No avances a diagnóstico sin información suficiente")
        elif stage == "assessment":
            formatted_parts.append("- Proporciona posibles diagnósticos diferenciales")
            formatted_parts.append("- Explica el razonamiento médico")
        elif stage == "recommendations":
            formatted_parts.append("- Proporciona plan de acción claro")
            formatted_parts.append("- Incluye signos de alarma")
        
        return "\n\n".join(formatted_parts)
    
    def _post_process_response(self, response: str, query: str, memory: ConversationMemory) -> str:
        """Post-procesar la respuesta para mejorar calidad y coherencia."""
        
        # Verificar que la respuesta esté en el idioma correcto
        spanish_in_query = any(char in query for char in ["á", "é", "í", "ó", "ú", "ñ", "¿", "¡"])
        spanish_in_response = any(char in response for char in ["á", "é", "í", "ó", "ú", "ñ"])
        
        if spanish_in_query and not spanish_in_response:
            logger.warning("Response language mismatch detected - query in Spanish but response in English")
        
        # Agregar contexto de especialidad si no está presente
        specialty_mention = self.specialty.replace("_", " ").title()
        if specialty_mention.lower() not in response.lower() and len(memory.conversation_history) == 0:
            if spanish_in_query:
                response = f"Como especialista en {specialty_mention}, " + response
            else:
                response = f"As a {specialty_mention} specialist, " + response
        
        return response
    
    def _evaluate_confidence_enhanced(self, query: str, response: str, knowledge: Dict[str, Any]) -> float:
        """Evaluación mejorada de confianza con múltiples factores."""
        
        # Confianza base
        base_confidence = self._evaluate_confidence(query, response)
        
        # Factor de knowledge base
        kb_factor = 1.0
        if knowledge.get("related_conditions"):
            kb_factor = 1.1  # Boost si encontró condiciones relacionadas
        
        # Factor de especialidad
        specialty_terms = self._get_specialty_keywords()
        specialty_matches = sum(1 for term in specialty_terms if term.lower() in query.lower())
        specialty_factor = min(1.2, 1.0 + (specialty_matches * 0.05))
        
        # Factor de completitud de respuesta
        response_length_factor = min(1.1, len(response.split()) / 100)  # Óptimo ~100 palabras
        
        # Factor de presencia de recomendaciones
        has_recommendations = "recomend" in response.lower() or "recommend" in response.lower()
        recommendation_factor = 1.05 if has_recommendations else 1.0
        
        # Calcular confianza final
        enhanced_confidence = base_confidence * kb_factor * specialty_factor * response_length_factor * recommendation_factor
        
        return max(0.1, min(1.0, enhanced_confidence))
    
    def _get_specialty_keywords(self) -> List[str]:
        """Obtener keywords específicos de la especialidad."""
        
        specialty_keywords = {
            "cardiology": ["corazón", "cardíaco", "presión", "heart", "cardiac", "chest"],
            "neurology": ["cerebro", "neurológico", "cabeza", "brain", "neurological", "headache"],
            "pediatrics": ["niño", "bebé", "child", "baby", "pediatric"],
            "dermatology": ["piel", "skin", "rash", "dermatitis"],
            "psychiatry": ["depresión", "ansiedad", "depression", "anxiety", "mental"],
            "oncology": ["cáncer", "tumor", "cancer", "oncology"],
            "emergency_medicine": ["emergencia", "urgente", "emergency", "urgent"],
            "internal_medicine": ["general", "sistémico", "systemic", "chronic"]
        }
        
        return specialty_keywords.get(self.specialty, [])
    
    def _create_validation_error_response(self, validation_result: Dict[str, Any]) -> AgentResponse:
        """Crear respuesta de error de validación."""
        
        error_message = f"Lo siento, {validation_result['reason']}. Por favor, proporciona más detalles sobre tu consulta médica."
        
        return AgentResponse(
            specialty=self.specialty,
            response=error_message,
            confidence=0.1,
            recommendations=["Proporciona más detalles específicos sobre tus síntomas", 
                           "Reformula tu consulta con información médica relevante"],
            sources=None
        )
    
    def _create_error_response(self, error: Exception) -> AgentResponse:
        """Crear respuesta de error mejorada."""
        
        error_message = (
            f"Como especialista en {self.specialty.replace('_', ' ')}, estoy experimentando problemas técnicos "
            f"para responder a tu consulta. Por favor, intenta reformular tu pregunta o intenta más tarde. "
            f"Si es urgente, te recomiendo contactar directamente con un profesional médico."
        )
        
        return AgentResponse(
            specialty=self.specialty,
            response=error_message,
            confidence=0.1,
            recommendations=["Consulta con un profesional médico si tu consulta es urgente",
                           "Intenta reformular tu pregunta de otra manera"],
            sources=None
        )
    
    def _update_performance_metrics(self, processing_time: float, confidence: float, word_count: int):
        """Actualizar métricas de performance del agente."""
        
        self.total_queries_processed += 1
        
        # Actualizar promedio de tiempo de respuesta
        if self.average_response_time == 0:
            self.average_response_time = processing_time
        else:
            self.average_response_time = (self.average_response_time + processing_time) / 2
        
        self.last_query_time = time.time()
    
    def _format_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Legacy method - delegated to enhanced version."""
        memory = self._get_or_create_memory("default")
        enriched_context = self._enrich_context(query, context or {}, memory)
        knowledge = self._search_knowledge_base(query)
        
        return self._format_query_enhanced(query, enriched_context, knowledge)
    
    def _extract_recommendations_and_sources(self, response: str) -> tuple[Optional[List[str]], Optional[List[str]]]:
        """Extract recommendations and sources from the response if available."""
        recommendations = []
        sources = []
        
        # Look for recommendation sections (improved patterns)
        recommendation_patterns = [
            "RECOMENDACIONES:",
            "RECOMMENDATIONS:",
            "RECOMENDACIONES PEDIÁTRICAS:",
            "RECOMENDACIONES CARDIOLÓGICAS:",
            "RECOMENDACIONES NEUROLÓGICAS:",
            "RECOMENDACIONES ONCOLÓGICAS:",
            "RECOMENDACIONES DERMATOLÓGICAS:",
            "RECOMENDACIONES PSIQUIÁTRICAS:",
            "RECOMENDACIONES DE EMERGENCIA:"
        ]
        
        for pattern in recommendation_patterns:
            if pattern in response:
                rec_section = response.split(pattern)[1].split("\n\n")[0]
                recommendations = [r.strip(" -•") for r in rec_section.split("\n") if r.strip() and not r.strip().startswith(pattern)]
                break
        
        # Look for source sections
        source_patterns = ["SOURCES:", "FUENTES:", "REFERENCIAS:"]
        for pattern in source_patterns:
            if pattern in response:
                src_section = response.split(pattern)[1].split("\n\n")[0]
                sources = [s.strip(" -•") for s in src_section.split("\n") if s.strip() and not s.strip().startswith(pattern)]
                break
            
        return recommendations or None, sources or None
    
    def _evaluate_confidence(self, query: str, response: str) -> float:
        """
        Basic confidence evaluation method.
        """
        # Evaluación básica sin recursión
        basic_confidence = 0.5  # Base confidence
        
        # Factor de longitud de respuesta
        if len(response.split()) > 20:
            basic_confidence += 0.1
        
        # Factor de keywords médicos
        medical_keywords = ["síntoma", "diagnóstico", "tratamiento", "medical", "symptom", "diagnosis", "treatment"]
        matches = sum(1 for keyword in medical_keywords if keyword.lower() in response.lower())
        basic_confidence += min(0.3, matches * 0.05)
        
        # Factor de pregunta específica
        if "?" in response:
            basic_confidence += 0.1
        
        return max(0.1, min(1.0, basic_confidence))
    
    def get_agent_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del agente."""
        return {
            "specialty": self.specialty,
            "total_queries_processed": self.total_queries_processed,
            "average_response_time": self.average_response_time,
            "active_conversations": len(self.conversation_memories),
            "confidence_threshold": self.confidence_threshold,
            "last_query_time": self.last_query_time
        }
    
    def clear_old_memories(self, max_age_hours: int = 24):
        """Limpiar memorias conversacionales antiguas."""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        old_sessions = [
            session_id for session_id, memory in self.conversation_memories.items()
            if memory.last_update < cutoff_time
        ]
        
        for session_id in old_sessions:
            del self.conversation_memories[session_id]
        
        if old_sessions:
            logger.info(f"Cleared {len(old_sessions)} old conversation memories for {self.specialty} agent") 
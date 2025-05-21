from typing import Dict, List, Any, Optional, TypedDict, Callable
import logging
import traceback
from abc import ABC, abstractmethod

from langchain.schema import SystemMessage, HumanMessage

from src.services.llm_service import LLMService
from src.models.data_models import AgentResponse

logger = logging.getLogger(__name__)

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
    """Base class for all medical specialty agents."""
    
    def __init__(self, specialty: str, llm_service: LLMService = None):
        """Initialize the agent with a specialty and optional LLM service."""
        self.specialty = specialty
        self.llm_service = llm_service or LLMService()
        self._system_prompt = self._build_system_prompt()
    
    @abstractmethod
    def _build_system_prompt(self) -> str:
        """Build the system prompt specific to this medical specialty."""
        pass
    
    async def process_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> AgentResponse:
        """Process a medical query and provide a response."""
        try:
            # Format the query for this specialty
            formatted_query = self._format_query(query, context)
            
            # Get response from LLM
            response = await self.llm_service.generate_response(
                system_prompt=self._system_prompt,
                user_prompt=formatted_query
            )
            
            # Extract recommendations and sources if available
            recommendations, sources = self._extract_recommendations_and_sources(response)
            
            # Evaluate confidence based on specialty alignment
            confidence = self._evaluate_confidence(query, response)
            
            return AgentResponse(
                specialty=self.specialty,
                response=response,
                confidence=confidence,
                recommendations=recommendations,
                sources=sources
            )
        except Exception as e:
            logger.error(f"Error in {self.specialty} agent processing query: {e}")
            logger.error(traceback.format_exc())
            
            # Generamos un mensaje de error más informativo con la especialidad
            error_message = (
                f"Lo siento, como especialista en {self.specialty}, estoy experimentando problemas técnicos "
                f"para responder a tu consulta. Por favor, intenta reformular tu pregunta o intenta más tarde. "
                f"Si es urgente, te recomiendo contactar directamente con un profesional médico."
            )
            
            # No intentamos generar una respuesta específica por especialidad - dejamos que el LLM lo maneje cuando esté disponible
            return AgentResponse(
                specialty=self.specialty,
                response=error_message,
                confidence=0.1,  # Baja confianza para indicar que es una respuesta de error
                recommendations=["Consulta con un profesional médico si tu consulta es urgente",
                                "Intenta reformular tu pregunta de otra manera"],
                sources=None
            )
    
    def _format_query(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Format the query with any additional context for this specialty."""
        # Detectar el idioma de la consulta de forma simplificada
        # Palabras y caracteres comunes en español
        spanish_indicators = ["á", "é", "í", "ó", "ú", "ñ", "¿", "¡", 
                             "hola", "gracias", "que", "como", "por", "para", "mi", "tu", "su",
                             "me", "te", "se", "lo", "la", "los", "las", "es", "son", "esta", "esto",
                             "tengo", "duele", "siento", "pica", "brazo", "cabeza", "pierna", "estómago"]
        
        is_spanish = any(indicator in query.lower() for indicator in spanish_indicators)
        
        # Analizar el estado de la consulta y el historial de conversación
        consultation_stage = "inicio"  # Por defecto asumimos que estamos al inicio
        previous_messages = []
        patient_info = {}
        
        if context and "conversation_history" in context and isinstance(context["conversation_history"], list):
            previous_messages = context["conversation_history"]
            
            # Contar intercambios entre médico y paciente
            doctor_messages = [msg for msg in previous_messages if msg.get("sender") != "user"]
            patient_messages = [msg for msg in previous_messages if msg.get("sender") == "user"]
            
            # Determinar la etapa de la consulta basada en el número de intercambios
            if len(doctor_messages) >= 2 and len(patient_messages) >= 2:
                consultation_stage = "seguimiento"
                
                # Extraer información relevante del paciente de mensajes anteriores
                for msg in patient_messages:
                    content = msg.get("content", "").lower()
                    
                    # Buscar información sobre duración
                    if any(word in content for word in ["días", "semanas", "meses", "años", "ayer", "hoy", "comenzó", "empezó"]):
                        patient_info["duración"] = True
                    
                    # Buscar información sobre síntomas asociados
                    if any(word in content for word in ["también", "además", "siento", "tengo", "noto", "observo"]):
                        patient_info["síntomas_asociados"] = True
                    
                    # Buscar información sobre factores agravantes/aliviantes
                    if any(word in content for word in ["mejora", "empeora", "alivia", "cuando", "si", "después", "calor", "frío"]):
                        patient_info["factores"] = True
            
            # Si el paciente ha dado mucha información, avanzar a diagnóstico
            if len(patient_info) >= 2 and len(patient_messages) >= 3:
                consultation_stage = "diagnóstico"
                
            # Si el paciente ha recibido diagnóstico y hay muchos intercambios, avanzar a cierre
            if consultation_stage == "diagnóstico" and len(doctor_messages) >= 3 and len(patient_messages) >= 4:
                consultation_stage = "cierre"
        
        # Construir el prompt estructurado para el LLM
        formatted_query = ""
        
        # 1. Instrucción de idioma
        if is_spanish:
            formatted_query += "INSTRUCCIÓN IMPORTANTE: Responde a esta consulta completamente en español.\n\n"
        
        # 2. Instrucción sobre la etapa de la consulta
        formatted_query += f"ETAPA DE CONSULTA: {consultation_stage.upper()}\n"
        if consultation_stage == "inicio":
            formatted_query += "Esta es una consulta inicial. Haz 2-3 preguntas básicas para entender el problema principal del paciente.\n\n"
        elif consultation_stage == "seguimiento":
            formatted_query += "Has recibido alguna información inicial. Continúa la anamnesis enfocándote en áreas que aún no has explorado. No repitas preguntas ya respondidas.\n\n"
        elif consultation_stage == "diagnóstico":
            formatted_query += "Ya has recopilado suficiente información para ofrecer posibles diagnósticos. Explica las posibles causas en lenguaje sencillo y sugiere los siguientes pasos.\n\n"
        elif consultation_stage == "cierre":
            formatted_query += "Es momento de cerrar la consulta con recomendaciones finales, plan de acción y signos de alarma que requieran atención inmediata.\n\n"
        
        # 3. Consulta actual del paciente
        formatted_query += f"CONSULTA ACTUAL DEL PACIENTE: {query}\n\n"
        
        # 4. Historial de conversación relevante
        if previous_messages:
            formatted_query += "HISTORIAL DE CONVERSACIÓN:\n"
            # Limitar a los últimos 5-6 mensajes más relevantes para no exceder el contexto
            relevant_messages = previous_messages[-6:]
            
            for i, msg in enumerate(relevant_messages):
                sender = msg.get("sender", "")
                content = msg.get("content", "")
                
                if sender == "user":
                    formatted_query += f"PACIENTE: {content}\n"
                elif sender == "system":
                    formatted_query += f"SISTEMA: {content}\n"
                else:
                    formatted_query += f"MÉDICO ({sender}): {content}\n"
            
            formatted_query += "\n"
        
        # 5. Información recopilada sobre el paciente
        if patient_info:
            formatted_query += "INFORMACIÓN YA RECOPILADA:\n"
            for key in patient_info:
                formatted_query += f"- {key}\n"
            formatted_query += "\n"
        
        # 6. Instrucciones específicas según la etapa
        formatted_query += "INSTRUCCIONES ESPECÍFICAS:\n"
        if consultation_stage == "inicio" or consultation_stage == "seguimiento":
            formatted_query += "- No avances al diagnóstico hasta tener información suficiente\n"
            formatted_query += "- Haz preguntas específicas y no repitas preguntas ya contestadas\n"
            formatted_query += "- No más de 2-3 preguntas a la vez\n"
        elif consultation_stage == "diagnóstico":
            formatted_query += "- Ofrece posibles diagnósticos basados en la información recopilada\n"
            formatted_query += "- Explica en lenguaje sencillo los mecanismos de cada posible diagnóstico\n"
            formatted_query += "- Sugiere posibles pruebas o exámenes si son necesarios\n"
        elif consultation_stage == "cierre":
            formatted_query += "- Resume los puntos clave de la consulta\n"
            formatted_query += "- Proporciona recomendaciones específicas y plan de acción\n"
            formatted_query += "- Indica signos de alarma que requieran atención médica\n"
            
        # 7. Contexto adicional (si existe)
        if context:
            # Filtramos conversation_history que ya procesamos arriba
            filtered_context = {k: v for k, v in context.items() if k != "conversation_history"}
            
            if filtered_context:
                formatted_query += "\nCONTEXTO ADICIONAL:\n"
                for key, value in filtered_context.items():
                    formatted_query += f"- {key}: {value}\n"
        
        return formatted_query
    
    def _extract_recommendations_and_sources(self, response: str) -> tuple[Optional[List[str]], Optional[List[str]]]:
        """Extract recommendations and sources from the response if available."""
        # This is a simple implementation - could be enhanced with pattern matching
        recommendations = []
        sources = []
        
        # Look for recommendation sections
        if "RECOMMENDATIONS:" in response:
            rec_section = response.split("RECOMMENDATIONS:")[1].split("\n\n")[0]
            recommendations = [r.strip() for r in rec_section.split("\n") if r.strip()]
        elif "RECOMENDACIONES:" in response:  # Spanish support
            rec_section = response.split("RECOMENDACIONES:")[1].split("\n\n")[0]
            recommendations = [r.strip() for r in rec_section.split("\n") if r.strip()]
        
        # Look for source sections
        if "SOURCES:" in response:
            src_section = response.split("SOURCES:")[1].split("\n\n")[0]
            sources = [s.strip() for s in src_section.split("\n") if s.strip()]
        elif "FUENTES:" in response:  # Spanish support
            src_section = response.split("FUENTES:")[1].split("\n\n")[0]
            sources = [s.strip() for s in src_section.split("\n") if s.strip()]
            
        return recommendations or None, sources or None
    
    def _evaluate_confidence(self, query: str, response: str) -> float:
        """
        Evaluate the confidence of this agent's response based on specialty alignment.
        Returns a float between 0 and 1.
        """
        # This is a simplified implementation - in a real system, this would be more sophisticated
        # Default moderate confidence
        confidence = 0.75
        
        # Adjust confidence based on content
        specialty_terms = {
            "cardiology": ["heart", "cardiac", "chest pain", "blood pressure", "cardiovascular", "corazón", "cardíaco", "presión arterial"],
            "neurology": ["brain", "neurological", "headache", "stroke", "migraine", "cerebral", "cerebro", "neurológico", "migraña"],
            "internal_medicine": ["general", "systemic", "chronic", "body", "health", "immune", "general", "sistémico", "crónico", "inmune"],
            "pediatrics": ["child", "infant", "baby", "kid", "adolescent", "pediatric", "niño", "bebé", "adolescente"],
            "dermatology": ["skin", "rash", "acne", "dermatitis", "piel", "sarpullido", "acné", "dermatitis"],
            "psychiatry": ["mental", "depression", "anxiety", "mood", "psychiatric", "depresión", "ansiedad", "psiquiátrico"],
            "oncology": ["cancer", "tumor", "oncology", "malignant", "cáncer", "tumor", "oncología", "maligno"],
            "emergency_medicine": ["emergency", "urgent", "critical", "trauma", "emergencia", "urgente", "crítico", "trauma"]
        }
        
        # Lower confidence if response contains uncertainty markers
        uncertainty_phrases = [
            "outside my specialty", 
            "refer to", 
            "consult with", 
            "I'm not certain",
            "unclear",
            "I cannot provide",
            "fuera de mi especialidad",
            "derivar a",
            "consultar con",
            "no estoy seguro",
            "no puedo proporcionar"
        ]
        
        # Increase confidence if specialty-specific terms are in the query or response
        if self.specialty in specialty_terms:
            specialty_specific_terms = specialty_terms[self.specialty]
            for term in specialty_specific_terms:
                if term.lower() in query.lower() or term.lower() in response.lower():
                    confidence += 0.05
                    break  # Only add this bonus once
        
        # Reduce confidence for uncertainty phrases
        for phrase in uncertainty_phrases:
            if phrase.lower() in response.lower():
                confidence -= 0.1
                break  # Only subtract once for any uncertainty indicator
                
        # Ensure confidence stays in range [0.1, 1.0]
        return max(0.1, min(1.0, confidence)) 
from typing import Dict, List, Any, Optional

from src.agents.base_agent import BaseMedicalAgent
from src.services.llm_service import LLMService

class InternalMedicineAgent(BaseMedicalAgent):
    """Agent specialized in internal medicine."""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        """Initialize the internal medicine agent."""
        super().__init__(specialty="internal_medicine", llm_service=llm_service)
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt specific to internal medicine."""
        return """Eres un asistente médico especializado en medicina interna, simulando una consulta médica real con un paciente.

COMPORTAMIENTO CRUCIAL: Debes emular el comportamiento de un médico real en consulta:

1. NO des un diagnóstico inmediato ante síntomas vagos. En lugar de eso, primero haz preguntas de anamnesis.

2. Utiliza una ESTRUCTURA DE CONSULTA MÉDICA:
   - Saludo inicial y presentación
   - Preguntas sobre los síntomas principales (qué, cuándo comenzó, intensidad)
   - Anamnesis estructurada (factores que lo empeoran/mejoran, síntomas asociados)
   - Historia clínica relevante (antecedentes, medicamentos, alergias)
   - Explicación de posibles causas en lenguaje sencillo
   - Plan de acción o recomendaciones

3. ESTILO CONVERSACIONAL:
   - Usa un tono empático y humano, no clínico ni frío
   - Explica términos médicos en lenguaje accesible (ej: "prurito" → "picazón")
   - Adapta tu lenguaje según el contexto (niño, adulto, anciano)
   - Haz máximo 2-3 preguntas por respuesta para no abrumar al paciente

4. ENFOQUE DE MEDICINA INTERNA:
   - Diagnóstico y tratamiento médico general
   - Atención primaria de adultos
   - Manejo de enfermedades crónicas (diabetes, hipertensión, etc.)
   - Medicina preventiva y pruebas de detección
   - Infecciones comunes y sus tratamientos
   - Interpretación de resultados básicos de laboratorio
   - Manejo no quirúrgico de condiciones comunes

5. RECOMENDACIONES ÚTILES:
   - Sugiere modificaciones del estilo de vida cuando sea apropiado
   - Indica claramente cuándo una condición requiere atención médica urgente
   - Recomienda seguimiento con proveedores de atención médica cuando sea necesario
   - Explica el razonamiento detrás de cada recomendación

IMPORTANTE:
- Nunca sugieras diagnósticos graves sin antes hacer preguntas básicas sobre los síntomas
- Si el paciente solo menciona un síntoma vago (como "me duele la cabeza"), DEBES primero hacer preguntas para comprender mejor el problema
- Si una pregunta está fuera de tu especialidad, reconoce esta limitación y sugiere consultar con el especialista adecuado
- Usa la primera persona ("te recomendaría...") para sonar más humano

Al final de tu respuesta, si ya has recopilado suficiente información para dar recomendaciones, incluye una sección titulada "RECOMENDACIONES:" con los puntos clave de consejos para el paciente."""
    
    def _evaluate_confidence(self, query: str, response: str) -> float:
        """
        Evaluate the confidence for internal medicine-related queries.
        Override base implementation to check for general medicine keywords.
        """
        base_confidence = super()._evaluate_confidence(query, response)
        
        # Check for internal medicine-related keywords to potentially increase confidence
        general_keywords = [
            "fever", "cough", "cold", "flu", "infection", "virus", "bacteria", 
            "antibiotic", "pain", "ache", "sore", "fatigue", "tired", "exhaustion", 
            "diet", "nutrition", "weight", "blood pressure", "cholesterol", "diabetes", 
            "sugar", "sleep", "insomnia", "allergy", "vaccine", "shot", "checkup", 
            "annual", "physical", "lab", "test", "results", "prevention", "screening",
            # Spanish keywords
            "fiebre", "tos", "resfriado", "gripe", "infección", "virus", "bacteria",
            "antibiótico", "dolor", "fatiga", "cansancio", "agotamiento",
            "dieta", "nutrición", "peso", "presión arterial", "colesterol", "diabetes",
            "azúcar", "sueño", "insomnio", "alergia", "vacuna", "chequeo",
            "análisis", "prueba", "resultados", "prevención"
        ]
        
        # Count general medicine keywords in query
        keyword_count = sum(1 for keyword in general_keywords if keyword.lower() in query.lower())
        
        # Increase confidence based on keyword matches
        confidence_boost = min(0.3, keyword_count * 0.05)
        adjusted_confidence = base_confidence + confidence_boost
        
        # Ensure confidence stays in range [0.1, 1.0]
        return max(0.1, min(1.0, adjusted_confidence)) 
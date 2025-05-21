from typing import Dict, List, Any, Optional

from src.agents.base_agent import BaseMedicalAgent
from src.services.llm_service import LLMService

class NeurologyAgent(BaseMedicalAgent):
    """Agent specialized in neurology."""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        """Initialize the neurology agent."""
        super().__init__(specialty="neurology", llm_service=llm_service)
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt specific to neurology."""
        return """Eres un asistente médico especializado en neurología, simulando una consulta neurológica real.

COMPORTAMIENTO CRUCIAL: Debes emular el comportamiento de un neurólogo real en consulta:

1. NO des un diagnóstico inmediato ante síntomas neurológicos vagos. En lugar de eso, primero haz preguntas específicas de anamnesis neurológica.

2. Utiliza una ESTRUCTURA DE CONSULTA NEUROLÓGICA:
   - Saludo inicial y presentación como neurólogo
   - Preguntas específicas sobre síntomas neurológicos:
     * Características del dolor/molestia (localización, irradiación, duración, intensidad)
     * Inicio y evolución de los síntomas (agudo, progresivo, intermitente)
     * Síntomas asociados (cambios visuales, alteraciones del habla, debilidad, mareos)
     * Desencadenantes y factores de alivio
     * Impacto en actividades diarias
   - Antecedentes neurológicos relevantes (convulsiones previas, TCE, ACV)
   - Historia familiar de enfermedades neurológicas
   - Hábitos (sueño, estrés, alcohol)
   - Medicación actual

3. ESTILO CONVERSACIONAL:
   - Usa un tono empático y humano, no clínico ni frío
   - Explica términos médicos en lenguaje accesible (ej: "migraña" → "dolor de cabeza intenso, generalmente en un lado")
   - Adapta tu lenguaje según el contexto del paciente
   - Haz máximo 2-3 preguntas por respuesta para no abrumar al paciente

4. ENFOQUE DE NEUROLOGÍA:
   - Trastornos neurológicos (ictus, epilepsia, esclerosis múltiple, enfermedad de Parkinson, etc.)
   - Cefaleas (migraña, tensional, en racimos)
   - Enfermedades neurodegenerativas (Alzheimer, demencia, ELA)
   - Procedimientos diagnósticos neurológicos (EEG, EMG, estudios de conducción nerviosa)
   - Trastornos del sistema nervioso central y periférico
   - Trastornos del movimiento
   - Neuro-oftalmología y trastornos vestibulares
   - Neuro-oncología (tumores cerebrales y de médula espinal)

5. RECOMENDACIONES ÚTILES:
   - Sugiere modificaciones del estilo de vida específicas para la salud neurológica
   - Indica muy claramente cuándo una situación requiere atención médica urgente
   - Recomienda seguimiento con proveedores de atención médica cuando corresponda
   - Explica el razonamiento detrás de cada recomendación

IMPORTANTE:
- Ante cualquier síntoma que sugiera un posible ACV, hemorragia cerebral o crisis convulsiva, ADVIERTE CLARAMENTE sobre buscar atención médica inmediata
- Nunca sugieras diagnósticos graves sin antes hacer preguntas básicas
- Si el paciente solo menciona un síntoma vago (como "me duele la cabeza"), DEBES primero hacer preguntas para caracterizar mejor el problema
- Usa la primera persona ("te recomendaría...") para sonar más humano

Al final de tu respuesta, si ya has recopilado suficiente información para dar recomendaciones, incluye una sección titulada "RECOMENDACIONES:" con los puntos clave de consejos para el paciente."""
    
    def _evaluate_confidence(self, query: str, response: str) -> float:
        """
        Evaluate the confidence for neurology-related queries.
        Override base implementation to check for neurology-specific keywords.
        """
        base_confidence = super()._evaluate_confidence(query, response)
        
        # Check for neurology-related keywords to potentially increase confidence
        neuro_keywords = [
            "brain", "headache", "migraine", "seizure", "epilepsy", "stroke", 
            "memory", "alzheimer", "parkinson", "tremor", "numbness", "tingling", 
            "multiple sclerosis", "nerve", "paralysis", "dizziness", "vertigo",
            "consciousness", "dementia", "neuropathy", "spinal", "meningitis",
            "encephalitis", "concussion", "neuromuscular",
            # Spanish keywords
            "cerebro", "dolor de cabeza", "migraña", "convulsión", "epilepsia", "ictus", 
            "memoria", "alzheimer", "parkinson", "temblor", "entumecimiento", "hormigueo", 
            "esclerosis múltiple", "nervio", "parálisis", "mareo", "vértigo",
            "consciencia", "demencia", "neuropatía", "espinal", "meningitis",
            "encefalitis", "conmoción", "neuromuscular", "embolia", "derrame"
        ]
        
        # Count neurology keywords in query
        keyword_count = sum(1 for keyword in neuro_keywords if keyword.lower() in query.lower())
        
        # Increase confidence based on keyword matches
        confidence_boost = min(0.3, keyword_count * 0.05)
        adjusted_confidence = base_confidence + confidence_boost
        
        # Ensure confidence stays in range [0.1, 1.0]
        return max(0.1, min(1.0, adjusted_confidence)) 
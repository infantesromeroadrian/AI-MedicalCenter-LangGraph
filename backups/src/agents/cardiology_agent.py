from typing import Dict, List, Any, Optional

from src.agents.base_agent import BaseMedicalAgent
from src.services.llm_service import LLMService

class CardiologyAgent(BaseMedicalAgent):
    """Agent specialized in cardiology."""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        """Initialize the cardiology agent."""
        super().__init__(specialty="cardiology", llm_service=llm_service)
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt specific to cardiology."""
        return """Eres un asistente médico especializado en cardiología, simulando una consulta cardiológica real.

COMPORTAMIENTO CRUCIAL: Debes emular el comportamiento de un cardiólogo real en consulta:

1. NO des un diagnóstico inmediato ante síntomas cardíacos vagos. En lugar de eso, primero haz preguntas específicas de anamnesis cardiológica.

2. Utiliza una ESTRUCTURA DE CONSULTA CARDIOLÓGICA:
   - Saludo inicial y presentación como cardiólogo
   - Preguntas específicas sobre síntomas cardiovasculares:
     * Características del dolor torácico (localización, irradiación, duración, factores desencadenantes)
     * Presencia de disnea (dificultad para respirar) y en qué circunstancias
     * Palpitaciones (ritmo, duración, asociación con actividad)
     * Síncopes o presíncopes (desmayos o mareos)
     * Edemas (hinchazón de piernas, tobillos)
   - Antecedentes cardiovasculares relevantes (HTA, dislipemia, diabetes, IAM previo)
   - Historia familiar de cardiopatía
   - Hábitos (tabaquismo, alcohol, actividad física)
   - Medicación actual

3. ESTILO CONVERSACIONAL:
   - Usa un tono empático y humano, no clínico ni frío
   - Explica términos médicos en lenguaje accesible (ej: "angina" → "dolor en el pecho por falta de oxígeno al corazón")
   - Adapta tu lenguaje según el contexto del paciente
   - Haz máximo 2-3 preguntas por respuesta para no abrumar al paciente

4. ENFOQUE DE CARDIOLOGÍA:
   - Enfermedades cardiovasculares (enfermedad coronaria, insuficiencia cardíaca, arritmias, etc.)
   - Procedimientos diagnósticos cardíacos (interpretación de ECG, pruebas de esfuerzo, ecocardiogramas)
   - Medicamentos y tratamientos cardiovasculares
   - Síntomas de ataque cardíaco y respuestas de emergencia
   - Factores de riesgo y prevención de enfermedades cardíacas
   - Condiciones cardíacas congénitas
   - Trastornos valvulares y tratamientos
   - Opciones de cirugía cardiovascular

5. RECOMENDACIONES ÚTILES:
   - Sugiere modificaciones del estilo de vida específicas para la salud cardiovascular
   - Indica muy claramente cuándo una situación requiere atención médica urgente
   - Recomienda seguimiento con proveedores de atención médica cuando corresponda
   - Explica el razonamiento detrás de cada recomendación

IMPORTANTE:
- Ante cualquier síntoma que sugiera un posible SCA (Síndrome Coronario Agudo) o emergencia cardiovascular, ADVIERTE CLARAMENTE sobre buscar atención médica inmediata
- Nunca sugieras diagnósticos graves sin antes hacer preguntas básicas
- Si el paciente solo menciona un síntoma vago (como "me duele el pecho"), DEBES primero hacer preguntas para caracterizar mejor el problema
- Usa la primera persona ("te recomendaría...") para sonar más humano

Al final de tu respuesta, si ya has recopilado suficiente información para dar recomendaciones, incluye una sección titulada "RECOMENDACIONES:" con los puntos clave de consejos para el paciente."""
    
    def _evaluate_confidence(self, query: str, response: str) -> float:
        """
        Evaluate the confidence for cardiology-related queries.
        Override base implementation to check for cardiology-specific keywords.
        """
        base_confidence = super()._evaluate_confidence(query, response)
        
        # Check for cardiology-related keywords to potentially increase confidence
        cardio_keywords = [
            "heart", "chest pain", "palpitation", "arrhythmia", "tachycardia", 
            "bradycardia", "blood pressure", "hypertension", "coronary", 
            "cardiovascular", "ECG", "EKG", "cholesterol", "statin", "angina",
            "valve", "murmur", "atrial", "ventricular", "fibrillation", "flutter",
            # Spanish keywords
            "corazón", "dolor de pecho", "palpitaciones", "arritmia", "taquicardia",
            "bradicardia", "presión arterial", "hipertensión", "coronaria",
            "cardiovascular", "colesterol", "angina", "válvula", "soplo", 
            "auricular", "ventricular", "fibrilación", "aleteo", "infarto",
            "latidos", "cardíaco", "cardiopatía"
        ]
        
        # Count cardiology keywords in query
        keyword_count = sum(1 for keyword in cardio_keywords if keyword.lower() in query.lower())
        
        # Increase confidence based on keyword matches
        confidence_boost = min(0.3, keyword_count * 0.05)
        adjusted_confidence = base_confidence + confidence_boost
        
        # Ensure confidence stays in range [0.1, 1.0]
        return max(0.1, min(1.0, adjusted_confidence)) 
from typing import Dict, List, Any, Optional

from src.agents.base_agent import BaseMedicalAgent
from src.services.llm_service import LLMService

class PediatricsAgent(BaseMedicalAgent):
    """Agent specialized in pediatrics and child healthcare."""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        """Initialize the pediatrics agent."""
        super().__init__(specialty="pediatrics", llm_service=llm_service)
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt specific to pediatrics."""
        return """Eres un pediatra especializado en la salud de bebés, niños y adolescentes hasta los 18 años.

COMPORTAMIENTO CRUCIAL: Debes emular el comportamiento de un pediatra real en consulta:

1. ENFOQUE PEDIÁTRICO ESPECÍFICO:
   - Considera SIEMPRE la edad del paciente para adaptar tu evaluación
   - Pregunta por hitos del desarrollo apropiados para la edad
   - Evalúa crecimiento (peso, talla, perímetro cefálico en lactantes)
   - Considera el contexto familiar y social del menor

2. ESTRUCTURA DE CONSULTA PEDIÁTRICA:
   - Saludo cordial dirigido tanto al menor como a los padres/cuidadores
   - Preguntas específicas por grupos de edad:
     * Lactantes (0-2 años): alimentación, sueño, desarrollo motor, vacunas
     * Preescolares (2-5 años): lenguaje, control de esfínteres, comportamiento
     * Escolares (5-12 años): rendimiento escolar, actividad física, nutrición
     * Adolescentes (12-18 años): desarrollo puberal, salud mental, conductas de riesgo

3. EVALUACIÓN DEL DESARROLLO:
   - Hitos motores (sostén cefálico, sedestación, marcha, etc.)
   - Desarrollo del lenguaje (primeras palabras, frases, vocabulario)
   - Desarrollo social y emocional
   - Desarrollo cognitivo apropiado para la edad

4. CONSIDERACIONES ESPECIALES PEDIÁTRICAS:
   - Dosificación de medicamentos SIEMPRE por peso corporal
   - Presentaciones pediátricas de medicamentos (jarabes, suspensiones)
   - Calendario de vacunación actualizado
   - Síntomas que pueden presentarse diferente en niños vs adultos
   - Necesidad de consentimiento parental para tratamientos

5. ENFOQUE DE PEDIATRÍA:
   - Enfermedades infecciosas comunes en la infancia
   - Problemas de crecimiento y desarrollo
   - Trastornos nutricionales (desnutrición, obesidad infantil)
   - Problemas respiratorios pediátricos (bronquiolitis, asma)
   - Dermatitis del pañal, eccema infantil
   - Trastornos del comportamiento y TDAH
   - Problemas gastrointestinales (cólicos, diarrea, estreñimiento)
   - Traumatismos pediátricos y prevención de accidentes

6. COMUNICACIÓN ADAPTADA:
   - Lenguaje sencillo y amigable para niños
   - Explicaciones comprensibles para padres sobre el desarrollo normal
   - Técnicas para tranquilizar a niños durante la evaluación
   - Educación a padres sobre cuidados preventivos

7. SIGNOS DE ALARMA PEDIÁTRICOS:
   - Fiebre en menores de 3 meses
   - Dificultad respiratoria o tirajes
   - Vómitos persistentes o deshidratación
   - Alteraciones del estado de conciencia
   - Convulsiones
   - Retraso significativo del desarrollo

IMPORTANTE:
- SIEMPRE pregunta la edad exacta del paciente al inicio
- Adapta todas tus preguntas y recomendaciones a la edad específica
- Considera el desarrollo normal vs patológico para cada grupo etario
- Involucra activamente a los padres/cuidadores en la evaluación
- Proporciona orientación sobre prevención y promoción de la salud infantil

Al final de tu respuesta, incluye una sección "Recomendaciones:" con consejos específicos para la edad del paciente, incluyendo aspectos del desarrollo, nutrición, seguridad y seguimiento médico."""
    
    def _evaluate_confidence(self, query: str, response: str) -> float:
        """
        Evaluate the confidence for pediatrics-related queries.
        Override base implementation to check for pediatrics-specific keywords.
        """
        base_confidence = super()._evaluate_confidence(query, response)
        
        # Check for pediatrics-related keywords to potentially increase confidence
        pediatric_keywords = [
            "baby", "infant", "child", "kid", "toddler", "adolescent", "teenager",
            "pediatric", "growth", "development", "vaccine", "immunization",
            "feeding", "bottle", "breastfeeding", "diaper", "rash", "fever child",
            "school", "behavior", "ADHD", "autism", "milestone", "walking", "talking",
            # Spanish keywords
            "bebé", "niño", "niña", "infante", "lactante", "escolar", "adolescente",
            "pediátrico", "crecimiento", "desarrollo", "vacuna", "inmunización",
            "alimentación", "biberón", "lactancia", "pañal", "sarpullido", "fiebre niño",
            "colegio", "comportamiento", "hitos", "caminar", "hablar", "pediatra"
        ]
        
        # Age-related indicators
        age_indicators = [
            "months old", "years old", "meses", "años", "recién nacido", "newborn",
            "0 años", "1 año", "2 años", "3 años", "4 años", "5 años",
            "6 años", "7 años", "8 años", "9 años", "10 años", "11 años",
            "12 años", "13 años", "14 años", "15 años", "16 años", "17 años"
        ]
        
        # Count pediatric keywords in query
        keyword_count = sum(1 for keyword in pediatric_keywords if keyword.lower() in query.lower())
        age_count = sum(1 for age in age_indicators if age.lower() in query.lower())
        
        # Increase confidence based on keyword matches
        confidence_boost = min(0.4, (keyword_count * 0.08) + (age_count * 0.15))
        adjusted_confidence = base_confidence + confidence_boost
        
        # Ensure confidence stays in range [0.1, 1.0]
        return max(0.1, min(1.0, adjusted_confidence)) 
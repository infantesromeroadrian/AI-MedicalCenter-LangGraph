from typing import Dict, List, Any, Optional

from src.agents.base_agent import BaseMedicalAgent
from src.services.llm_service import LLMService

class PsychiatryAgent(BaseMedicalAgent):
    """Agent specialized in psychiatry and mental health."""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        """Initialize the psychiatry agent."""
        super().__init__(specialty="psychiatry", llm_service=llm_service)
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt specific to psychiatry."""
        return """Eres un psiquiatra especializado en salud mental y trastornos psiquiátricos.

COMPORTAMIENTO CRUCIAL: Debes emular el comportamiento de un psiquiatra real en consulta:

1. ENFOQUE PSIQUIÁTRICO EMPÁTICO:
   - Establece un ambiente de confianza y no juzgamiento
   - Utiliza escucha activa y validación emocional
   - Respeta la autonomía y dignidad del paciente
   - Mantén confidencialidad y privacidad

2. ESTRUCTURA DE CONSULTA PSIQUIÁTRICA:
   - Saludo empático y establecimiento de rapport
   - Evaluación del estado mental actual:
     * Apariencia y comportamiento
     * Estado de ánimo y afecto
     * Percepción y contenido del pensamiento
     * Cognición y orientación
     * Insight y juicio
   - Historia psiquiátrica personal y familiar
   - Factores psicosociales y estresores actuales
   - Funcionamiento laboral, social y personal

3. EVALUACIÓN DE TRASTORNOS MENTALES:
   - Trastornos del estado de ánimo: depresión mayor, trastorno bipolar, distimia
   - Trastornos de ansiedad: ansiedad generalizada, pánico, fobias, TOC, TEPT
   - Trastornos psicóticos: esquizofrenia, trastorno delirante, episodios psicóticos
   - Trastornos neurocognitivos: demencias, deterioro cognitivo leve
   - Trastornos de la personalidad: borderline, antisocial, narcisista
   - Trastornos por uso de sustancias: alcohol, drogas, dependencia

4. EVALUACIÓN DE RIESGO:
   - Riesgo suicida: ideación, planificación, intentos previos, factores protectores
   - Riesgo de autolesión no suicida
   - Riesgo de heteroagresión
   - Capacidad de autocuidado y funcionamiento
   - Necesidad de hospitalización o intervención de crisis

5. TRATAMIENTOS PSICOFARMACOLÓGICOS:
   - Antidepresivos: ISRS, IRSN, tricíclicos, IMAO
   - Ansiolíticos: benzodiazepinas, buspirona, pregabalina
   - Antipsicóticos: típicos, atípicos, efectos secundarios
   - Estabilizadores del ánimo: litio, anticonvulsivantes
   - Hipnóticos y sedantes para trastornos del sueño
   - Consideraciones de dosificación, interacciones y efectos adversos

6. PSICOTERAPIAS Y ENFOQUES NO FARMACOLÓGICOS:
   - Terapia cognitivo-conductual (TCC)
   - Terapia dialéctica conductual (TDC)
   - Terapia de aceptación y compromiso (TAC)
   - EMDR para trauma
   - Terapia interpersonal
   - Mindfulness y técnicas de relajación

7. FACTORES PSICOSOCIALES:
   - Relaciones familiares y de pareja
   - Situación laboral y económica
   - Traumas y eventos vitales estresantes
   - Apoyo social y redes de contención
   - Factores culturales y espirituales

8. COMUNICACIÓN TERAPÉUTICA:
   - Evita tecnicismos innecesarios
   - Explica diagnósticos de manera comprensible
   - Aborda estigma y mitos sobre salud mental
   - Fomenta adherencia al tratamiento
   - Proporciona esperanza realista

IMPORTANTE:
- SIEMPRE evalúa riesgo suicida en pacientes con síntomas depresivos
- No minimices los síntomas o experiencias del paciente
- Considera factores biológicos, psicológicos y sociales
- Deriva a emergencias si hay riesgo inmediato
- Enfatiza que los trastornos mentales son condiciones médicas tratables

Al final de tu respuesta, incluye una sección "RECOMENDACIONES PSIQUIÁTRICAS:" con consejos sobre manejo de síntomas, técnicas de afrontamiento, adherencia al tratamiento y cuándo buscar ayuda de emergencia."""
    
    def _evaluate_confidence(self, query: str, response: str) -> float:
        """
        Evaluate the confidence for psychiatry-related queries.
        Override base implementation to check for psychiatry-specific keywords.
        """
        base_confidence = super()._evaluate_confidence(query, response)
        
        # Check for psychiatry-related keywords to potentially increase confidence
        psychiatry_keywords = [
            "mental health", "depression", "anxiety", "bipolar", "schizophrenia",
            "psychiatry", "psychiatric", "psychotherapy", "counseling", "therapy",
            "mood", "panic", "OCD", "PTSD", "trauma", "stress", "insomnia",
            "medication", "antidepressant", "anxiolytic", "antipsychotic",
            # Spanish keywords
            "salud mental", "depresión", "ansiedad", "bipolar", "esquizofrenia",
            "psiquiatría", "psiquiátrico", "psicoterapia", "terapia", "consejería",
            "estado de ánimo", "pánico", "TOC", "TEPT", "trauma", "estrés", "insomnio",
            "medicamento", "antidepresivo", "ansiolítico", "antipsicótico", "psiquiatra"
        ]
        
        # Mental health conditions
        mental_conditions = [
            "major depression", "bipolar disorder", "generalized anxiety", "panic disorder",
            "social anxiety", "specific phobia", "obsessive compulsive", "post traumatic stress",
            "borderline personality", "narcissistic personality", "antisocial personality",
            "attention deficit", "hyperactivity", "autism spectrum", "eating disorder",
            # Spanish mental health conditions
            "depresión mayor", "trastorno bipolar", "ansiedad generalizada", "trastorno de pánico",
            "ansiedad social", "fobia específica", "obsesivo compulsivo", "estrés postraumático",
            "personalidad límite", "personalidad narcisista", "personalidad antisocial",
            "déficit de atención", "hiperactividad", "espectro autista", "trastorno alimentario"
        ]
        
        # Psychiatric symptoms
        psychiatric_symptoms = [
            "sadness", "hopelessness", "worthlessness", "guilt", "suicidal thoughts",
            "racing thoughts", "hallucinations", "delusions", "paranoia", "euphoria",
            "irritability", "mood swings", "panic attacks", "flashbacks", "nightmares",
            "concentration problems", "memory issues", "sleep problems", "appetite changes",
            # Spanish psychiatric symptoms
            "tristeza", "desesperanza", "inutilidad", "culpa", "pensamientos suicidas",
            "pensamientos acelerados", "alucinaciones", "delirios", "paranoia", "euforia",
            "irritabilidad", "cambios de humor", "ataques de pánico", "flashbacks", "pesadillas",
            "problemas de concentración", "problemas de memoria", "problemas de sueño", "cambios de apetito"
        ]
        
        # Count psychiatry keywords in query
        keyword_count = sum(1 for keyword in psychiatry_keywords if keyword.lower() in query.lower())
        condition_count = sum(1 for condition in mental_conditions if condition.lower() in query.lower())
        symptom_count = sum(1 for symptom in psychiatric_symptoms if symptom.lower() in query.lower())
        
        # Increase confidence based on keyword matches
        confidence_boost = min(0.5, (keyword_count * 0.1) + (condition_count * 0.15) + (symptom_count * 0.08))
        adjusted_confidence = base_confidence + confidence_boost
        
        # Ensure confidence stays in range [0.1, 1.0]
        return max(0.1, min(1.0, adjusted_confidence))

    def _validate_medical_query(self, query: str) -> Dict[str, Any]:
        """
        Validar que la consulta sea apropiada para consulta psicológica.
        Sobrescribe la validación médica estricta para ser más flexible.
        """
        
        # Validaciones básicas
        if len(query.strip()) < 3:
            return {"is_valid": False, "reason": "Consulta demasiado corta"}
        
        if len(query.strip()) > 2000:
            return {"is_valid": False, "reason": "Consulta demasiado larga"}
        
        # Validar contenido psicológico/emocional (más flexible que médico)
        psychological_keywords = [
            # Emociones y estados mentales
            "siento", "me siento", "estoy", "me encuentro", "emoción", "emocional",
            "triste", "tristeza", "deprimido", "depresión", "ansiedad", "ansioso",
            "preocupado", "preocupación", "miedo", "temor", "ira", "enojo", "rabia",
            "feliz", "alegría", "confundido", "confusión", "perdido",
            
            # Situaciones psicológicas
            "estrés", "estresado", "agobio", "agobiado", "abrumado", "burnout",
            "relación", "pareja", "familia", "trabajo", "laboral", "social",
            "soledad", "solo", "aislado", "aislamiento",
            
            # Comportamientos y hábitos
            "duermo", "sueño", "insomnio", "apetito", "como", "hábito", "rutina",
            "motivación", "energía", "concentración", "memoria", "pensamientos",
            
            # Experiencias de vida
            "vida", "vivir", "muerte", "pérdida", "duelo", "cambio", "transición",
            "pandemia", "covid", "confinamiento", "cuarentena", "zona de confort",
            "casa", "salir", "sociabilizar", "gente", "personas",
            
            # Saludos y apertura emocional
            "hola", "buenas", "ayuda", "necesito", "quiero", "me pasa", "me ocurre",
            "desde", "hace", "tiempo", "últimamente", "recientemente",
            
            # English equivalents
            "feel", "feeling", "emotion", "sad", "depression", "anxiety", "worried",
            "stress", "relationship", "family", "work", "sleep", "tired", "lonely",
            "help", "need", "want", "life", "living", "since", "lately", "recently",
            "pandemic", "home", "comfort zone", "social", "people"
        ]
        
        # Verificar si contiene contenido psicológico
        has_psychological_content = any(keyword in query.lower() for keyword in psychological_keywords)
        
        # Para consultas psicológicas, también aceptamos saludos y contexto general
        is_greeting_with_context = (
            any(greeting in query.lower() for greeting in ["hola", "buenas", "hello", "hi"]) and
            len(query.split()) > 1  # Más de una palabra
        )
        
        # Verificar si menciona situaciones de vida relevantes
        life_situations = [
            "pandemia", "covid", "cuarentena", "confinamiento", "casa", "hogar",
            "trabajo", "pareja", "familia", "amigos", "social", "gente",
            "zona de confort", "salir", "actividades", "rutina", "hábitos"
        ]
        has_life_context = any(situation in query.lower() for situation in life_situations)
        
        if has_psychological_content or is_greeting_with_context or has_life_context:
            return {"is_valid": True, "reason": "Consulta psicológica válida"}
        
        # Si no encuentra contenido relevante, dar una sugerencia más específica
        return {
            "is_valid": False, 
            "reason": "Para una consulta psicológica, puedes compartir cómo te sientes, qué te preocupa, o alguna situación que quieras conversar"
        } 

    def _create_validation_error_response(self, validation_result: Dict[str, Any]):
        """Crear respuesta de error de validación más empática para consulta psicológica."""
        
        # Import here to avoid circular imports
        from src.agents.base_agent import AgentResponse
        
        reason = validation_result['reason']
        
        if "demasiado corta" in reason:
            error_message = (
                "Hola, me da mucho gusto que estés aquí. Veo que has escrito algo breve. "
                "Este es tu espacio seguro para compartir. ¿Te gustaría contarme un poco más "
                "sobre cómo te sientes o qué te trae por aquí hoy?"
            )
        elif "demasiado larga" in reason:
            error_message = (
                "Veo que tienes mucho que compartir, y eso está muy bien. Para poder ayudarte mejor, "
                "¿podrías resumir lo principal que te preocupa o te gustaría conversar hoy? "
                "Podemos ir profundizando paso a paso."
            )
        else:
            error_message = (
                "Entiendo que tal vez no sepas por dónde empezar, y eso es completamente normal. "
                "Este es un espacio donde puedes compartir cualquier cosa que sientes, te preocupa "
                "o simplemente quieres conversar. No hay respuestas correctas o incorrectas. "
                "¿Cómo has estado últimamente?"
            )
        
        return AgentResponse(
            specialty=self.specialty,
            response=error_message,
            confidence=0.9,  # Alta confianza en la respuesta empática
            recommendations=[
                "Comparte cualquier emoción o sentimiento que tengas", 
                "Puedes hablar sobre situaciones que te preocupan",
                "No hay tema demasiado pequeño o grande para conversar"
            ],
            sources=None
        ) 
from typing import Dict, List, Any, Optional

from src.agents.base_agent import BaseMedicalAgent
from src.services.llm_service import LLMService

class EmergencyMedicineAgent(BaseMedicalAgent):
    """Agent specialized in emergency medicine and urgent care."""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        """Initialize the emergency medicine agent."""
        super().__init__(specialty="emergency_medicine", llm_service=llm_service)
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt specific to emergency medicine."""
        return """Eres un médico de emergencias especializado en atención médica urgente y crítica.

COMPORTAMIENTO CRUCIAL: Debes emular el comportamiento de un médico de emergencias en urgencias:

1. ENFOQUE DE MEDICINA DE EMERGENCIA:
   - Evaluación rápida y sistemática ABCDE (vía aérea, respiración, circulación, discapacidad, exposición)
   - Priorización según gravedad y riesgo vital inmediato
   - Toma de decisiones rápidas con información limitada
   - Estabilización antes que diagnóstico definitivo

2. TRIAJE Y EVALUACIÓN INICIAL:
   - Triaje Manchester o similar para clasificar urgencia
   - Signos vitales: presión arterial, frecuencia cardíaca, frecuencia respiratoria, temperatura, saturación O2
   - Nivel de conciencia: Escala de Glasgow, AVDN
   - Evaluación primaria para amenazas vitales inmediatas

3. EMERGENCIAS CARDIOVASCULARES:
   - Síndrome coronario agudo: STEMI, NSTEMI, angina inestable
   - Paro cardiorrespiratorio: RCP, desfibrilación, ACLS
   - Edema pulmonar agudo
   - Shock cardiogénico
   - Arritmias con compromiso hemodinámico
   - Disección aórtica

4. EMERGENCIAS RESPIRATORIAS:
   - Insuficiencia respiratoria aguda
   - Crisis asmática severa
   - Neumotórax a tensión
   - Embolia pulmonar
   - Aspiración de cuerpo extraño
   - Edema laríngeo

5. EMERGENCIAS NEUROLÓGICAS:
   - Accidente cerebrovascular (ACV): código ictus
   - Estado epiléptico
   - Trauma craneoencefálico
   - Hipertensión intracraneal
   - Coma de origen desconocido
   - Meningitis aguda

6. TRAUMA Y LESIONES:
   - Evaluación ATLS (Advanced Trauma Life Support)
   - Trauma mayor: politraumatizado
   - Traumatismo craneoencefálico severo
   - Trauma torácico: neumotórax, hemotórax
   - Trauma abdominal: hemoperitoneo
   - Fracturas complejas y luxaciones

7. EMERGENCIAS METABÓLICAS:
   - Cetoacidosis diabética
   - Coma hiperosmolar
   - Hipoglucemia severa
   - Intoxicaciones agudas
   - Desequilibrios electrolíticos graves
   - Insuficiencia suprarrenal aguda

8. SHOCK Y ESTADOS CRÍTICOS:
   - Shock hipovolémico, cardiogénico, distributivo, obstructivo
   - Sepsis y shock séptico
   - Anafilaxia
   - Síndrome de respuesta inflamatoria sistémica
   - Falla orgánica múltiple

9. PROCEDIMIENTOS DE EMERGENCIA:
   - Intubación orotraqueal
   - Acceso vascular: venoso periférico, central, intraóseo
   - Desfibrilación y cardioversión
   - Toracostomía de emergencia
   - Cricotiroidotomía
   - Punción lumbar

10. MANEJO DEL DOLOR Y SEDACIÓN:
    - Analgesia multimodal en urgencias
    - Sedación procedural
    - Control del dolor en politraumatizado
    - Manejo de agitación psicomotriz

PROTOCOLOS DE ACTUACIÓN:
- SIEMPRE evalúa ABC (vía aérea, respiración, circulación) primero
- Identifica amenazas vitales inmediatas
- Prioriza estabilización sobre diagnóstico
- Considera activación de códigos de emergencia (código azul, código rojo, etc.)
- Evalúa necesidad de UCI o quirófano

COMUNICACIÓN EN EMERGENCIAS:
- Información clara y directa a pacientes y familiares
- Explicación de la gravedad de forma comprensible
- Coordinación con otros servicios: UCI, quirófano, especialistas
- Documentación concisa pero completa

IMPORTANTE:
- CUALQUIER síntoma que sugiera amenaza vital requiere atención inmediata
- No demores tratamientos vitales por estudios complementarios
- Mantén alta sospecha de condiciones que imitan otras patologías
- Considera siempre los diagnósticos diferenciales más graves primero
- Si hay duda sobre la gravedad, siempre err del lado de la precaución

Al final de tu respuesta, incluye una sección "RECOMENDACIONES DE EMERGENCIA:" con indicaciones claras sobre cuándo buscar atención inmediata, qué hacer mientras llega ayuda médica, y signos de alarma a vigilar."""
    
    def _evaluate_confidence(self, query: str, response: str) -> float:
        """
        Evaluate the confidence for emergency medicine-related queries.
        Override base implementation to check for emergency-specific keywords.
        """
        base_confidence = super()._evaluate_confidence(query, response)
        
        # Check for emergency medicine-related keywords
        emergency_keywords = [
            "emergency", "urgent", "critical", "severe", "acute", "sudden",
            "emergency room", "ER", "ambulance", "911", "first aid", "trauma",
            "cardiac arrest", "stroke", "heart attack", "seizure", "unconscious",
            # Spanish keywords
            "emergencia", "urgente", "crítico", "severo", "agudo", "súbito",
            "sala de emergencias", "ambulancia", "primeros auxilios", "trauma",
            "paro cardíaco", "derrame", "infarto", "ataque cardíaco", "convulsión", "inconsciente"
        ]
        
        # Emergency conditions
        emergency_conditions = [
            "myocardial infarction", "cardiac arrest", "stroke", "seizure", "anaphylaxis",
            "respiratory failure", "shock", "trauma", "poisoning", "overdose",
            "acute abdomen", "appendicitis", "intestinal obstruction", "GI bleeding",
            "pulmonary embolism", "pneumothorax", "asthma attack", "COPD exacerbation",
            # Spanish emergency conditions
            "infarto de miocardio", "paro cardíaco", "derrame cerebral", "convulsiones", "anafilaxia",
            "insuficiencia respiratoria", "shock", "trauma", "intoxicación", "sobredosis",
            "abdomen agudo", "apendicitis", "obstrucción intestinal", "sangrado digestivo",
            "embolia pulmonar", "neumotórax", "crisis asmática", "exacerbación EPOC"
        ]
        
        # Emergency symptoms
        emergency_symptoms = [
            "chest pain", "difficulty breathing", "loss of consciousness", "severe headache",
            "severe abdominal pain", "high fever", "profuse bleeding", "severe burns",
            "neck stiffness", "confusion", "slurred speech", "weakness", "paralysis",
            # Spanish emergency symptoms
            "dolor de pecho", "dificultad para respirar", "pérdida de conocimiento", "dolor de cabeza severo",
            "dolor abdominal severo", "fiebre alta", "sangrado profuso", "quemaduras severas",
            "rigidez de cuello", "confusión", "habla arrastrada", "debilidad", "parálisis"
        ]
        
        # Count emergency keywords in query
        keyword_count = sum(1 for keyword in emergency_keywords if keyword.lower() in query.lower())
        condition_count = sum(1 for condition in emergency_conditions if condition.lower() in query.lower())
        symptom_count = sum(1 for symptom in emergency_symptoms if symptom.lower() in query.lower())
        
        # Emergency medicine gets higher confidence boost due to urgency
        confidence_boost = min(0.6, (keyword_count * 0.15) + (condition_count * 0.2) + (symptom_count * 0.1))
        adjusted_confidence = base_confidence + confidence_boost
        
        # Ensure confidence stays in range [0.1, 1.0]
        return max(0.1, min(1.0, adjusted_confidence)) 
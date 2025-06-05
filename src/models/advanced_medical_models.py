"""
Advanced Medical Models with Structured Outputs for LangGraph
"""
from typing import Annotated, TypedDict, Literal, List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from src.models.data_models import UserQuery, AgentResponse, ConsensusResponse

# 1. Router Médico Avanzado
class MedicalRouterOutput(BaseModel):
    """Structured output para el router médico inteligente"""
    primary_specialty: Literal[
        "cardiology", "neurology", "oncology", "pediatrics", 
        "psychiatry", "dermatology", "internal_medicine", "emergency_medicine"
    ] = Field(description="Especialidad médica principal determinada")
    
    secondary_specialties: List[str] = Field(
        description="Especialidades médicas secundarias que podrían ser relevantes",
        max_items=3
    )
    
    urgency_level: Literal["low", "medium", "high", "critical"] = Field(
        description="Nivel de urgencia médica identificado"
    )
    
    confidence: float = Field(
        description="Nivel de confianza en la clasificación (0.0-1.0)",
        ge=0.0, le=1.0
    )
    
    medical_keywords: List[str] = Field(
        description="Palabras clave médicas identificadas",
        max_items=8
    )
    
    suspected_conditions: List[str] = Field(
        description="Condiciones médicas sospechadas basadas en síntomas",
        max_items=5
    )
    
    requires_emergency: bool = Field(
        description="¿Requiere atención médica de emergencia inmediata?"
    )

# 2. Evaluador Médico Crítico
class MedicalEvaluatorOutput(BaseModel):
    """Structured output para el evaluador médico crítico"""
    clinical_accuracy: int = Field(
        description="Precisión clínica de la respuesta (1-10)",
        ge=1, le=10
    )
    
    safety_score: int = Field(
        description="Puntuación de seguridad médica (1-10)",
        ge=1, le=10
    )
    
    completeness: bool = Field(
        description="¿La respuesta aborda todos los aspectos clínicos relevantes?"
    )
    
    appropriate_recommendations: bool = Field(
        description="¿Las recomendaciones son médicamente apropiadas?"
    )
    
    patient_safety: bool = Field(
        description="¿La respuesta prioriza la seguridad del paciente?"
    )
    
    ethical_compliance: bool = Field(
        description="¿Cumple con estándares éticos médicos?"
    )
    
    needs_specialist_referral: bool = Field(
        description="¿Se necesita derivación a especialista?"
    )
    
    needs_improvement: bool = Field(
        description="¿La respuesta médica necesita mejoras?"
    )
    
    improvement_suggestions: str = Field(
        description="Sugerencias específicas para mejorar la respuesta médica"
    )
    
    safety_warnings: str = Field(
        description="Advertencias de seguridad que deben incluirse"
    )
    
    clinical_feedback: str = Field(
        description="Feedback clínico constructivo para el agente médico"
    )

# 3. Criterios de Satisfacción Médica
class MedicalSatisfactionOutput(BaseModel):
    """Criterios de satisfacción específicos para consultas médicas"""
    medical_criteria_met: bool = Field(
        description="¿Se cumplieron todos los criterios médicos?"
    )
    
    patient_concerns_addressed: bool = Field(
        description="¿Se atendieron todas las preocupaciones del paciente?"
    )
    
    appropriate_detail_level: bool = Field(
        description="¿El nivel de detalle es apropiado para el paciente?"
    )
    
    actionable_guidance: bool = Field(
        description="¿Se proporcionó orientación práctica y accionable?"
    )
    
    next_medical_action: Literal[
        "complete", "improve_response", "seek_emergency", 
        "specialist_referral", "additional_tests", "follow_up"
    ] = Field(description="Acción médica recomendada siguiente")
    
    confidence_level: float = Field(
        description="Nivel de confianza en la evaluación médica (0.0-1.0)",
        ge=0.0, le=1.0
    )
    
    requires_human_physician: bool = Field(
        description="¿Se requiere consulta con médico humano?"
    )

# 4. Estado Avanzado del Sistema Médico
class AdvancedMedicalState(TypedDict):
    # Información básica de la consulta
    user_query: UserQuery
    messages: List[Any]
    
    # Información del routing médico
    primary_specialty: str
    secondary_specialties: List[str]
    urgency_level: str
    medical_keywords: List[str]
    suspected_conditions: List[str]
    requires_emergency: bool
    router_confidence: float
    
    # Respuestas de agentes especializados
    agent_responses: Dict[str, AgentResponse]
    current_response: str
    active_agent: str
    
    # Sistema de evaluación médica
    clinical_accuracy: int
    safety_score: int
    patient_safety: bool
    ethical_compliance: bool
    needs_improvement: bool
    improvement_suggestions: str
    safety_warnings: str
    clinical_feedback: str
    
    # Criterios de satisfacción médica
    medical_criteria: str  # Criterios específicos para la consulta
    medical_criteria_met: bool
    patient_concerns_addressed: bool
    next_medical_action: str
    requires_human_physician: bool
    
    # Control de flujo y feedback loops
    attempt_count: int
    max_attempts: int
    is_complete: bool
    needs_specialist_referral: bool
    
    # Contexto médico y aprendizaje
    medical_history: List[Dict[str, Any]]
    clinical_context: Dict[str, Any]
    interaction_metrics: Dict[str, Any]
    
    # Consenso final
    consensus_response: Optional[ConsensusResponse]

# 5. Métricas de Calidad Médica
class MedicalQualityMetrics(BaseModel):
    """Métricas específicas para evaluar calidad médica"""
    diagnostic_accuracy: float = Field(ge=0.0, le=1.0)
    treatment_appropriateness: float = Field(ge=0.0, le=1.0)
    patient_safety_score: float = Field(ge=0.0, le=1.0)
    evidence_based: bool
    ethical_compliance: bool
    communication_clarity: float = Field(ge=0.0, le=1.0)
    time_to_resolution: int  # en segundos
    patient_satisfaction_predicted: float = Field(ge=0.0, le=1.0)

# 6. Contexto Clínico Avanzado
class ClinicalContext(BaseModel):
    """Contexto clínico estructurado para mejores decisiones"""
    patient_demographics: Optional[Dict[str, Any]] = None
    presenting_symptoms: List[str] = []
    symptom_duration: Optional[str] = None
    severity_level: Optional[int] = Field(None, ge=1, le=10)
    previous_medical_history: List[str] = []
    current_medications: List[str] = []
    allergies: List[str] = []
    risk_factors: List[str] = []
    red_flags: List[str] = []  # Señales de alarma médica

# 7. Recomendaciones Médicas Estructuradas
class MedicalRecommendations(BaseModel):
    """Recomendaciones médicas estructuradas y priorizadas"""
    immediate_actions: List[str] = Field(
        description="Acciones que debe tomar inmediatamente"
    )
    short_term_recommendations: List[str] = Field(
        description="Recomendaciones a corto plazo (días)"
    )
    long_term_recommendations: List[str] = Field(
        description="Recomendaciones a largo plazo (semanas/meses)"
    )
    warning_signs: List[str] = Field(
        description="Señales de alarma que requieren atención inmediata"
    )
    follow_up_timeline: str = Field(
        description="Cronograma recomendado para seguimiento"
    )
    specialist_referrals: List[str] = Field(
        description="Especialistas a los que se debe derivar"
    )
    lifestyle_modifications: List[str] = Field(
        description="Modificaciones del estilo de vida recomendadas"
    ) 
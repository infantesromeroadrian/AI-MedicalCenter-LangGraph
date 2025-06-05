"""
Modelos de datos avanzados para análisis psicológico completo.
Soporta evaluaciones, seguimiento longitudinal y análisis de personalidad.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import json


class AttachmentStyle(Enum):
    """Estilos de apego según la teoría del apego."""
    SECURE = "secure"
    ANXIOUS_PREOCCUPIED = "anxious_preoccupied"
    DISMISSIVE_AVOIDANT = "dismissive_avoidant"
    FEARFUL_AVOIDANT = "fearful_avoidant"
    UNKNOWN = "unknown"


class DefenseMechanism(Enum):
    """Mecanismos de defensa psicológicos."""
    DENIAL = "denial"
    PROJECTION = "projection"
    RATIONALIZATION = "rationalization"
    DISPLACEMENT = "displacement"
    REGRESSION = "regression"
    SUBLIMATION = "sublimation"
    REACTION_FORMATION = "reaction_formation"
    SUPPRESSION = "suppression"
    INTELLECTUALIZATION = "intellectualization"
    HUMOR = "humor"


class EmotionCategory(Enum):
    """Categorías emocionales expandidas."""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    SURPRISE = "surprise"
    DISGUST = "disgust"
    ANXIETY = "anxiety"
    EXCITEMENT = "excitement"
    CONTENTMENT = "contentment"
    CONFUSION = "confusion"
    AMBIVALENCE = "ambivalence"


@dataclass
class BigFiveProfile:
    """Perfil de personalidad Big Five (OCEAN)."""
    openness: float = 0.0  # 0-100 scale
    conscientiousness: float = 0.0
    extraversion: float = 0.0
    agreeableness: float = 0.0
    neuroticism: float = 0.0
    confidence_level: float = 0.0
    analysis_date: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            'openness': self.openness,
            'conscientiousness': self.conscientiousness,
            'extraversion': self.extraversion,
            'agreeableness': self.agreeableness,
            'neuroticism': self.neuroticism,
            'confidence_level': self.confidence_level,
            'analysis_date': self.analysis_date.isoformat()
        }


@dataclass
class PsychologicalAssessment:
    """Evaluación psicológica con puntuaciones estándar."""
    assessment_id: str
    session_id: str
    assessment_type: str  # PHQ-9, GAD-7, Beck, etc.
    raw_responses: Dict[str, Any]
    total_score: float
    severity_level: str  # minimal, mild, moderate, severe
    subscale_scores: Dict[str, float] = field(default_factory=dict)
    percentile: float = 0.0
    clinical_cutoff: float = 0.0
    assessment_date: datetime = field(default_factory=datetime.now)
    notes: str = ""
    
    def to_dict(self) -> dict:
        return {
            'assessment_id': self.assessment_id,
            'session_id': self.session_id,
            'assessment_type': self.assessment_type,
            'raw_responses': self.raw_responses,
            'total_score': self.total_score,
            'severity_level': self.severity_level,
            'subscale_scores': self.subscale_scores,
            'percentile': self.percentile,
            'clinical_cutoff': self.clinical_cutoff,
            'assessment_date': self.assessment_date.isoformat(),
            'notes': self.notes
        }


@dataclass
class EmotionalState:
    """Estado emocional multi-dimensional en un momento específico."""
    timestamp: datetime
    primary_emotion: EmotionCategory
    secondary_emotions: List[EmotionCategory] = field(default_factory=list)
    intensity: float = 0.0  # 0-100 scale
    valence: float = 0.0  # -100 to +100 (negative to positive)
    arousal: float = 0.0  # 0-100 (calm to excited)
    mixed_emotions: bool = False
    contradictory_emotions: List[str] = field(default_factory=list)
    confidence: float = 0.0
    triggers: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'primary_emotion': self.primary_emotion.value,
            'secondary_emotions': [e.value for e in self.secondary_emotions],
            'intensity': self.intensity,
            'valence': self.valence,
            'arousal': self.arousal,
            'mixed_emotions': self.mixed_emotions,
            'contradictory_emotions': self.contradictory_emotions,
            'confidence': self.confidence,
            'triggers': self.triggers
        }


@dataclass
class PersonalityInsight:
    """Insight de personalidad específico."""
    insight_type: str  # "big_five", "attachment", "defense_mechanism"
    content: str
    confidence: float
    supporting_evidence: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            'insight_type': self.insight_type,
            'content': self.content,
            'confidence': self.confidence,
            'supporting_evidence': self.supporting_evidence,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class MindfulnessSession:
    """Sesión de mindfulness y técnicas de relajación."""
    session_id: str
    technique_type: str  # "breathing", "meditation", "grounding"
    duration_minutes: int
    difficulty_level: str  # "beginner", "intermediate", "advanced"
    emotional_state_before: EmotionalState
    emotional_state_after: Optional[EmotionalState] = None
    completion_rate: float = 0.0  # 0-100%
    user_rating: Optional[int] = None  # 1-5 stars
    notes: str = ""
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        return {
            'session_id': self.session_id,
            'technique_type': self.technique_type,
            'duration_minutes': self.duration_minutes,
            'difficulty_level': self.difficulty_level,
            'emotional_state_before': self.emotional_state_before.to_dict(),
            'emotional_state_after': self.emotional_state_after.to_dict() if self.emotional_state_after else None,
            'completion_rate': self.completion_rate,
            'user_rating': self.user_rating,
            'notes': self.notes,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


@dataclass
class LongitudinalDataPoint:
    """Punto de datos para seguimiento longitudinal."""
    timestamp: datetime
    metric_type: str  # "mood", "anxiety", "depression", "stress"
    value: float
    context: str = ""
    source: str = ""  # "session", "daily_checkin", "assessment"
    
    def to_dict(self) -> dict:
        return {
            'timestamp': self.timestamp.isoformat(),
            'metric_type': self.metric_type,
            'value': self.value,
            'context': self.context,
            'source': self.source
        }


@dataclass
class TemporalPattern:
    """Patrón temporal identificado en los datos."""
    pattern_type: str  # "daily", "weekly", "monthly", "seasonal"
    metric: str
    pattern_description: str
    confidence: float
    peak_times: List[str] = field(default_factory=list)
    low_times: List[str] = field(default_factory=list)
    trend_direction: str = "stable"  # "improving", "declining", "stable"
    statistical_significance: float = 0.0
    identified_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            'pattern_type': self.pattern_type,
            'metric': self.metric,
            'pattern_description': self.pattern_description,
            'confidence': self.confidence,
            'peak_times': self.peak_times,
            'low_times': self.low_times,
            'trend_direction': self.trend_direction,
            'statistical_significance': self.statistical_significance,
            'identified_at': self.identified_at.isoformat()
        }


@dataclass
class CrisisRiskAssessment:
    """Evaluación de riesgo de crisis."""
    assessment_id: str
    session_id: str
    risk_level: str  # "low", "moderate", "high", "critical"
    risk_score: float  # 0-100
    risk_factors: List[str] = field(default_factory=list)
    protective_factors: List[str] = field(default_factory=list)
    immediate_actions: List[str] = field(default_factory=list)
    confidence: float = 0.0
    model_version: str = "1.0"
    assessed_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            'assessment_id': self.assessment_id,
            'session_id': self.session_id,
            'risk_level': self.risk_level,
            'risk_score': self.risk_score,
            'risk_factors': self.risk_factors,
            'protective_factors': self.protective_factors,
            'immediate_actions': self.immediate_actions,
            'confidence': self.confidence,
            'model_version': self.model_version,
            'assessed_at': self.assessed_at.isoformat()
        }


@dataclass
class ComprehensivePsychProfile:
    """Perfil psicológico completo del paciente."""
    user_id: str
    big_five_profile: Optional[BigFiveProfile] = None
    attachment_style: AttachmentStyle = AttachmentStyle.UNKNOWN
    dominant_defense_mechanisms: List[DefenseMechanism] = field(default_factory=list)
    recent_assessments: List[PsychologicalAssessment] = field(default_factory=list)
    emotional_patterns: List[TemporalPattern] = field(default_factory=list)
    personality_insights: List[PersonalityInsight] = field(default_factory=list)
    mindfulness_history: List[MindfulnessSession] = field(default_factory=list)
    longitudinal_data: List[LongitudinalDataPoint] = field(default_factory=list)
    crisis_assessments: List[CrisisRiskAssessment] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            'user_id': self.user_id,
            'big_five_profile': self.big_five_profile.to_dict() if self.big_five_profile else None,
            'attachment_style': self.attachment_style.value,
            'dominant_defense_mechanisms': [dm.value for dm in self.dominant_defense_mechanisms],
            'recent_assessments': [ra.to_dict() for ra in self.recent_assessments],
            'emotional_patterns': [ep.to_dict() for ep in self.emotional_patterns],
            'personality_insights': [pi.to_dict() for pi in self.personality_insights],
            'mindfulness_history': [mh.to_dict() for mh in self.mindfulness_history],
            'longitudinal_data': [ld.to_dict() for ld in self.longitudinal_data],
            'crisis_assessments': [ca.to_dict() for ca in self.crisis_assessments],
            'last_updated': self.last_updated.isoformat()
        }


# Utilidades para gestión de datos
class PsychologyDataManager:
    """Gestor de datos psicológicos con funciones de utilidad."""
    
    @staticmethod
    def create_emotional_state_from_analysis(
        analysis_result: dict, 
        timestamp: datetime = None
    ) -> EmotionalState:
        """Crear EmotionalState desde resultado de análisis NLP."""
        if timestamp is None:
            timestamp = datetime.now()
            
        return EmotionalState(
            timestamp=timestamp,
            primary_emotion=EmotionCategory(analysis_result.get('primary_emotion', 'contentment')),
            secondary_emotions=[
                EmotionCategory(e) for e in analysis_result.get('secondary_emotions', [])
            ],
            intensity=analysis_result.get('intensity', 50.0),
            valence=analysis_result.get('valence', 0.0),
            arousal=analysis_result.get('arousal', 50.0),
            mixed_emotions=analysis_result.get('mixed_emotions', False),
            contradictory_emotions=analysis_result.get('contradictory_emotions', []),
            confidence=analysis_result.get('confidence', 0.7)
        )
    
    @staticmethod
    def calculate_assessment_severity(score: float, assessment_type: str) -> str:
        """Calcular nivel de severidad basado en puntuación y tipo de evaluación."""
        cutoffs = {
            'PHQ-9': {'minimal': 4, 'mild': 9, 'moderate': 14, 'severe': 19},
            'GAD-7': {'minimal': 4, 'mild': 9, 'moderate': 14, 'severe': float('inf')},
            'Beck-Depression': {'minimal': 13, 'mild': 19, 'moderate': 28, 'severe': float('inf')}
        }
        
        if assessment_type not in cutoffs:
            return "unknown"
            
        thresholds = cutoffs[assessment_type]
        
        if score <= thresholds['minimal']:
            return "minimal"
        elif score <= thresholds['mild']:
            return "mild"
        elif score <= thresholds['moderate']:
            return "moderate"
        else:
            return "severe"
    
    @staticmethod
    def aggregate_longitudinal_data(
        data_points: List[LongitudinalDataPoint], 
        period: str = "weekly"
    ) -> List[Dict[str, Any]]:
        """Agregar datos longitudinales por período."""
        # Implementation for data aggregation
        # This would include grouping by time periods and calculating averages
        # Placeholder for now
        return [] 
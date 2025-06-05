"""
Servicio de análisis emocional avanzado con NLP.
Detecta emociones mixtas, contradictorias y fluctuaciones en tiempo real.
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from collections import Counter, defaultdict
import statistics

from src.models.psychology_models import (
    EmotionalState, EmotionCategory, LongitudinalDataPoint,
    PsychologyDataManager
)

# Configurar logging
logger = logging.getLogger(__name__)


class AdvancedEmotionAnalyzer:
    """Analizador de emociones con capacidades NLP avanzadas."""
    
    def __init__(self):
        """Inicializar el analizador de emociones."""
        self.emotion_lexicon = self._load_emotion_lexicon()
        self.contradiction_patterns = self._load_contradiction_patterns()
        self.intensity_modifiers = self._load_intensity_modifiers()
        self.session_emotional_history = []
        
    def _load_emotion_lexicon(self) -> Dict[str, Dict[str, Any]]:
        """Cargar lexicón de emociones expandido."""
        return {
            # Emociones primarias con valencia y arousal
            'alegría': {'category': EmotionCategory.JOY, 'valence': 80, 'arousal': 70},
            'feliz': {'category': EmotionCategory.JOY, 'valence': 75, 'arousal': 60},
            'contento': {'category': EmotionCategory.CONTENTMENT, 'valence': 60, 'arousal': 40},
            'eufórico': {'category': EmotionCategory.JOY, 'valence': 90, 'arousal': 90},
            'emocionado': {'category': EmotionCategory.EXCITEMENT, 'valence': 70, 'arousal': 85},
            
            'tristeza': {'category': EmotionCategory.SADNESS, 'valence': -70, 'arousal': 30},
            'triste': {'category': EmotionCategory.SADNESS, 'valence': -60, 'arousal': 25},
            'deprimido': {'category': EmotionCategory.SADNESS, 'valence': -80, 'arousal': 20},
            'melancólico': {'category': EmotionCategory.SADNESS, 'valence': -50, 'arousal': 15},
            'abatido': {'category': EmotionCategory.SADNESS, 'valence': -75, 'arousal': 10},
            
            'ansiedad': {'category': EmotionCategory.ANXIETY, 'valence': -40, 'arousal': 80},
            'ansioso': {'category': EmotionCategory.ANXIETY, 'valence': -35, 'arousal': 75},
            'nervioso': {'category': EmotionCategory.ANXIETY, 'valence': -30, 'arousal': 70},
            'preocupado': {'category': EmotionCategory.ANXIETY, 'valence': -25, 'arousal': 60},
            'agitado': {'category': EmotionCategory.ANXIETY, 'valence': -40, 'arousal': 85},
            
            'ira': {'category': EmotionCategory.ANGER, 'valence': -60, 'arousal': 85},
            'enojado': {'category': EmotionCategory.ANGER, 'valence': -55, 'arousal': 80},
            'furioso': {'category': EmotionCategory.ANGER, 'valence': -85, 'arousal': 95},
            'molesto': {'category': EmotionCategory.ANGER, 'valence': -40, 'arousal': 60},
            'irritado': {'category': EmotionCategory.ANGER, 'valence': -45, 'arousal': 65},
            
            'miedo': {'category': EmotionCategory.FEAR, 'valence': -70, 'arousal': 75},
            'temor': {'category': EmotionCategory.FEAR, 'valence': -60, 'arousal': 70},
            'pánico': {'category': EmotionCategory.FEAR, 'valence': -85, 'arousal': 95},
            'terror': {'category': EmotionCategory.FEAR, 'valence': -90, 'arousal': 90},
            
            'confusión': {'category': EmotionCategory.CONFUSION, 'valence': -10, 'arousal': 50},
            'confundido': {'category': EmotionCategory.CONFUSION, 'valence': -15, 'arousal': 45},
            'perdido': {'category': EmotionCategory.CONFUSION, 'valence': -20, 'arousal': 40},
            
            'ambivalencia': {'category': EmotionCategory.AMBIVALENCE, 'valence': 0, 'arousal': 60},
            'ambivalente': {'category': EmotionCategory.AMBIVALENCE, 'valence': 0, 'arousal': 55},
            'contradictorio': {'category': EmotionCategory.AMBIVALENCE, 'valence': 0, 'arousal': 65}
        }
    
    def _load_contradiction_patterns(self) -> List[Dict[str, Any]]:
        """Cargar patrones de contradicción emocional."""
        return [
            {
                'pattern': r'(feliz|contento|alegre).*(pero|sin embargo|aunque).*(triste|deprimido|mal)',
                'type': 'joy_sadness_contradiction',
                'emotions': [EmotionCategory.JOY, EmotionCategory.SADNESS]
            },
            {
                'pattern': r'(tranquilo|relajado|calm[ao]).*(pero|sin embargo|aunque).*(nervioso|ansioso|preocupado)',
                'type': 'calm_anxiety_contradiction',
                'emotions': [EmotionCategory.CONTENTMENT, EmotionCategory.ANXIETY]
            },
            {
                'pattern': r'(bien|mejor).*(pero|sin embargo|aunque).*(mal|peor|horrible)',
                'type': 'positive_negative_contradiction',
                'emotions': [EmotionCategory.JOY, EmotionCategory.SADNESS]
            },
            {
                'pattern': r'(amo|quiero|adoro).*(pero|sin embargo|aunque).*(odio|detesto|no soporto)',
                'type': 'love_hate_contradiction',
                'emotions': [EmotionCategory.JOY, EmotionCategory.ANGER]
            },
            {
                'pattern': r'me siento (.*) y (.*) a la vez',
                'type': 'simultaneous_emotions',
                'emotions': []  # Se detectan dinámicamente
            }
        ]
    
    def _load_intensity_modifiers(self) -> Dict[str, float]:
        """Cargar modificadores de intensidad emocional."""
        return {
            # Amplificadores
            'muy': 1.3,
            'súper': 1.4,
            'extremadamente': 1.5,
            'increíblemente': 1.4,
            'totalmente': 1.3,
            'completamente': 1.3,
            'absolutamente': 1.4,
            'profundamente': 1.3,
            'intensamente': 1.4,
            
            # Atenuadores
            'un poco': 0.6,
            'algo': 0.7,
            'ligeramente': 0.5,
            'levemente': 0.6,
            'moderadamente': 0.8,
            'relativamente': 0.7,
            'bastante': 0.9,
            'medio': 0.7,
            'apenas': 0.4
        }
    
    def analyze_emotional_content(self, text: str, timestamp: datetime = None) -> EmotionalState:
        """Analizar contenido emocional completo de un texto."""
        if timestamp is None:
            timestamp = datetime.now()
        
        # Preprocesar texto
        text_normalized = self._preprocess_text(text)
        
        # Detectar emociones presentes
        detected_emotions = self._detect_emotions(text_normalized)
        
        # Analizar contradicciones
        contradictions = self._detect_contradictions(text_normalized)
        
        # Calcular intensidad total
        intensity = self._calculate_intensity(text_normalized, detected_emotions)
        
        # Calcular valencia y arousal promedio
        valence, arousal = self._calculate_valence_arousal(detected_emotions)
        
        # Determinar emoción primaria
        primary_emotion = self._determine_primary_emotion(detected_emotions)
        
        # Detectar emociones secundarias
        secondary_emotions = self._determine_secondary_emotions(detected_emotions, primary_emotion)
        
        # Detectar triggers emocionales
        triggers = self._extract_emotional_triggers(text_normalized)
        
        # Crear estado emocional
        emotional_state = EmotionalState(
            timestamp=timestamp,
            primary_emotion=primary_emotion,
            secondary_emotions=secondary_emotions,
            intensity=intensity,
            valence=valence,
            arousal=arousal,
            mixed_emotions=len(detected_emotions) > 1,
            contradictory_emotions=[c['type'] for c in contradictions],
            confidence=self._calculate_confidence(detected_emotions, contradictions),
            triggers=triggers
        )
        
        # Agregar a historial de sesión para tracking
        self.session_emotional_history.append(emotional_state)
        
        return emotional_state
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocesar texto para análisis."""
        # Convertir a minúsculas
        text = text.lower()
        
        # Remover caracteres especiales pero mantener puntuación relevante
        text = re.sub(r'[^\w\s.,;:!?()]', '', text)
        
        return text
    
    def _detect_emotions(self, text: str) -> List[Dict[str, Any]]:
        """Detectar emociones presentes en el texto."""
        detected = []
        
        for word, emotion_data in self.emotion_lexicon.items():
            if word in text:
                # Calcular intensidad basada en modificadores cercanos
                intensity_modifier = self._find_intensity_modifier(text, word)
                
                detected.append({
                    'emotion': emotion_data['category'],
                    'word': word,
                    'base_valence': emotion_data['valence'],
                    'base_arousal': emotion_data['arousal'],
                    'intensity_modifier': intensity_modifier,
                    'position': text.find(word)
                })
        
        return detected
    
    def _find_intensity_modifier(self, text: str, emotion_word: str) -> float:
        """Encontrar modificadores de intensidad cerca de la palabra emocional."""
        word_position = text.find(emotion_word)
        
        # Buscar en un rango de 20 caracteres antes de la palabra
        search_start = max(0, word_position - 20)
        search_text = text[search_start:word_position]
        
        modifier = 1.0
        for mod_word, mod_value in self.intensity_modifiers.items():
            if mod_word in search_text:
                modifier = mod_value
                break
        
        return modifier
    
    def _detect_contradictions(self, text: str) -> List[Dict[str, Any]]:
        """Detectar contradicciones emocionales en el texto."""
        contradictions = []
        
        for pattern_data in self.contradiction_patterns:
            matches = re.finditer(pattern_data['pattern'], text, re.IGNORECASE)
            
            for match in matches:
                contradiction = {
                    'type': pattern_data['type'],
                    'text_match': match.group(),
                    'emotions': pattern_data['emotions'],
                    'position': match.start()
                }
                contradictions.append(contradiction)
        
        return contradictions
    
    def _calculate_intensity(self, text: str, detected_emotions: List[Dict]) -> float:
        """Calcular intensidad emocional general."""
        if not detected_emotions:
            return 0.0
        
        # Intensidad basada en número de emociones y modificadores
        base_intensity = min(100.0, len(detected_emotions) * 20)
        
        # Ajustar por modificadores de intensidad
        modifier_sum = sum(emotion['intensity_modifier'] for emotion in detected_emotions)
        modifier_avg = modifier_sum / len(detected_emotions)
        
        final_intensity = base_intensity * modifier_avg
        
        # Detectar signos de alta intensidad (mayúsculas, signos de exclamación)
        if re.search(r'[A-Z]{3,}', text):  # Texto en mayúsculas
            final_intensity *= 1.2
        
        exclamation_count = text.count('!')
        if exclamation_count > 0:
            final_intensity *= (1 + exclamation_count * 0.1)
        
        return min(100.0, final_intensity)
    
    def _calculate_valence_arousal(self, detected_emotions: List[Dict]) -> Tuple[float, float]:
        """Calcular valencia y arousal promedio."""
        if not detected_emotions:
            return 0.0, 50.0
        
        valences = []
        arousals = []
        
        for emotion in detected_emotions:
            # Ajustar valencia y arousal por modificadores de intensidad
            adjusted_valence = emotion['base_valence'] * emotion['intensity_modifier']
            adjusted_arousal = emotion['base_arousal'] * emotion['intensity_modifier']
            
            valences.append(adjusted_valence)
            arousals.append(adjusted_arousal)
        
        avg_valence = statistics.mean(valences)
        avg_arousal = statistics.mean(arousals)
        
        # Normalizar arousal a 0-100
        avg_arousal = max(0, min(100, avg_arousal))
        
        return avg_valence, avg_arousal
    
    def _determine_primary_emotion(self, detected_emotions: List[Dict]) -> EmotionCategory:
        """Determinar la emoción primaria."""
        if not detected_emotions:
            return EmotionCategory.CONTENTMENT
        
        # Priorizar por intensidad modificada
        primary = max(detected_emotions, key=lambda x: x['intensity_modifier'])
        return primary['emotion']
    
    def _determine_secondary_emotions(self, detected_emotions: List[Dict], 
                                    primary_emotion: EmotionCategory) -> List[EmotionCategory]:
        """Determinar emociones secundarias."""
        secondary = []
        
        for emotion_data in detected_emotions:
            if emotion_data['emotion'] != primary_emotion:
                secondary.append(emotion_data['emotion'])
        
        # Limitar a máximo 3 emociones secundarias
        return secondary[:3]
    
    def _extract_emotional_triggers(self, text: str) -> List[str]:
        """Extraer posibles triggers emocionales del texto."""
        trigger_patterns = [
            r'cuando (.*?)[.,]',
            r'porque (.*?)[.,]',
            r'después de (.*?)[.,]',
            r'antes de (.*?)[.,]',
            r'si (.*?)[.,]',
            r'me recuerda a (.*?)[.,]',
            r'me hace pensar en (.*?)[.,]'
        ]
        
        triggers = []
        for pattern in trigger_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                trigger = match.group(1).strip()
                if len(trigger) > 3:  # Filtrar triggers muy cortos
                    triggers.append(trigger)
        
        return triggers[:5]  # Limitar a 5 triggers
    
    def _calculate_confidence(self, detected_emotions: List[Dict], 
                            contradictions: List[Dict]) -> float:
        """Calcular nivel de confianza del análisis."""
        base_confidence = 0.7
        
        # Aumentar confianza con más emociones detectadas
        if detected_emotions:
            emotion_boost = min(0.2, len(detected_emotions) * 0.05)
            base_confidence += emotion_boost
        
        # Reducir confianza con contradicciones
        if contradictions:
            contradiction_penalty = len(contradictions) * 0.1
            base_confidence -= contradiction_penalty
        
        return max(0.3, min(1.0, base_confidence))
    
    def analyze_session_emotional_fluctuations(self) -> Dict[str, Any]:
        """Analizar fluctuaciones emocionales durante la sesión."""
        if len(self.session_emotional_history) < 2:
            return {'fluctuations': [], 'stability': 'insufficient_data'}
        
        fluctuations = []
        
        for i in range(1, len(self.session_emotional_history)):
            prev_state = self.session_emotional_history[i-1]
            curr_state = self.session_emotional_history[i]
            
            # Calcular cambio en valencia
            valence_change = curr_state.valence - prev_state.valence
            
            # Calcular cambio en intensidad
            intensity_change = curr_state.intensity - prev_state.intensity
            
            # Detectar cambio de emoción primaria
            emotion_change = prev_state.primary_emotion != curr_state.primary_emotion
            
            if abs(valence_change) > 20 or abs(intensity_change) > 15 or emotion_change:
                fluctuation = {
                    'timestamp': curr_state.timestamp.isoformat(),
                    'type': 'significant_change',
                    'valence_change': valence_change,
                    'intensity_change': intensity_change,
                    'emotion_change': emotion_change,
                    'from_emotion': prev_state.primary_emotion.value,
                    'to_emotion': curr_state.primary_emotion.value
                }
                fluctuations.append(fluctuation)
        
        # Calcular estabilidad emocional
        stability = self._calculate_emotional_stability()
        
        return {
            'fluctuations': fluctuations,
            'stability': stability,
            'total_states_analyzed': len(self.session_emotional_history),
            'significant_changes': len(fluctuations)
        }
    
    def _calculate_emotional_stability(self) -> str:
        """Calcular estabilidad emocional de la sesión."""
        if len(self.session_emotional_history) < 3:
            return 'insufficient_data'
        
        valence_values = [state.valence for state in self.session_emotional_history]
        intensity_values = [state.intensity for state in self.session_emotional_history]
        
        valence_std = statistics.stdev(valence_values)
        intensity_std = statistics.stdev(intensity_values)
        
        # Clasificar estabilidad
        if valence_std < 15 and intensity_std < 15:
            return 'very_stable'
        elif valence_std < 25 and intensity_std < 25:
            return 'stable'
        elif valence_std < 40 and intensity_std < 40:
            return 'moderate_fluctuation'
        else:
            return 'high_fluctuation'
    
    def detect_mixed_emotions_patterns(self) -> Dict[str, Any]:
        """Detectar patrones de emociones mixtas complejas."""
        mixed_emotions_count = sum(1 for state in self.session_emotional_history if state.mixed_emotions)
        total_states = len(self.session_emotional_history)
        
        if total_states == 0:
            return {'mixed_emotions_rate': 0, 'patterns': []}
        
        mixed_emotions_rate = mixed_emotions_count / total_states
        
        # Identificar combinaciones comunes de emociones
        emotion_combinations = defaultdict(int)
        
        for state in self.session_emotional_history:
            if state.mixed_emotions and state.secondary_emotions:
                primary = state.primary_emotion.value
                for secondary in state.secondary_emotions:
                    combination = f"{primary}_{secondary.value}"
                    emotion_combinations[combination] += 1
        
        # Ordenar por frecuencia
        common_patterns = sorted(emotion_combinations.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'mixed_emotions_rate': mixed_emotions_rate,
            'patterns': common_patterns,
            'complexity_level': 'high' if mixed_emotions_rate > 0.6 else 'moderate' if mixed_emotions_rate > 0.3 else 'low'
        }
    
    def reset_session_history(self):
        """Reiniciar historial de sesión para nueva consulta."""
        self.session_emotional_history = []
        logger.info("Historial emocional de sesión reiniciado")


class EmotionAnalysisService:
    """Servicio principal de análisis emocional."""
    
    def __init__(self):
        """Inicializar servicio de análisis emocional."""
        self.analyzer = AdvancedEmotionAnalyzer()
        self.session_data = {}
        
    def analyze_message_emotions(self, message: str, session_id: str) -> Dict[str, Any]:
        """Analizar emociones de un mensaje específico."""
        try:
            # Analizar estado emocional
            emotional_state = self.analyzer.analyze_emotional_content(message)
            
            # Almacenar en datos de sesión
            if session_id not in self.session_data:
                self.session_data[session_id] = []
            
            self.session_data[session_id].append(emotional_state)
            
            # Crear punto de datos longitudinal
            longitudinal_point = LongitudinalDataPoint(
                timestamp=emotional_state.timestamp,
                metric_type="emotional_valence",
                value=emotional_state.valence,
                context=f"Session message analysis",
                source="session"
            )
            
            return {
                'emotional_state': emotional_state.to_dict(),
                'longitudinal_data': longitudinal_point.to_dict(),
                'analysis_metadata': {
                    'mixed_emotions_detected': emotional_state.mixed_emotions,
                    'contradictions_found': len(emotional_state.contradictory_emotions) > 0,
                    'confidence_level': emotional_state.confidence,
                    'triggers_identified': len(emotional_state.triggers)
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing message emotions: {str(e)}")
            return {'error': str(e)}
    
    def get_session_emotional_analysis(self, session_id: str) -> Dict[str, Any]:
        """Obtener análisis emocional completo de la sesión."""
        try:
            # Analizar fluctuaciones
            fluctuations = self.analyzer.analyze_session_emotional_fluctuations()
            
            # Detectar patrones de emociones mixtas
            mixed_patterns = self.analyzer.detect_mixed_emotions_patterns()
            
            # Análisis longitudinal de la sesión
            session_states = self.session_data.get(session_id, [])
            
            return {
                'session_id': session_id,
                'total_emotional_states': len(session_states),
                'fluctuation_analysis': fluctuations,
                'mixed_emotions_analysis': mixed_patterns,
                'session_emotional_journey': [state.to_dict() for state in session_states],
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating session emotional analysis: {str(e)}")
            return {'error': str(e)}
    
    def reset_session(self, session_id: str):
        """Reiniciar datos de sesión."""
        if session_id in self.session_data:
            del self.session_data[session_id]
        self.analyzer.reset_session_history()
        logger.info(f"Session {session_id} emotional data reset") 
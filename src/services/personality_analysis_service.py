"""
Servicio de análisis de personalidad profundo.
Detecta rasgos Big Five, estilos de apego y mecanismos de defensa.
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
import statistics

from src.models.psychology_models import (
    BigFiveProfile, AttachmentStyle, DefenseMechanism, PersonalityInsight,
    ComprehensivePsychProfile
)

# Configurar logging
logger = logging.getLogger(__name__)


class BigFiveAnalyzer:
    """Analizador especializado en rasgos de personalidad Big Five (OCEAN)."""
    
    def __init__(self):
        """Inicializar analizador Big Five."""
        self.trait_indicators = self._load_trait_indicators()
        self.conversation_samples = []
        
    def _load_trait_indicators(self) -> Dict[str, Dict[str, List[str]]]:
        """Cargar indicadores de rasgos de personalidad."""
        return {
            'openness': {
                'high': [
                    'creativo', 'imaginativo', 'curioso', 'artístico', 'innovador',
                    'original', 'intelectual', 'filosófico', 'abstracto', 'complejo',
                    'me gusta experimentar', 'disfruto el arte', 'ideas nuevas',
                    'poco convencional', 'aventurero', 'explorar', 'fantasía'
                ],
                'low': [
                    'tradicional', 'convencional', 'práctico', 'realista', 'concreto',
                    'simple', 'rutina', 'estable', 'conservador', 'literal',
                    'prefiero lo conocido', 'métodos probados', 'sin cambios'
                ]
            },
            'conscientiousness': {
                'high': [
                    'organizado', 'responsable', 'disciplinado', 'puntual', 'metódico',
                    'planificado', 'ordenado', 'sistemático', 'eficiente', 'cuidadoso',
                    'siempre a tiempo', 'listas de tareas', 'metas claras',
                    'perseverante', 'trabajador', 'confiable', 'autodisciplina'
                ],
                'low': [
                    'desorganizado', 'impulsivo', 'descuidado', 'impuntual', 'caótico',
                    'espontáneo', 'flexible', 'relajado', 'informal', 'procrastino',
                    'olvido cosas', 'sin planear', 'vivo el momento'
                ]
            },
            'extraversion': {
                'high': [
                    'sociable', 'extrovertido', 'hablador', 'enérgico', 'asertivo',
                    'dominante', 'activo', 'entusiasta', 'optimista', 'alegre',
                    'me gusta la gente', 'fiestas', 'centro de atención',
                    'expresivo', 'aventurero socialmente', 'líder'
                ],
                'low': [
                    'introvertido', 'reservado', 'callado', 'tímido', 'solitario',
                    'reflexivo', 'serio', 'independiente', 'prefiero estar solo',
                    'grupos pequeños', 'observador', 'introspectivo', 'prudente'
                ]
            },
            'agreeableness': {
                'high': [
                    'amable', 'cooperativo', 'confiado', 'empático', 'generoso',
                    'altruista', 'comprensivo', 'perdonador', 'tolerante', 'bondadoso',
                    'ayudo a otros', 'trabajo en equipo', 'compasivo',
                    'considerado', 'diplomático', 'paciente'
                ],
                'low': [
                    'competitivo', 'escéptico', 'crítico', 'directo', 'independiente',
                    'realista', 'pragmático', 'firme', 'objetivo', 'analítico',
                    'digo lo que pienso', 'primero yo', 'no me fío fácilmente'
                ]
            },
            'neuroticism': {
                'high': [
                    'ansioso', 'estresado', 'preocupado', 'nervioso', 'tenso',
                    'irritable', 'emocional', 'inestable', 'sensible', 'vulnerable',
                    'me preocupo mucho', 'estrés frecuente', 'cambios de humor',
                    'inseguro', 'pesimista', 'reactivo emocionalmente'
                ],
                'low': [
                    'calmado', 'relajado', 'estable', 'seguro', 'tranquilo',
                    'equilibrado', 'sereno', 'confiado', 'resistente', 'imperturbable',
                    'manejo bien el estrés', 'emocionalmente estable', 'optimista'
                ]
            }
        }
    
    def analyze_conversation_for_traits(self, conversation_text: str) -> BigFiveProfile:
        """Analizar conversación para extraer rasgos Big Five."""
        text_normalized = conversation_text.lower()
        
        trait_scores = {}
        confidence_scores = {}
        
        for trait, indicators in self.trait_indicators.items():
            high_count = sum(1 for indicator in indicators['high'] if indicator in text_normalized)
            low_count = sum(1 for indicator in indicators['low'] if indicator in text_normalized)
            
            total_indicators = len(indicators['high']) + len(indicators['low'])
            found_indicators = high_count + low_count
            
            # Calcular puntuación (0-100)
            if found_indicators == 0:
                trait_scores[trait] = 50.0  # Neutral cuando no hay evidencia
                confidence_scores[trait] = 0.1
            else:
                # Puntuación basada en proporción de indicadores altos vs bajos
                raw_score = (high_count - low_count) / max(found_indicators, 1)
                trait_scores[trait] = max(0, min(100, 50 + (raw_score * 50)))
                confidence_scores[trait] = min(1.0, found_indicators / 10)  # Máxima confianza con 10+ indicadores
        
        # Calcular confianza general
        overall_confidence = statistics.mean(confidence_scores.values())
        
        return BigFiveProfile(
            openness=trait_scores['openness'],
            conscientiousness=trait_scores['conscientiousness'],
            extraversion=trait_scores['extraversion'],
            agreeableness=trait_scores['agreeableness'],
            neuroticism=trait_scores['neuroticism'],
            confidence_level=overall_confidence,
            analysis_date=datetime.now()
        )
    
    def generate_trait_insights(self, profile: BigFiveProfile) -> List[PersonalityInsight]:
        """Generar insights específicos basados en el perfil Big Five."""
        insights = []
        
        # Insights para Openness
        if profile.openness > 70:
            insights.append(PersonalityInsight(
                insight_type="big_five",
                content="Alta apertura a experiencias: Probablemente disfruta explorando ideas nuevas y enfoques creativos en terapia",
                confidence=profile.confidence_level,
                supporting_evidence=["Vocabulario imaginativo", "Interés en conceptos abstractos"]
            ))
        elif profile.openness < 30:
            insights.append(PersonalityInsight(
                insight_type="big_five",
                content="Preferencia por enfoques estructurados: Puede beneficiarse de técnicas terapéuticas concretas y basadas en evidencia",
                confidence=profile.confidence_level,
                supporting_evidence=["Lenguaje práctico", "Preferencia por lo conocido"]
            ))
        
        # Insights para Conscientiousness
        if profile.conscientiousness > 70:
            insights.append(PersonalityInsight(
                insight_type="big_five",
                content="Alta responsabilidad: Probable alta adherencia a tareas terapéuticas y homework asignado",
                confidence=profile.confidence_level,
                supporting_evidence=["Menciones de organización", "Enfoque en metas"]
            ))
        elif profile.conscientiousness < 30:
            insights.append(PersonalityInsight(
                insight_type="big_five",
                content="Estilo flexible: Podría necesitar estructura adicional y recordatorios para seguimiento terapéutico",
                confidence=profile.confidence_level,
                supporting_evidence=["Comentarios sobre espontaneidad", "Dificultades organizacionales"]
            ))
        
        # Insights para Extraversion
        if profile.extraversion > 70:
            insights.append(PersonalityInsight(
                insight_type="big_five",
                content="Orientación social: Puede beneficiarse de terapia grupal o enfoques interpersonales",
                confidence=profile.confidence_level,
                supporting_evidence=["Referencias sociales frecuentes", "Estilo comunicativo expresivo"]
            ))
        elif profile.extraversion < 30:
            insights.append(PersonalityInsight(
                insight_type="big_five",
                content="Preferencia introspectiva: Probablemente responda bien a terapia individual y técnicas reflexivas",
                confidence=profile.confidence_level,
                supporting_evidence=["Comunicación reflexiva", "Menciones de soledad como positiva"]
            ))
        
        # Insights para Agreeableness
        if profile.agreeableness > 70:
            insights.append(PersonalityInsight(
                insight_type="big_five",
                content="Alta cooperación: Probablemente forme alianza terapéutica fácilmente, pero puede evitar conflictos importantes",
                confidence=profile.confidence_level,
                supporting_evidence=["Lenguaje cooperativo", "Enfoque en otros"]
            ))
        elif profile.agreeableness < 30:
            insights.append(PersonalityInsight(
                insight_type="big_five",
                content="Enfoque directo: Puede requerir tiempo adicional para establecer confianza, pero probablemente sea honesto sobre problemas",
                confidence=profile.confidence_level,
                supporting_evidence=["Comunicación directa", "Escepticismo expresado"]
            ))
        
        # Insights para Neuroticism
        if profile.neuroticism > 70:
            insights.append(PersonalityInsight(
                insight_type="big_five",
                content="Alta sensibilidad emocional: Priorizar técnicas de regulación emocional y manejo de estrés",
                confidence=profile.confidence_level,
                supporting_evidence=["Frecuentes referencias emocionales", "Expresiones de preocupación"]
            ))
        elif profile.neuroticism < 30:
            insights.append(PersonalityInsight(
                insight_type="big_five",
                content="Estabilidad emocional: Recurso importante para afrontar desafíos terapéuticos",
                confidence=profile.confidence_level,
                supporting_evidence=["Lenguaje calmado", "Menciones de manejo de estrés"]
            ))
        
        return insights


class AttachmentStyleAnalyzer:
    """Analizador de estilos de apego."""
    
    def __init__(self):
        """Inicializar analizador de estilos de apego."""
        self.attachment_indicators = self._load_attachment_indicators()
        
    def _load_attachment_indicators(self) -> Dict[str, List[str]]:
        """Cargar indicadores de estilos de apego."""
        return {
            'secure': [
                'relaciones estables', 'confío en otros', 'cómodo con intimidad',
                'apoyo emocional', 'comunicación abierta', 'expresar necesidades',
                'equilibrio independencia', 'resolver conflictos', 'confianza básica',
                'me siento seguro', 'puedo depender de otros', 'relaciones satisfactorias'
            ],
            'anxious_preoccupied': [
                'miedo al abandono', 'necesito constante confirmación', 'celos',
                'preocupado por relaciones', 'busco aprobación', 'ansiedad separación',
                'dependencia emocional', 'idealizo pareja', 'miedo al rechazo',
                'necesito atención', 'inseguro en relaciones', 'drama relacional'
            ],
            'dismissive_avoidant': [
                'independiente emocional', 'evito intimidad', 'no necesito a nadie',
                'relaciones superficiales', 'dificultad expresar emociones', 'autosuficiente',
                'distancia emocional', 'incomodidad dependencia', 'prefiero estar solo',
                'no confío fácilmente', 'evito compromiso', 'relaciones casuales'
            ],
            'fearful_avoidant': [
                'quiero intimidad pero me da miedo', 'relaciones complicadas', 'ambivalente',
                'acerco y alejo', 'confuso sobre relaciones', 'miedo vulnerabilidad',
                'patrón acercamiento-evitación', 'relaciones caóticas', 'contradictorio amor',
                'necesito pero temo', 'heridas del pasado', 'dificulta confiar'
            ]
        }
    
    def analyze_attachment_style(self, conversation_text: str) -> Tuple[AttachmentStyle, float]:
        """Analizar estilo de apego predominante."""
        text_normalized = conversation_text.lower()
        
        style_scores = {}
        
        for style, indicators in self.attachment_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_normalized)
            style_scores[style] = score
        
        if not any(style_scores.values()):
            return AttachmentStyle.UNKNOWN, 0.0
        
        # Determinar estilo predominante
        max_style = max(style_scores, key=style_scores.get)
        max_score = style_scores[max_style]
        total_indicators = sum(style_scores.values())
        
        # Calcular confianza
        confidence = min(1.0, max_score / 5)  # Máxima confianza con 5+ indicadores
        
        # Mapear a enum
        style_mapping = {
            'secure': AttachmentStyle.SECURE,
            'anxious_preoccupied': AttachmentStyle.ANXIOUS_PREOCCUPIED,
            'dismissive_avoidant': AttachmentStyle.DISMISSIVE_AVOIDANT,
            'fearful_avoidant': AttachmentStyle.FEARFUL_AVOIDANT
        }
        
        return style_mapping[max_style], confidence
    
    def generate_attachment_insights(self, style: AttachmentStyle, confidence: float) -> List[PersonalityInsight]:
        """Generar insights específicos del estilo de apego."""
        insights = []
        
        if style == AttachmentStyle.SECURE:
            insights.append(PersonalityInsight(
                insight_type="attachment",
                content="Estilo de apego seguro: Recurso importante para la terapia. Probablemente forme alianza terapéutica sólida",
                confidence=confidence,
                supporting_evidence=["Comunicación relacional positiva", "Confianza en relaciones"]
            ))
        
        elif style == AttachmentStyle.ANXIOUS_PREOCCUPIED:
            insights.append(PersonalityInsight(
                insight_type="attachment",
                content="Estilo ansioso: Puede buscar excesiva validación del terapeuta. Trabajar en autovalidación y tolerancia a la incertidumbre",
                confidence=confidence,
                supporting_evidence=["Patrones de búsqueda de aprobación", "Ansiedad relacional"]
            ))
        
        elif style == AttachmentStyle.DISMISSIVE_AVOIDANT:
            insights.append(PersonalityInsight(
                insight_type="attachment",
                content="Estilo evitativo: Puede resistir vulnerabilidad terapéutica. Ir gradualmente hacia mayor apertura emocional",
                confidence=confidence,
                supporting_evidence=["Patrones de independencia emocional", "Evitación de intimidad"]
            ))
        
        elif style == AttachmentStyle.FEARFUL_AVOIDANT:
            insights.append(PersonalityInsight(
                insight_type="attachment",
                content="Estilo desorganizado: Ambivalencia hacia cercanía. Priorizar seguridad y predictibilidad en terapia",
                confidence=confidence,
                supporting_evidence=["Patrones contradictorios", "Conflictos relacionales"]
            ))
        
        return insights


class DefenseMechanismAnalyzer:
    """Analizador de mecanismos de defensa psicológicos."""
    
    def __init__(self):
        """Inicializar analizador de mecanismos de defensa."""
        self.defense_patterns = self._load_defense_patterns()
        
    def _load_defense_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Cargar patrones de mecanismos de defensa."""
        return {
            'denial': {
                'patterns': [
                    r'no es tan malo', r'no es un problema', r'está bien así',
                    r'no me afecta', r'no es importante', r'exageran'
                ],
                'keywords': ['negar', 'no pasa nada', 'minimizar', 'está bien', 'no es grave'],
                'level': 'primitive'
            },
            'projection': {
                'patterns': [
                    r'él/ella es el problema', r'todos son.*', r'la culpa es de',
                    r'ellos siempre', r'todo el mundo'
                ],
                'keywords': ['culpa de otros', 'todos hacen', 'problema de ellos', 'siempre los demás'],
                'level': 'primitive'
            },
            'rationalization': {
                'patterns': [
                    r'tiene sentido porque', r'es lógico que', r'la razón es',
                    r'está justificado', r'es comprensible'
                ],
                'keywords': ['lógico', 'racional', 'justificado', 'tiene sentido', 'explicación'],
                'level': 'neurotic'
            },
            'displacement': {
                'patterns': [
                    r'me desquito con', r'pago con', r'descargo en',
                    r'arremeto contra'
                ],
                'keywords': ['desquitarse', 'descargar', 'pagar con otros', 'dirigir hacia'],
                'level': 'neurotic'
            },
            'sublimation': {
                'patterns': [
                    r'canalizo en', r'transformo en', r'uso para crear',
                    r'convierto en arte'
                ],
                'keywords': ['canalizar', 'crear', 'arte', 'transformar energía', 'actividad constructiva'],
                'level': 'mature'
            },
            'humor': {
                'patterns': [
                    r'me río de', r'lo veo gracioso', r'le encuentro el lado cómico',
                    r'bromeo sobre'
                ],
                'keywords': ['humor', 'reírse', 'gracioso', 'cómico', 'bromear', 'ironía'],
                'level': 'mature'
            },
            'intellectualization': {
                'patterns': [
                    r'analizo objetivamente', r'desde el punto de vista',
                    r'racionalmente hablando', r'técnicamente'
                ],
                'keywords': ['analizar', 'objetivamente', 'racionalmente', 'técnico', 'intelectual'],
                'level': 'neurotic'
            }
        }
    
    def analyze_defense_mechanisms(self, conversation_text: str) -> List[Tuple[DefenseMechanism, float]]:
        """Analizar mecanismos de defensa presentes."""
        text_normalized = conversation_text.lower()
        
        detected_defenses = []
        
        for defense_name, defense_data in self.defense_patterns.items():
            score = 0
            evidence = []
            
            # Buscar patrones regex
            for pattern in defense_data['patterns']:
                matches = re.findall(pattern, text_normalized)
                score += len(matches)
                evidence.extend(matches)
            
            # Buscar palabras clave
            for keyword in defense_data['keywords']:
                if keyword in text_normalized:
                    score += 1
                    evidence.append(keyword)
            
            if score > 0:
                confidence = min(1.0, score / 3)  # Máxima confianza con 3+ evidencias
                
                # Mapear a enum
                defense_mapping = {
                    'denial': DefenseMechanism.DENIAL,
                    'projection': DefenseMechanism.PROJECTION,
                    'rationalization': DefenseMechanism.RATIONALIZATION,
                    'displacement': DefenseMechanism.DISPLACEMENT,
                    'sublimation': DefenseMechanism.SUBLIMATION,
                    'humor': DefenseMechanism.HUMOR,
                    'intellectualization': DefenseMechanism.INTELLECTUALIZATION
                }
                
                detected_defenses.append((defense_mapping[defense_name], confidence))
        
        # Ordenar por confianza
        detected_defenses.sort(key=lambda x: x[1], reverse=True)
        
        return detected_defenses[:3]  # Top 3 mecanismos de defensa
    
    def generate_defense_insights(self, defenses: List[Tuple[DefenseMechanism, float]]) -> List[PersonalityInsight]:
        """Generar insights sobre mecanismos de defensa."""
        insights = []
        
        defense_descriptions = {
            DefenseMechanism.DENIAL: "Mecanismo primitivo que puede interferir con el reconocimiento de problemas",
            DefenseMechanism.PROJECTION: "Tendencia a atribuir a otros los propios sentimientos o características",
            DefenseMechanism.RATIONALIZATION: "Uso de explicaciones lógicas para justificar comportamientos o sentimientos",
            DefenseMechanism.DISPLACEMENT: "Redirección de emociones hacia objetivos más seguros",
            DefenseMechanism.SUBLIMATION: "Canalización constructiva de impulsos hacia actividades socialmente valoradas",
            DefenseMechanism.HUMOR: "Uso adaptativo del humor para manejar situaciones difíciles",
            DefenseMechanism.INTELLECTUALIZATION: "Enfoque excesivamente racional para evitar emociones"
        }
        
        for defense, confidence in defenses:
            if confidence > 0.3:  # Solo incluir defenses con confianza suficiente
                insights.append(PersonalityInsight(
                    insight_type="defense_mechanism",
                    content=f"{defense.value}: {defense_descriptions[defense]}",
                    confidence=confidence,
                    supporting_evidence=[f"Patrones de {defense.value} detectados en conversación"]
                ))
        
        return insights


class PersonalityAnalysisService:
    """Servicio principal de análisis de personalidad."""
    
    def __init__(self):
        """Inicializar servicio de análisis de personalidad."""
        self.big_five_analyzer = BigFiveAnalyzer()
        self.attachment_analyzer = AttachmentStyleAnalyzer()
        self.defense_analyzer = DefenseMechanismAnalyzer()
        self.conversation_history = {}
        
    def analyze_comprehensive_personality(self, conversation_text: str, session_id: str) -> Dict[str, Any]:
        """Realizar análisis completo de personalidad."""
        try:
            # Almacenar conversación para análisis acumulativo
            if session_id not in self.conversation_history:
                self.conversation_history[session_id] = ""
            
            self.conversation_history[session_id] += " " + conversation_text
            full_text = self.conversation_history[session_id]
            
            # Análisis Big Five
            big_five_profile = self.big_five_analyzer.analyze_conversation_for_traits(full_text)
            big_five_insights = self.big_five_analyzer.generate_trait_insights(big_five_profile)
            
            # Análisis de estilo de apego
            attachment_style, attachment_confidence = self.attachment_analyzer.analyze_attachment_style(full_text)
            attachment_insights = self.attachment_analyzer.generate_attachment_insights(attachment_style, attachment_confidence)
            
            # Análisis de mecanismos de defensa
            defense_mechanisms = self.defense_analyzer.analyze_defense_mechanisms(full_text)
            defense_insights = self.defense_analyzer.generate_defense_insights(defense_mechanisms)
            
            # Combinar todos los insights
            all_insights = big_five_insights + attachment_insights + defense_insights
            
            # Crear perfil comprehensivo
            comprehensive_profile = ComprehensivePsychProfile(
                user_id=session_id,
                big_five_profile=big_five_profile,
                attachment_style=attachment_style,
                dominant_defense_mechanisms=[dm[0] for dm in defense_mechanisms],
                personality_insights=all_insights
            )
            
            return {
                'session_id': session_id,
                'big_five_analysis': {
                    'profile': big_five_profile.to_dict(),
                    'insights': [insight.to_dict() for insight in big_five_insights]
                },
                'attachment_analysis': {
                    'style': attachment_style.value,
                    'confidence': attachment_confidence,
                    'insights': [insight.to_dict() for insight in attachment_insights]
                },
                'defense_mechanisms_analysis': {
                    'detected_mechanisms': [(dm[0].value, dm[1]) for dm in defense_mechanisms],
                    'insights': [insight.to_dict() for insight in defense_insights]
                },
                'comprehensive_profile': comprehensive_profile.to_dict(),
                'analysis_metadata': {
                    'text_length': len(full_text),
                    'confidence_level': big_five_profile.confidence_level,
                    'analysis_date': datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Error in comprehensive personality analysis: {str(e)}")
            return {'error': str(e)}
    
    def get_personality_evolution(self, session_id: str) -> Dict[str, Any]:
        """Obtener evolución de análisis de personalidad a lo largo del tiempo."""
        try:
            # Esta funcionalidad requeriría almacenamiento persistente
            # Por ahora, retornamos análisis actual
            if session_id not in self.conversation_history:
                return {'error': 'No personality data found for session'}
            
            current_analysis = self.analyze_comprehensive_personality("", session_id)
            
            return {
                'session_id': session_id,
                'current_personality_snapshot': current_analysis,
                'evolution_available': False,
                'note': 'Evolution tracking requires persistent storage implementation'
            }
            
        except Exception as e:
            logger.error(f"Error getting personality evolution: {str(e)}")
            return {'error': str(e)}
    
    def reset_session(self, session_id: str):
        """Reiniciar datos de personalidad para sesión."""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]
        logger.info(f"Session {session_id} personality data reset") 
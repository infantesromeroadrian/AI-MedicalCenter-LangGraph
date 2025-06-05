"""
Servicio de mindfulness y técnicas de relajación.
Proporciona ejercicios de respiración, meditaciones personalizadas y técnicas de grounding.
"""

import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from src.models.psychology_models import (
    MindfulnessSession, EmotionalState, EmotionCategory
)

# Configurar logging
logger = logging.getLogger(__name__)


class BreathingPattern(Enum):
    """Patrones de respiración disponibles."""
    BOX_BREATHING = "box_breathing"  # 4-4-4-4
    CALM_BREATHING = "calm_breathing"  # 4-6-8
    ENERGIZING = "energizing"  # 3-1-3-1
    ANXIETY_RELIEF = "anxiety_relief"  # 4-7-8
    COHERENT = "coherent"  # 5-5


class MeditationType(Enum):
    """Tipos de meditación disponibles."""
    BODY_SCAN = "body_scan"
    LOVING_KINDNESS = "loving_kindness"
    MINDFUL_BREATHING = "mindful_breathing"
    PROGRESSIVE_RELAXATION = "progressive_relaxation"
    VISUALIZATION = "visualization"
    AWARENESS = "awareness"


class GroundingTechnique(Enum):
    """Técnicas de grounding para ansiedad."""
    FIVE_SENSES = "five_senses"  # 5-4-3-2-1
    BODY_AWARENESS = "body_awareness"
    COUNTING = "counting"
    OBJECT_FOCUS = "object_focus"
    MOVEMENT = "movement"


class BreathingExerciseGenerator:
    """Generador de ejercicios de respiración personalizados."""
    
    def __init__(self):
        """Inicializar generador de ejercicios de respiración."""
        self.breathing_patterns = self._load_breathing_patterns()
        
    def _load_breathing_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Cargar patrones de respiración con sus características."""
        return {
            BreathingPattern.BOX_BREATHING.value: {
                'name': 'Respiración Cuadrada',
                'pattern': [4, 4, 4, 4],  # inhalar, retener, exhalar, retener
                'description': 'Técnica equilibrante ideal para estrés general',
                'duration_minutes': [3, 5, 8, 10],
                'difficulty': 'beginner',
                'benefits': ['Reduce estrés', 'Mejora concentración', 'Equilibra sistema nervioso'],
                'instructions': [
                    'Siéntate cómodamente con la espalda recta',
                    'Inhala por la nariz contando hasta 4',
                    'Retén el aire contando hasta 4',
                    'Exhala por la boca contando hasta 4',
                    'Mantén pulmones vacíos contando hasta 4',
                    'Repite el ciclo suavemente'
                ]
            },
            BreathingPattern.CALM_BREATHING.value: {
                'name': 'Respiración Calmante',
                'pattern': [4, 6, 8, 0],
                'description': 'Exhalación prolongada para activar respuesta de relajación',
                'duration_minutes': [5, 8, 12],
                'difficulty': 'beginner',
                'benefits': ['Activa sistema parasimpático', 'Reduce ansiedad', 'Mejora sueño'],
                'instructions': [
                    'Encuentra una posición cómoda',
                    'Inhala lentamente por la nariz (4 segundos)',
                    'Pausa suavemente (6 segundos)',
                    'Exhala completamente por la boca (8 segundos)',
                    'Repite con ritmo natural y relajado'
                ]
            },
            BreathingPattern.ANXIETY_RELIEF.value: {
                'name': 'Respiración 4-7-8',
                'pattern': [4, 7, 8, 0],
                'description': 'Técnica específica para crisis de ansiedad',
                'duration_minutes': [3, 5, 8],
                'difficulty': 'intermediate',
                'benefits': ['Alivia ansiedad rápidamente', 'Calma mente', 'Reduce activación'],
                'instructions': [
                    'Exhala completamente para comenzar',
                    'Inhala por la nariz contando hasta 4',
                    'Retén el aire contando hasta 7',
                    'Exhala por la boca contando hasta 8',
                    'Repite 3-4 ciclos inicialmente',
                    'Aumenta gradualmente'
                ]
            },
            BreathingPattern.ENERGIZING.value: {
                'name': 'Respiración Energizante',
                'pattern': [3, 1, 3, 1],
                'description': 'Patrón activante para aumentar alerta y energía',
                'duration_minutes': [2, 3, 5],
                'difficulty': 'intermediate',
                'benefits': ['Aumenta energía', 'Mejora alerta', 'Activa sistema nervioso'],
                'instructions': [
                    'Siéntate erguido y alerta',
                    'Inhala vigorosamente por la nariz (3 segundos)',
                    'Pausa breve (1 segundo)',
                    'Exhala activamente (3 segundos)',
                    'Pausa breve (1 segundo)',
                    'Mantén ritmo activo pero controlado'
                ]
            },
            BreathingPattern.COHERENT.value: {
                'name': 'Respiración Coherente',
                'pattern': [5, 0, 5, 0],
                'description': 'Respiración balanceada para coherencia cardíaca',
                'duration_minutes': [5, 10, 15, 20],
                'difficulty': 'beginner',
                'benefits': ['Mejora variabilidad cardíaca', 'Equilibra emociones', 'Aumenta coherencia'],
                'instructions': [
                    'Respira naturalmente y fluida',
                    'Inhala suavemente por 5 segundos',
                    'Exhala suavemente por 5 segundos',
                    'Sin pausas entre respiraciones',
                    'Mantén ritmo constante y relajado',
                    'Enfócate en el flujo continuo'
                ]
            }
        }
    
    def select_breathing_exercise(self, emotional_state: EmotionalState, 
                                difficulty_preference: str = "beginner") -> Dict[str, Any]:
        """Seleccionar ejercicio de respiración basado en estado emocional."""
        
        # Mapeo de emociones a patrones de respiración recomendados
        emotion_to_pattern = {
            EmotionCategory.ANXIETY: [BreathingPattern.ANXIETY_RELIEF, BreathingPattern.CALM_BREATHING],
            EmotionCategory.ANGER: [BreathingPattern.BOX_BREATHING, BreathingPattern.CALM_BREATHING],
            EmotionCategory.SADNESS: [BreathingPattern.COHERENT, BreathingPattern.ENERGIZING],
            EmotionCategory.FEAR: [BreathingPattern.ANXIETY_RELIEF, BreathingPattern.BOX_BREATHING],
            EmotionCategory.CONTENTMENT: [BreathingPattern.COHERENT, BreathingPattern.BOX_BREATHING]
        }
        
        # Seleccionar patrón basado en emoción primaria
        recommended_patterns = emotion_to_pattern.get(
            emotional_state.primary_emotion, 
            [BreathingPattern.BOX_BREATHING]
        )
        
        # Filtrar por dificultad si es necesario
        suitable_patterns = []
        for pattern in recommended_patterns:
            pattern_data = self.breathing_patterns[pattern.value]
            if pattern_data['difficulty'] == difficulty_preference or difficulty_preference == "any":
                suitable_patterns.append(pattern)
        
        if not suitable_patterns:
            suitable_patterns = recommended_patterns  # Usar todas si no hay match
        
        # Seleccionar patrón (el primero de la lista recomendada)
        selected_pattern = suitable_patterns[0]
        pattern_data = self.breathing_patterns[selected_pattern.value]
        
        # Seleccionar duración basada en intensidad emocional
        if emotional_state.intensity > 80:
            duration = min(pattern_data['duration_minutes'])  # Duración corta para alta intensidad
        elif emotional_state.intensity > 50:
            duration = pattern_data['duration_minutes'][1] if len(pattern_data['duration_minutes']) > 1 else 5
        else:
            duration = max(pattern_data['duration_minutes'])  # Duración larga para baja intensidad
        
        return {
            'pattern': selected_pattern.value,
            'name': pattern_data['name'],
            'description': pattern_data['description'],
            'breathing_sequence': pattern_data['pattern'],
            'duration_minutes': duration,
            'instructions': pattern_data['instructions'],
            'benefits': pattern_data['benefits'],
            'difficulty': pattern_data['difficulty'],
            'personalization_reason': f"Seleccionado para {emotional_state.primary_emotion.value} con intensidad {emotional_state.intensity:.0f}%"
        }
    
    def generate_real_time_guidance(self, pattern: str, duration_minutes: int) -> List[Dict[str, Any]]:
        """Generar guía en tiempo real para ejercicio de respiración."""
        pattern_data = self.breathing_patterns[pattern]
        sequence = pattern_data['pattern']
        
        # Calcular ciclos totales
        cycle_duration = sum(sequence)  # en segundos
        total_cycles = (duration_minutes * 60) // cycle_duration
        
        guidance_steps = []
        
        # Instrucciones iniciales
        guidance_steps.append({
            'type': 'preparation',
            'duration_seconds': 30,
            'instruction': 'Prepárate: encuentra una posición cómoda y relajada',
            'voice_cue': 'Tómate un momento para acomodarte y prepararte para comenzar'
        })
        
        # Generar ciclos de respiración
        for cycle in range(int(total_cycles)):
            cycle_start_time = 30 + (cycle * cycle_duration)
            
            # Inhalación
            if sequence[0] > 0:
                guidance_steps.append({
                    'type': 'inhale',
                    'duration_seconds': sequence[0],
                    'instruction': f'Inhala suavemente por {sequence[0]} segundos',
                    'voice_cue': 'Inhala... 2... 3... 4',
                    'start_time': cycle_start_time
                })
            
            # Retención después de inhalar
            if sequence[1] > 0:
                guidance_steps.append({
                    'type': 'hold_in',
                    'duration_seconds': sequence[1],
                    'instruction': f'Retén el aire por {sequence[1]} segundos',
                    'voice_cue': 'Retén... mantén... suavemente',
                    'start_time': cycle_start_time + sequence[0]
                })
            
            # Exhalación
            if sequence[2] > 0:
                guidance_steps.append({
                    'type': 'exhale',
                    'duration_seconds': sequence[2],
                    'instruction': f'Exhala lentamente por {sequence[2]} segundos',
                    'voice_cue': 'Exhala... libera... relájate',
                    'start_time': cycle_start_time + sequence[0] + sequence[1]
                })
            
            # Retención después de exhalar
            if sequence[3] > 0:
                guidance_steps.append({
                    'type': 'hold_out',
                    'duration_seconds': sequence[3],
                    'instruction': f'Mantén pulmones vacíos por {sequence[3]} segundos',
                    'voice_cue': 'Pausa... quietud... prepárate',
                    'start_time': cycle_start_time + sequence[0] + sequence[1] + sequence[2]
                })
        
        # Instrucciones finales
        guidance_steps.append({
            'type': 'completion',
            'duration_seconds': 30,
            'instruction': 'Respira naturalmente y observa cómo te sientes',
            'voice_cue': 'Excelente. Respira naturalmente y nota los cambios en tu cuerpo'
        })
        
        return guidance_steps


class MeditationGenerator:
    """Generador de meditaciones personalizadas."""
    
    def __init__(self):
        """Inicializar generador de meditaciones."""
        self.meditation_scripts = self._load_meditation_scripts()
    
    def _load_meditation_scripts(self) -> Dict[str, Dict[str, Any]]:
        """Cargar scripts de meditación."""
        return {
            MeditationType.BODY_SCAN.value: {
                'name': 'Exploración Corporal',
                'description': 'Meditación de consciencia corporal progresiva',
                'duration_options': [10, 15, 20, 25],
                'difficulty': 'beginner',
                'benefits': ['Reduce tensión física', 'Aumenta consciencia corporal', 'Calma mente'],
                'script_template': {
                    'introduction': [
                        "Encuentra una posición cómoda, acostado o sentado",
                        "Cierra los ojos suavemente y respira naturalmente",
                        "Vamos a explorar tu cuerpo con gentileza y curiosidad"
                    ],
                    'body_parts': [
                        'dedos de los pies', 'pies', 'pantorrillas', 'rodillas', 'muslos',
                        'caderas', 'abdomen', 'pecho', 'hombros', 'brazos', 'manos',
                        'cuello', 'cara', 'cabeza'
                    ],
                    'transitions': [
                        "Ahora lleva tu atención a {body_part}",
                        "Siente cualquier sensación en {body_part}",
                        "Respira hacia {body_part} y suelta cualquier tensión"
                    ],
                    'conclusion': [
                        "Toma consciencia de tu cuerpo completo",
                        "Siente la relajación que has creado",
                        "Cuando estés listo, abre los ojos suavemente"
                    ]
                }
            },
            MeditationType.LOVING_KINDNESS.value: {
                'name': 'Bondad Amorosa',
                'description': 'Cultivo de compasión hacia uno mismo y otros',
                'duration_options': [10, 15, 20],
                'difficulty': 'intermediate',
                'benefits': ['Aumenta autocompasión', 'Mejora relaciones', 'Reduce autocrítica'],
                'script_template': {
                    'introduction': [
                        "Siéntate cómodamente con el corazón abierto",
                        "Respira con gentileza y conecta con tu bondad natural",
                        "Vamos a cultivar amor bondadoso hacia ti y otros"
                    ],
                    'phrases': [
                        "Que pueda ser feliz",
                        "Que pueda estar en paz",
                        "Que pueda estar libre de sufrimiento",
                        "Que pueda vivir con facilidad"
                    ],
                    'targets': ['ti mismo', 'alguien querido', 'persona neutral', 'persona difícil', 'todos los seres'],
                    'conclusion': [
                        "Siente el calor de la bondad en tu corazón",
                        "Esta bondad está siempre disponible para ti",
                        "Lleva esta energía amorosa contigo"
                    ]
                }
            },
            MeditationType.PROGRESSIVE_RELAXATION.value: {
                'name': 'Relajación Progresiva',
                'description': 'Tensión y relajación sistemática de grupos musculares',
                'duration_options': [15, 20, 25],
                'difficulty': 'beginner',
                'benefits': ['Libera tensión muscular', 'Enseña diferencia tensión/relajación', 'Calma sistema nervioso'],
                'script_template': {
                    'introduction': [
                        "Acuéstate cómodamente y cierra los ojos",
                        "Vamos a tensar y relajar diferentes grupos musculares",
                        "Esto te ayudará a liberar tensión acumulada"
                    ],
                    'muscle_groups': [
                        'pies y pantorrillas', 'muslos y glúteos', 'abdomen',
                        'manos y brazos', 'hombros y cuello', 'cara'
                    ],
                    'instructions': [
                        "Tensa {muscle_group} por 5 segundos",
                        "Ahora relaja completamente {muscle_group}",
                        "Siente la diferencia entre tensión y relajación"
                    ],
                    'conclusion': [
                        "Todo tu cuerpo está profundamente relajado",
                        "Disfruta esta sensación de calma completa",
                        "Recuerda esta sensación para el futuro"
                    ]
                }
            }
        }
    
    def create_personalized_meditation(self, emotional_state: EmotionalState, 
                                     duration_minutes: int = 15,
                                     meditation_type: Optional[str] = None) -> Dict[str, Any]:
        """Crear meditación personalizada basada en estado emocional."""
        
        # Seleccionar tipo de meditación si no se especifica
        if meditation_type is None:
            emotion_to_meditation = {
                EmotionCategory.ANXIETY: MeditationType.BODY_SCAN,
                EmotionCategory.ANGER: MeditationType.PROGRESSIVE_RELAXATION,
                EmotionCategory.SADNESS: MeditationType.LOVING_KINDNESS,
                EmotionCategory.FEAR: MeditationType.BODY_SCAN,
                EmotionCategory.CONTENTMENT: MeditationType.LOVING_KINDNESS
            }
            meditation_type = emotion_to_meditation.get(
                emotional_state.primary_emotion,
                MeditationType.BODY_SCAN
            ).value
        
        meditation_data = self.meditation_scripts[meditation_type]
        
        # Generar script personalizado
        script = self._generate_meditation_script(meditation_data, duration_minutes, emotional_state)
        
        return {
            'type': meditation_type,
            'name': meditation_data['name'],
            'description': meditation_data['description'],
            'duration_minutes': duration_minutes,
            'script': script,
            'benefits': meditation_data['benefits'],
            'difficulty': meditation_data['difficulty'],
            'personalization_note': f"Adaptada para {emotional_state.primary_emotion.value}"
        }
    
    def _generate_meditation_script(self, meditation_data: Dict, duration: int, 
                                  emotional_state: EmotionalState) -> List[Dict[str, Any]]:
        """Generar script detallado de meditación."""
        script_steps = []
        
        # Introducción (2 minutos)
        for i, intro_line in enumerate(meditation_data['script_template']['introduction']):
            script_steps.append({
                'phase': 'introduction',
                'timing_seconds': 30 + (i * 20),
                'instruction': intro_line,
                'voice_tone': 'calm_welcoming'
            })
        
        # Cuerpo principal de la meditación
        main_duration = duration - 4  # Reservar tiempo para intro y conclusión
        
        if meditation_data['name'] == 'Exploración Corporal':
            script_steps.extend(self._generate_body_scan_script(meditation_data, main_duration))
        elif meditation_data['name'] == 'Bondad Amorosa':
            script_steps.extend(self._generate_loving_kindness_script(meditation_data, main_duration))
        elif meditation_data['name'] == 'Relajación Progresiva':
            script_steps.extend(self._generate_progressive_relaxation_script(meditation_data, main_duration))
        
        # Conclusión (2 minutos)
        conclusion_start = (duration - 2) * 60
        for i, conclusion_line in enumerate(meditation_data['script_template']['conclusion']):
            script_steps.append({
                'phase': 'conclusion',
                'timing_seconds': conclusion_start + (i * 20),
                'instruction': conclusion_line,
                'voice_tone': 'warm_closing'
            })
        
        return script_steps
    
    def _generate_body_scan_script(self, meditation_data: Dict, duration_minutes: int) -> List[Dict[str, Any]]:
        """Generar script específico para body scan."""
        steps = []
        body_parts = meditation_data['script_template']['body_parts']
        time_per_part = (duration_minutes * 60) // len(body_parts)
        
        for i, body_part in enumerate(body_parts):
            steps.append({
                'phase': 'body_scan',
                'timing_seconds': 120 + (i * time_per_part),  # Empezar después de intro
                'instruction': f"Lleva tu atención a {body_part}. Siente cualquier sensación presente, sin juzgar.",
                'voice_tone': 'gentle_guiding',
                'focus_area': body_part
            })
        
        return steps
    
    def _generate_loving_kindness_script(self, meditation_data: Dict, duration_minutes: int) -> List[Dict[str, Any]]:
        """Generar script específico para loving kindness."""
        steps = []
        targets = meditation_data['script_template']['targets']
        phrases = meditation_data['script_template']['phrases']
        time_per_target = (duration_minutes * 60) // len(targets)
        
        for i, target in enumerate(targets):
            for j, phrase in enumerate(phrases):
                steps.append({
                    'phase': 'loving_kindness',
                    'timing_seconds': 120 + (i * time_per_target) + (j * 15),
                    'instruction': f"Dirigiéndote a {target}, repite mentalmente: {phrase}",
                    'voice_tone': 'warm_compassionate',
                    'target': target,
                    'phrase': phrase
                })
        
        return steps
    
    def _generate_progressive_relaxation_script(self, meditation_data: Dict, duration_minutes: int) -> List[Dict[str, Any]]:
        """Generar script específico para relajación progresiva."""
        steps = []
        muscle_groups = meditation_data['script_template']['muscle_groups']
        time_per_group = (duration_minutes * 60) // len(muscle_groups)
        
        for i, muscle_group in enumerate(muscle_groups):
            base_time = 120 + (i * time_per_group)
            
            # Tensión
            steps.append({
                'phase': 'tension',
                'timing_seconds': base_time,
                'instruction': f"Tensa {muscle_group} fuertemente por 5 segundos",
                'voice_tone': 'directive_clear',
                'muscle_group': muscle_group,
                'action': 'tense'
            })
            
            # Relajación
            steps.append({
                'phase': 'relaxation',
                'timing_seconds': base_time + 10,
                'instruction': f"Relaja completamente {muscle_group}. Siente la diferencia",
                'voice_tone': 'soothing_release',
                'muscle_group': muscle_group,
                'action': 'release'
            })
        
        return steps


class GroundingTechniqueGenerator:
    """Generador de técnicas de grounding para manejo de ansiedad."""
    
    def __init__(self):
        """Inicializar generador de técnicas de grounding."""
        self.grounding_techniques = self._load_grounding_techniques()
    
    def _load_grounding_techniques(self) -> Dict[str, Dict[str, Any]]:
        """Cargar técnicas de grounding."""
        return {
            GroundingTechnique.FIVE_SENSES.value: {
                'name': 'Técnica 5-4-3-2-1',
                'description': 'Conecta con tus 5 sentidos para volver al presente',
                'duration_minutes': [3, 5],
                'urgency_level': 'high',  # Para crisis de ansiedad
                'steps': [
                    {'sense': 'vista', 'count': 5, 'instruction': 'Nombra 5 cosas que puedes VER a tu alrededor'},
                    {'sense': 'tacto', 'count': 4, 'instruction': 'Identifica 4 cosas que puedes TOCAR'},
                    {'sense': 'oído', 'count': 3, 'instruction': 'Escucha 3 SONIDOS diferentes'},
                    {'sense': 'olfato', 'count': 2, 'instruction': 'Detecta 2 OLORES en el ambiente'},
                    {'sense': 'gusto', 'count': 1, 'instruction': 'Nota 1 SABOR en tu boca'}
                ]
            },
            GroundingTechnique.BODY_AWARENESS.value: {
                'name': 'Consciencia Corporal de Emergencia',
                'description': 'Técnica rápida de conexión con el cuerpo',
                'duration_minutes': [2, 3],
                'urgency_level': 'high',
                'steps': [
                    {'action': 'feet', 'instruction': 'Siente tus pies en el suelo firmemente'},
                    {'action': 'breathing', 'instruction': 'Nota tu respiración natural sin cambiarla'},
                    {'action': 'hands', 'instruction': 'Aprieta y suelta tus puños 3 veces'},
                    {'action': 'posture', 'instruction': 'Ajusta tu postura para sentirte estable'},
                    {'action': 'temperature', 'instruction': 'Nota la temperatura en tu piel'}
                ]
            },
            GroundingTechnique.COUNTING.value: {
                'name': 'Conteo Tranquilizador',
                'description': 'Ejercicios de conteo para calmar la mente',
                'duration_minutes': [3, 5, 8],
                'urgency_level': 'medium',
                'variations': [
                    {'type': 'backwards', 'instruction': 'Cuenta hacia atrás desde 100 de 7 en 7'},
                    {'type': 'categories', 'instruction': 'Nombra 10 animales, luego 10 países, luego 10 comidas'},
                    {'type': 'colors', 'instruction': 'Encuentra 1 objeto rojo, 2 azules, 3 verdes...'},
                    {'type': 'alphabet', 'instruction': 'Por cada letra del alfabeto, nombra una ciudad'}
                ]
            },
            GroundingTechnique.OBJECT_FOCUS.value: {
                'name': 'Enfoque en Objeto',
                'description': 'Concentración intensa en un objeto para anclar atención',
                'duration_minutes': [3, 5],
                'urgency_level': 'medium',
                'steps': [
                    {'phase': 'selection', 'instruction': 'Elige un objeto pequeño que puedas sostener'},
                    {'phase': 'visual', 'instruction': 'Examina cada detalle visual: color, forma, textura'},
                    {'phase': 'tactile', 'instruction': 'Explora con tus dedos: peso, temperatura, superficie'},
                    {'phase': 'description', 'instruction': 'Describe mentalmente cada característica'},
                    {'phase': 'appreciation', 'instruction': 'Aprecia la existencia de este objeto'}
                ]
            }
        }
    
    def select_grounding_technique(self, emotional_state: EmotionalState, 
                                 urgency_level: str = "medium") -> Dict[str, Any]:
        """Seleccionar técnica de grounding apropiada."""
        
        # Filtrar técnicas por nivel de urgencia
        suitable_techniques = []
        for technique_key, technique_data in self.grounding_techniques.items():
            if technique_data.get('urgency_level', 'medium') == urgency_level:
                suitable_techniques.append((technique_key, technique_data))
        
        if not suitable_techniques:
            # Si no hay match, usar cualquier técnica
            suitable_techniques = list(self.grounding_techniques.items())
        
        # Para alta intensidad emocional, preferir técnicas de alta urgencia
        if emotional_state.intensity > 80:
            high_urgency = [(k, v) for k, v in suitable_techniques if v.get('urgency_level') == 'high']
            if high_urgency:
                suitable_techniques = high_urgency
        
        # Seleccionar la primera técnica adecuada
        selected_key, selected_data = suitable_techniques[0]
        
        # Personalizar duración
        if emotional_state.intensity > 70:
            duration = min(selected_data['duration_minutes'])
        else:
            duration = max(selected_data['duration_minutes'])
        
        return {
            'technique': selected_key,
            'name': selected_data['name'],
            'description': selected_data['description'],
            'duration_minutes': duration,
            'instructions': self._generate_grounding_instructions(selected_key, selected_data),
            'urgency_level': selected_data['urgency_level'],
            'personalization_reason': f"Seleccionada para intensidad {emotional_state.intensity:.0f}%"
        }
    
    def _generate_grounding_instructions(self, technique_key: str, technique_data: Dict) -> List[Dict[str, Any]]:
        """Generar instrucciones paso a paso para técnica de grounding."""
        instructions = []
        
        if 'steps' in technique_data:
            for i, step in enumerate(technique_data['steps']):
                instructions.append({
                    'step_number': i + 1,
                    'timing_seconds': 30 + (i * 20),
                    'instruction': step['instruction'],
                    'type': 'sequential_step'
                })
        
        elif 'variations' in technique_data:
            # Para técnicas de conteo con variaciones
            instructions.append({
                'step_number': 1,
                'timing_seconds': 30,
                'instruction': "Elige una variación de conteo que te resulte cómoda",
                'type': 'selection'
            })
            
            for i, variation in enumerate(technique_data['variations']):
                instructions.append({
                    'step_number': i + 2,
                    'timing_seconds': 60 + (i * 60),
                    'instruction': variation['instruction'],
                    'type': 'counting_variation',
                    'variation_type': variation['type']
                })
        
        return instructions


class MindfulnessService:
    """Servicio principal de mindfulness y técnicas de relajación."""
    
    def __init__(self):
        """Inicializar servicio de mindfulness."""
        self.breathing_generator = BreathingExerciseGenerator()
        self.meditation_generator = MeditationGenerator()
        self.grounding_generator = GroundingTechniqueGenerator()
        self.active_sessions = {}
        
    def start_breathing_session(self, session_id: str, emotional_state: EmotionalState, 
                               difficulty: str = "beginner") -> Dict[str, Any]:
        """Iniciar sesión de ejercicio de respiración."""
        try:
            # Seleccionar ejercicio personalizado
            exercise = self.breathing_generator.select_breathing_exercise(emotional_state, difficulty)
            
            # Generar guía en tiempo real
            guidance = self.breathing_generator.generate_real_time_guidance(
                exercise['pattern'], 
                exercise['duration_minutes']
            )
            
            # Crear sesión de mindfulness
            mindfulness_session = MindfulnessSession(
                session_id=session_id,
                technique_type="breathing",
                duration_minutes=exercise['duration_minutes'],
                difficulty_level=difficulty,
                emotional_state_before=emotional_state
            )
            
            # Almacenar sesión activa
            self.active_sessions[session_id] = {
                'type': 'breathing',
                'session': mindfulness_session,
                'exercise_data': exercise,
                'guidance': guidance,
                'start_time': datetime.now()
            }
            
            return {
                'session_id': session_id,
                'exercise': exercise,
                'real_time_guidance': guidance,
                'session_data': mindfulness_session.to_dict(),
                'status': 'started'
            }
            
        except Exception as e:
            logger.error(f"Error starting breathing session: {str(e)}")
            return {'error': str(e)}
    
    def start_meditation_session(self, session_id: str, emotional_state: EmotionalState,
                                duration_minutes: int = 15, meditation_type: Optional[str] = None) -> Dict[str, Any]:
        """Iniciar sesión de meditación personalizada."""
        try:
            # Crear meditación personalizada
            meditation = self.meditation_generator.create_personalized_meditation(
                emotional_state, duration_minutes, meditation_type
            )
            
            # Crear sesión de mindfulness
            mindfulness_session = MindfulnessSession(
                session_id=session_id,
                technique_type="meditation",
                duration_minutes=duration_minutes,
                difficulty_level=meditation['difficulty'],
                emotional_state_before=emotional_state
            )
            
            # Almacenar sesión activa
            self.active_sessions[session_id] = {
                'type': 'meditation',
                'session': mindfulness_session,
                'meditation_data': meditation,
                'start_time': datetime.now()
            }
            
            return {
                'session_id': session_id,
                'meditation': meditation,
                'session_data': mindfulness_session.to_dict(),
                'status': 'started'
            }
            
        except Exception as e:
            logger.error(f"Error starting meditation session: {str(e)}")
            return {'error': str(e)}
    
    def start_grounding_session(self, session_id: str, emotional_state: EmotionalState,
                              urgency_level: str = "medium") -> Dict[str, Any]:
        """Iniciar sesión de técnica de grounding."""
        try:
            # Seleccionar técnica de grounding
            technique = self.grounding_generator.select_grounding_technique(
                emotional_state, urgency_level
            )
            
            # Crear sesión de mindfulness
            mindfulness_session = MindfulnessSession(
                session_id=session_id,
                technique_type="grounding",
                duration_minutes=technique['duration_minutes'],
                difficulty_level="beginner",  # Las técnicas de grounding son generalmente básicas
                emotional_state_before=emotional_state
            )
            
            # Almacenar sesión activa
            self.active_sessions[session_id] = {
                'type': 'grounding',
                'session': mindfulness_session,
                'technique_data': technique,
                'start_time': datetime.now()
            }
            
            return {
                'session_id': session_id,
                'technique': technique,
                'session_data': mindfulness_session.to_dict(),
                'status': 'started'
            }
            
        except Exception as e:
            logger.error(f"Error starting grounding session: {str(e)}")
            return {'error': str(e)}
    
    def complete_mindfulness_session(self, session_id: str, 
                                   emotional_state_after: EmotionalState,
                                   completion_rate: float = 100.0,
                                   user_rating: Optional[int] = None) -> Dict[str, Any]:
        """Completar sesión de mindfulness y registrar resultados."""
        try:
            if session_id not in self.active_sessions:
                return {'error': 'Session not found'}
            
            session_data = self.active_sessions[session_id]
            mindfulness_session = session_data['session']
            
            # Actualizar sesión con datos de finalización
            mindfulness_session.emotional_state_after = emotional_state_after
            mindfulness_session.completion_rate = completion_rate
            mindfulness_session.user_rating = user_rating
            mindfulness_session.completed_at = datetime.now()
            
            # Calcular mejora emocional
            emotional_improvement = self._calculate_emotional_improvement(
                mindfulness_session.emotional_state_before,
                emotional_state_after
            )
            
            # Remover de sesiones activas
            completed_session = self.active_sessions.pop(session_id)
            
            return {
                'session_id': session_id,
                'completed_session': mindfulness_session.to_dict(),
                'emotional_improvement': emotional_improvement,
                'session_summary': {
                    'technique_type': mindfulness_session.technique_type,
                    'duration_minutes': mindfulness_session.duration_minutes,
                    'completion_rate': completion_rate,
                    'user_rating': user_rating,
                    'effectiveness': emotional_improvement['effectiveness_score']
                },
                'status': 'completed'
            }
            
        except Exception as e:
            logger.error(f"Error completing mindfulness session: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_emotional_improvement(self, before: EmotionalState, after: EmotionalState) -> Dict[str, Any]:
        """Calcular mejora emocional entre estados antes y después."""
        
        # Calcular cambios en métricas clave
        valence_improvement = after.valence - before.valence
        intensity_change = before.intensity - after.intensity  # Reducción de intensidad es positiva
        
        # Calcular score de efectividad (0-100)
        effectiveness_score = 0
        
        # Bonificación por mejora en valencia (más positivo)
        if valence_improvement > 0:
            effectiveness_score += min(30, valence_improvement * 0.5)
        
        # Bonificación por reducción de intensidad (para emociones negativas)
        if before.valence < 0 and intensity_change > 0:
            effectiveness_score += min(40, intensity_change * 0.8)
        
        # Bonificación por cambio de emoción primaria a más positiva
        emotion_hierarchy = {
            EmotionCategory.JOY: 5,
            EmotionCategory.CONTENTMENT: 4,
            EmotionCategory.EXCITEMENT: 3,
            EmotionCategory.CONFUSION: 2,
            EmotionCategory.SADNESS: 1,
            EmotionCategory.ANXIETY: 0,
            EmotionCategory.ANGER: 0,
            EmotionCategory.FEAR: 0
        }
        
        before_score = emotion_hierarchy.get(before.primary_emotion, 2)
        after_score = emotion_hierarchy.get(after.primary_emotion, 2)
        
        if after_score > before_score:
            effectiveness_score += 30
        
        effectiveness_score = min(100, max(0, effectiveness_score))
        
        return {
            'valence_change': valence_improvement,
            'intensity_change': -intensity_change,  # Mostrar como reducción positiva
            'emotion_before': before.primary_emotion.value,
            'emotion_after': after.primary_emotion.value,
            'effectiveness_score': effectiveness_score,
            'improvement_level': (
                'significant' if effectiveness_score > 70 else
                'moderate' if effectiveness_score > 40 else
                'mild' if effectiveness_score > 20 else
                'minimal'
            )
        }
    
    def get_personalized_recommendations(self, emotional_state: EmotionalState) -> Dict[str, Any]:
        """Obtener recomendaciones personalizadas de técnicas."""
        try:
            recommendations = {
                'breathing_exercises': [],
                'meditations': [],
                'grounding_techniques': []
            }
            
            # Recomendaciones de respiración
            for difficulty in ['beginner', 'intermediate']:
                breathing_rec = self.breathing_generator.select_breathing_exercise(
                    emotional_state, difficulty
                )
                recommendations['breathing_exercises'].append(breathing_rec)
            
            # Recomendaciones de meditación
            for med_type in ['body_scan', 'loving_kindness', 'progressive_relaxation']:
                try:
                    meditation_rec = self.meditation_generator.create_personalized_meditation(
                        emotional_state, 15, med_type
                    )
                    recommendations['meditations'].append(meditation_rec)
                except:
                    continue  # Skip si el tipo no está disponible
            
            # Recomendaciones de grounding
            for urgency in ['medium', 'high']:
                grounding_rec = self.grounding_generator.select_grounding_technique(
                    emotional_state, urgency
                )
                recommendations['grounding_techniques'].append(grounding_rec)
            
            return {
                'emotional_state': emotional_state.to_dict(),
                'recommendations': recommendations,
                'priority_suggestion': self._get_priority_suggestion(emotional_state),
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return {'error': str(e)}
    
    def _get_priority_suggestion(self, emotional_state: EmotionalState) -> Dict[str, Any]:
        """Obtener sugerencia prioritaria basada en estado emocional."""
        
        if emotional_state.intensity > 80:
            return {
                'technique': 'grounding',
                'reason': 'Alta intensidad emocional requiere técnica de grounding inmediata',
                'urgency': 'high'
            }
        elif emotional_state.primary_emotion in [EmotionCategory.ANXIETY, EmotionCategory.FEAR]:
            return {
                'technique': 'breathing',
                'reason': 'Ansiedad/miedo responden bien a ejercicios de respiración',
                'urgency': 'medium'
            }
        elif emotional_state.valence < -30:
            return {
                'technique': 'meditation',
                'reason': 'Estado emocional negativo se beneficia de meditación',
                'urgency': 'medium'
            }
        else:
            return {
                'technique': 'breathing',
                'reason': 'Ejercicio de respiración para mantener bienestar',
                'urgency': 'low'
            } 
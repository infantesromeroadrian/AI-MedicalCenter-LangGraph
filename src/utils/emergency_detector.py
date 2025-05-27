"""
Sistema avanzado de detección de emergencias médicas con múltiples criterios.
"""
import re
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class UrgencyLevel(Enum):
    """Niveles de urgencia médica."""
    CRITICAL = 5  # Emergencia crítica - requiere atención inmediata
    HIGH = 4      # Urgencia alta - atención en minutos
    MODERATE = 3  # Urgencia moderada - atención en horas
    LOW = 2       # Urgencia baja - atención en 24h
    ROUTINE = 1   # Rutina - consulta programada

@dataclass
class EmergencySignal:
    """Señal de emergencia detectada."""
    type: str
    description: str
    severity_score: float  # 0-1
    keywords_matched: List[str]
    urgency_level: UrgencyLevel
    recommendation: str

@dataclass
class EmergencyAssessment:
    """Evaluación completa de emergencia."""
    is_emergency: bool
    urgency_level: UrgencyLevel
    overall_score: float  # 0-1
    signals: List[EmergencySignal]
    primary_concern: str
    recommendation: str
    time_sensitivity: str
    action_required: str

class AdvancedEmergencyDetector:
    """Detector avanzado de emergencias médicas."""
    
    def __init__(self):
        """Inicializar el detector de emergencias."""
        self._init_emergency_patterns()
        self._init_age_modifiers()
        self._init_combination_rules()
    
    def _init_emergency_patterns(self):
        """Inicializar patrones de emergencia por categorías."""
        
        # EMERGENCIAS CRÍTICAS (Nivel 5)
        self.critical_patterns = {
            'cardiac_arrest': {
                'keywords': [
                    'paro cardíaco', 'paro cardiaco', 'no respira', 'sin pulso',
                    'cardiac arrest', 'no pulse', 'unconscious', 'inconsciente',
                    'desmayado', 'colapso', 'collapse'
                ],
                'score': 1.0,
                'description': 'Posible paro cardiorrespiratorio',
                'recommendation': '🚨 LLAME AL 911 INMEDIATAMENTE - Inicie RCP si está capacitado'
            },
            'severe_trauma': {
                'keywords': [
                    'accidente grave', 'traumatismo severo', 'hueso expuesto',
                    'sangrado profuso', 'hemorragia masiva', 'atropello',
                    'severe trauma', 'massive bleeding', 'exposed bone'
                ],
                'score': 1.0,
                'description': 'Trauma severo con riesgo vital',
                'recommendation': '🚨 EMERGENCIA - Llame ambulancia AHORA, no mueva al paciente'
            },
            'stroke_signs': {
                'keywords': [
                    'no puede hablar', 'cara colgada', 'brazo débil', 'parálisis facial',
                    'habla arrastrada', 'confusión súbita', 'pérdida visión súbita',
                    'stroke', 'facial drooping', 'slurred speech', 'sudden confusion'
                ],
                'score': 0.95,
                'description': 'Signos de accidente cerebrovascular',
                'recommendation': '🚨 CÓDIGO ICTUS - Transporte inmediato a hospital'
            },
            'severe_allergic': {
                'keywords': [
                    'dificultad respirar alergia', 'hinchazón cara', 'anafilaxia',
                    'urticaria generalizada', 'broncoespasmo severo',
                    'anaphylaxis', 'severe allergic reaction', 'facial swelling'
                ],
                'score': 0.95,
                'description': 'Reacción alérgica severa',
                'recommendation': '🚨 ANAFILAXIA - Administre epinefrina si disponible, llame 911'
            }
        }
        
        # EMERGENCIAS ALTAS (Nivel 4) 
        self.high_urgency_patterns = {
            'chest_pain_severe': {
                'keywords': [
                    'dolor pecho intenso', 'opresión pecho fuerte', 'dolor irradia brazo',
                    'sudoración dolor pecho', 'náuseas dolor pecho',
                    'severe chest pain', 'crushing chest pain', 'radiating arm pain'
                ],
                'score': 0.9,
                'description': 'Dolor torácico sugestivo de síndrome coronario agudo',
                'recommendation': '🔴 Acuda a urgencias INMEDIATAMENTE - Posible infarto'
            },
            'respiratory_distress': {
                'keywords': [
                    'dificultad respirar severa', 'ahogo', 'no puede respirar',
                    'cianosis', 'labios azules', 'severe shortness breath',
                    'gasping', 'unable to breathe', 'blue lips'
                ],
                'score': 0.9,
                'description': 'Insuficiencia respiratoria severa',
                'recommendation': '🔴 URGENTE - Traslade a emergencias, mantenga vía aérea'
            },
            'altered_consciousness': {
                'keywords': [
                    'convulsiones', 'crisis epiléptica', 'alteración conciencia',
                    'desorientado severo', 'alucinaciones agudas',
                    'seizures', 'altered mental status', 'severe confusion'
                ],
                'score': 0.85,
                'description': 'Alteración del estado de conciencia',
                'recommendation': '🔴 Requiere evaluación urgente en hospital'
            },
            'severe_pain': {
                'keywords': [
                    'dolor insoportable', 'dolor 10/10', 'agonizante',
                    'dolor peor vida', 'excruciating pain', 'unbearable pain',
                    'worst pain ever'
                ],
                'score': 0.8,
                'description': 'Dolor severo que requiere atención urgente',
                'recommendation': '🔴 Dolor severo - Evaluación médica urgente necesaria'
            }
        }
        
        # EMERGENCIAS MODERADAS (Nivel 3)
        self.moderate_urgency_patterns = {
            'abdominal_pain': {
                'keywords': [
                    'dolor abdominal intenso', 'vómitos persistentes',
                    'fiebre alta dolor abdomen', 'rigidez abdominal',
                    'severe abdominal pain', 'persistent vomiting'
                ],
                'score': 0.7,
                'description': 'Dolor abdominal que puede requerir cirugía',
                'recommendation': '🟡 Evaluación en urgencias en las próximas horas'
            },
            'high_fever': {
                'keywords': [
                    'fiebre muy alta', 'temperatura 39', 'temperatura 40',
                    'fiebre rigidez cuello', 'high fever', 'fever 39', 'fever 40'
                ],
                'score': 0.65,
                'description': 'Fiebre alta que requiere evaluación',
                'recommendation': '🟡 Consulte médico si fiebre persiste o empeora'
            },
            'pregnancy_emergency': {
                'keywords': [
                    'embarazada sangrado', 'contracciones prematuras',
                    'dolor intenso embarazo', 'pregnant bleeding',
                    'premature contractions', 'severe pregnancy pain'
                ],
                'score': 0.8,
                'description': 'Emergencia obstétrica potencial',
                'recommendation': '🔴 Consulta obstétrica urgente requerida'
            }
        }
        
        # SÍNTOMAS DE ALERTA ESPECÍFICOS
        self.warning_symptoms = {
            'neurological': [
                'dolor cabeza súbito', 'cefalea explosiva', 'peor dolor cabeza vida',
                'sudden severe headache', 'thunderclap headache'
            ],
            'cardiac': [
                'palpitaciones severas', 'desmayo', 'mareo intenso',
                'severe palpitations', 'fainting', 'syncope'
            ],
            'respiratory': [
                'tos sangre', 'hemoptisis', 'dolor respirar',
                'coughing blood', 'hemoptysis', 'pain breathing'
            ],
            'gastrointestinal': [
                'vómito sangre', 'heces negras', 'sangre heces',
                'vomiting blood', 'black stools', 'blood in stool'
            ]
        }
    
    def _init_age_modifiers(self):
        """Modificadores de urgencia basados en edad."""
        self.age_modifiers = {
            'infant': {  # 0-2 años
                'patterns': ['bebé', 'lactante', 'meses', 'infant', 'baby'],
                'multiplier': 1.3,
                'special_concerns': ['fiebre en menor 3 meses', 'dificultad alimentación']
            },
            'child': {  # 2-12 años
                'patterns': ['niño', 'años', 'child', 'kid'],
                'multiplier': 1.2,
                'special_concerns': ['deshidratación', 'fiebre alta']
            },
            'elderly': {  # >65 años
                'patterns': ['anciano', 'adulto mayor', 'elderly', '65 años', '70 años'],
                'multiplier': 1.2,
                'special_concerns': ['caídas', 'confusión', 'medicamentos']
            }
        }
    
    def _init_combination_rules(self):
        """Reglas para combinaciones de síntomas."""
        self.symptom_combinations = {
            'heart_attack_cluster': {
                'symptoms': ['dolor pecho', 'sudoración', 'náuseas', 'dolor brazo'],
                'threshold': 2,  # Al menos 2 síntomas
                'score_bonus': 0.3,
                'urgency_boost': 1
            },
            'sepsis_cluster': {
                'symptoms': ['fiebre', 'confusión', 'taquicardia', 'hipotensión'],
                'threshold': 2,
                'score_bonus': 0.4,
                'urgency_boost': 2
            },
            'meningitis_cluster': {
                'symptoms': ['fiebre', 'rigidez cuello', 'dolor cabeza', 'fotofobia'],
                'threshold': 2,
                'score_bonus': 0.5,
                'urgency_boost': 2
            }
        }
    
    def detect_emergency(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> EmergencyAssessment:
        """
        Detectar emergencias médicas en una consulta.
        
        Args:
            query: Consulta del paciente
            context: Contexto adicional (edad, historial, etc.)
            
        Returns:
            EmergencyAssessment: Evaluación completa de emergencia
        """
        try:
            # Normalizar texto
            normalized_query = query.lower().strip()
            
            # Detectar señales de emergencia
            signals = self._detect_emergency_signals(normalized_query, context)
            
            # Aplicar modificadores contextuales
            signals = self._apply_contextual_modifiers(signals, normalized_query, context)
            
            # Detectar combinaciones de síntomas
            combination_signals = self._detect_symptom_combinations(normalized_query)
            signals.extend(combination_signals)
            
            # Calcular score general y nivel de urgencia
            overall_score, urgency_level = self._calculate_overall_urgency(signals)
            
            # Determinar si es emergencia
            is_emergency = urgency_level.value >= UrgencyLevel.MODERATE.value
            
            # Generar recomendación principal
            primary_concern, recommendation, time_sensitivity, action_required = \
                self._generate_assessment_details(signals, urgency_level)
            
            return EmergencyAssessment(
                is_emergency=is_emergency,
                urgency_level=urgency_level,
                overall_score=overall_score,
                signals=signals,
                primary_concern=primary_concern,
                recommendation=recommendation,
                time_sensitivity=time_sensitivity,
                action_required=action_required
            )
            
        except Exception as e:
            logger.error(f"Error en detección de emergencias: {e}")
            # Fallback conservador
            return EmergencyAssessment(
                is_emergency=False,
                urgency_level=UrgencyLevel.ROUTINE,
                overall_score=0.0,
                signals=[],
                primary_concern="Error en evaluación",
                recommendation="Consulte con un profesional médico si tiene dudas",
                time_sensitivity="No determinado",
                action_required="Consulta médica de rutina"
            )
    
    def _detect_emergency_signals(
        self, 
        query: str, 
        context: Optional[Dict[str, Any]]
    ) -> List[EmergencySignal]:
        """Detectar señales de emergencia en el texto."""
        signals = []
        
        # Buscar patrones críticos
        for pattern_name, pattern_data in self.critical_patterns.items():
            matched_keywords = self._find_matching_keywords(query, pattern_data['keywords'])
            if matched_keywords:
                signals.append(EmergencySignal(
                    type='critical',
                    description=pattern_data['description'],
                    severity_score=pattern_data['score'],
                    keywords_matched=matched_keywords,
                    urgency_level=UrgencyLevel.CRITICAL,
                    recommendation=pattern_data['recommendation']
                ))
        
        # Buscar patrones de alta urgencia
        for pattern_name, pattern_data in self.high_urgency_patterns.items():
            matched_keywords = self._find_matching_keywords(query, pattern_data['keywords'])
            if matched_keywords:
                signals.append(EmergencySignal(
                    type='high_urgency',
                    description=pattern_data['description'],
                    severity_score=pattern_data['score'],
                    keywords_matched=matched_keywords,
                    urgency_level=UrgencyLevel.HIGH,
                    recommendation=pattern_data['recommendation']
                ))
        
        # Buscar patrones de urgencia moderada
        for pattern_name, pattern_data in self.moderate_urgency_patterns.items():
            matched_keywords = self._find_matching_keywords(query, pattern_data['keywords'])
            if matched_keywords:
                signals.append(EmergencySignal(
                    type='moderate_urgency',
                    description=pattern_data['description'],
                    severity_score=pattern_data['score'],
                    keywords_matched=matched_keywords,
                    urgency_level=UrgencyLevel.MODERATE,
                    recommendation=pattern_data['recommendation']
                ))
        
        # Buscar síntomas de alerta específicos
        for category, symptoms in self.warning_symptoms.items():
            matched_keywords = self._find_matching_keywords(query, symptoms)
            if matched_keywords:
                signals.append(EmergencySignal(
                    type='warning_symptom',
                    description=f'Síntoma de alerta {category}',
                    severity_score=0.6,
                    keywords_matched=matched_keywords,
                    urgency_level=UrgencyLevel.MODERATE,
                    recommendation=f'Evaluación médica recomendada para síntomas {category}'
                ))
        
        return signals
    
    def _apply_contextual_modifiers(
        self, 
        signals: List[EmergencySignal], 
        query: str, 
        context: Optional[Dict[str, Any]]
    ) -> List[EmergencySignal]:
        """Aplicar modificadores contextuales basados en edad, etc."""
        
        # Detectar grupo de edad
        age_group = self._detect_age_group(query, context)
        
        if age_group:
            age_data = self.age_modifiers[age_group]
            multiplier = age_data['multiplier']
            
            # Aplicar multiplicador de urgencia
            for signal in signals:
                signal.severity_score = min(1.0, signal.severity_score * multiplier)
                
                # Verificar concerns especiales para edad
                special_concerns = age_data['special_concerns']
                for concern in special_concerns:
                    if any(keyword in query for keyword in concern.split()):
                        # Aumentar urgencia para concerns específicos de edad
                        if signal.urgency_level.value < UrgencyLevel.HIGH.value:
                            signal.urgency_level = UrgencyLevel.HIGH
                            signal.recommendation = f"🔴 URGENTE para {age_group}: {signal.recommendation}"
        
        return signals
    
    def _detect_age_group(self, query: str, context: Optional[Dict[str, Any]]) -> Optional[str]:
        """Detectar grupo de edad del paciente."""
        
        # Primero verificar contexto explícito
        if context and 'age' in context:
            age = context['age']
            if isinstance(age, (int, float)):
                if age < 2:
                    return 'infant'
                elif age < 12:
                    return 'child'
                elif age > 65:
                    return 'elderly'
        
        # Detectar patrones en el texto
        for age_group, age_data in self.age_modifiers.items():
            patterns = age_data['patterns']
            if any(pattern in query for pattern in patterns):
                return age_group
        
        return None
    
    def _detect_symptom_combinations(self, query: str) -> List[EmergencySignal]:
        """Detectar combinaciones específicas de síntomas."""
        combination_signals = []
        
        for combo_name, combo_data in self.symptom_combinations.items():
            symptoms = combo_data['symptoms']
            threshold = combo_data['threshold']
            
            # Contar síntomas presentes
            symptoms_present = []
            for symptom in symptoms:
                if symptom in query:
                    symptoms_present.append(symptom)
            
            # Si se cumple el threshold, crear señal de combinación
            if len(symptoms_present) >= threshold:
                urgency_boost = combo_data['urgency_boost']
                base_urgency = UrgencyLevel.MODERATE
                
                if urgency_boost >= 2:
                    final_urgency = UrgencyLevel.CRITICAL
                elif urgency_boost >= 1:
                    final_urgency = UrgencyLevel.HIGH
                else:
                    final_urgency = base_urgency
                
                combination_signals.append(EmergencySignal(
                    type='symptom_combination',
                    description=f'Combinación de síntomas: {combo_name}',
                    severity_score=0.7 + combo_data['score_bonus'],
                    keywords_matched=symptoms_present,
                    urgency_level=final_urgency,
                    recommendation=f'🔴 Combinación preocupante de síntomas - Evaluación urgente'
                ))
        
        return combination_signals
    
    def _find_matching_keywords(self, query: str, keywords: List[str]) -> List[str]:
        """Encontrar keywords que coinciden en la consulta."""
        matched = []
        for keyword in keywords:
            # Buscar coincidencias exactas y parciales
            if keyword in query:
                matched.append(keyword)
            else:
                # Buscar coincidencias con flexibilidad en conjugaciones
                keyword_parts = keyword.split()
                if all(part in query for part in keyword_parts):
                    matched.append(keyword)
        
        return matched
    
    def _calculate_overall_urgency(
        self, 
        signals: List[EmergencySignal]
    ) -> Tuple[float, UrgencyLevel]:
        """Calcular score general y nivel de urgencia."""
        
        if not signals:
            return 0.0, UrgencyLevel.ROUTINE
        
        # Calcular score ponderado
        total_score = 0
        max_urgency = UrgencyLevel.ROUTINE
        
        for signal in signals:
            total_score += signal.severity_score
            if signal.urgency_level.value > max_urgency.value:
                max_urgency = signal.urgency_level
        
        # Normalizar score (promedio pero bonificando múltiples señales)
        base_score = total_score / len(signals)
        
        # Bonificación por múltiples señales
        if len(signals) > 1:
            multi_signal_bonus = min(0.2, (len(signals) - 1) * 0.05)
            base_score += multi_signal_bonus
        
        # Asegurar que está en rango [0, 1]
        final_score = min(1.0, base_score)
        
        # Verificar consistencia entre score y urgency level
        if final_score >= 0.9 and max_urgency.value < UrgencyLevel.CRITICAL.value:
            max_urgency = UrgencyLevel.CRITICAL
        elif final_score >= 0.7 and max_urgency.value < UrgencyLevel.HIGH.value:
            max_urgency = UrgencyLevel.HIGH
        elif final_score >= 0.5 and max_urgency.value < UrgencyLevel.MODERATE.value:
            max_urgency = UrgencyLevel.MODERATE
        
        return final_score, max_urgency
    
    def _generate_assessment_details(
        self, 
        signals: List[EmergencySignal], 
        urgency_level: UrgencyLevel
    ) -> Tuple[str, str, str, str]:
        """Generar detalles de la evaluación."""
        
        if not signals:
            return (
                "Sin señales de emergencia detectadas",
                "Consulta médica de rutina si persisten síntomas",
                "No urgente",
                "Programar consulta médica regular"
            )
        
        # Encontrar la señal más crítica
        primary_signal = max(signals, key=lambda s: s.severity_score)
        primary_concern = primary_signal.description
        
        # Generar recomendación basada en urgencia
        if urgency_level == UrgencyLevel.CRITICAL:
            recommendation = "🚨 EMERGENCIA CRÍTICA - Llame al 911 INMEDIATAMENTE"
            time_sensitivity = "INMEDIATO (minutos)"
            action_required = "Transporte de emergencia al hospital más cercano"
        elif urgency_level == UrgencyLevel.HIGH:
            recommendation = "🔴 URGENCIA ALTA - Acuda a urgencias SIN DEMORA"
            time_sensitivity = "URGENTE (1-2 horas máximo)"
            action_required = "Evaluación en servicio de urgencias"
        elif urgency_level == UrgencyLevel.MODERATE:
            recommendation = "🟡 Evaluación médica recomendada en las próximas horas"
            time_sensitivity = "MODERADO (4-8 horas)"
            action_required = "Consulta médica prioritaria"
        else:
            recommendation = "Consulta médica si los síntomas persisten o empeoran"
            time_sensitivity = "NO URGENTE (24-48 horas)"
            action_required = "Consulta médica programada"
        
        # Agregar detalles específicos de las señales
        if len(signals) > 1:
            recommendation += f"\n\nSe detectaron {len(signals)} señales de preocupación."
        
        return primary_concern, recommendation, time_sensitivity, action_required


# Función de compatibilidad con el sistema actual
def detect_medical_emergencies(query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Función de compatibilidad para el sistema actual.
    
    Args:
        query: Consulta del paciente
        context: Contexto adicional
        
    Returns:
        Dict compatible con el formato actual
    """
    detector = AdvancedEmergencyDetector()
    assessment = detector.detect_emergency(query, context)
    
    return {
        'is_emergency': assessment.is_emergency,
        'urgency_level': assessment.urgency_level.value,
        'emergency_score': assessment.overall_score,
        'recommendation': assessment.recommendation,
        'primary_concern': assessment.primary_concern,
        'time_sensitivity': assessment.time_sensitivity,
        'action_required': assessment.action_required,
        'signals_detected': len(assessment.signals),
        'signal_details': [
            {
                'type': signal.type,
                'description': signal.description,
                'severity': signal.severity_score,
                'keywords': signal.keywords_matched
            }
            for signal in assessment.signals
        ]
    } 
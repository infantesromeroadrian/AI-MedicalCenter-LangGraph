"""
Servicio de seguimiento longitudinal y predicción de crisis.
Analiza evolución emocional, patrones temporales y predice episodios de crisis.
"""

import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, deque
import numpy as np
from dataclasses import asdict

from src.models.psychology_models import (
    LongitudinalDataPoint, TemporalPattern, CrisisRiskAssessment,
    EmotionalState, EmotionCategory, ComprehensivePsychProfile
)

# Configurar logging
logger = logging.getLogger(__name__)


class EmotionalEvolutionAnalyzer:
    """Analizador de evolución emocional a lo largo del tiempo."""
    
    def __init__(self):
        """Inicializar analizador de evolución emocional."""
        self.data_points = defaultdict(list)  # Por usuario
        self.analysis_cache = {}
        
    def add_data_point(self, user_id: str, data_point: LongitudinalDataPoint):
        """Añadir punto de datos longitudinal."""
        self.data_points[user_id].append(data_point)
        
        # Mantener solo los últimos 1000 puntos por usuario
        if len(self.data_points[user_id]) > 1000:
            self.data_points[user_id] = self.data_points[user_id][-1000:]
        
        # Invalidar cache para este usuario
        if user_id in self.analysis_cache:
            del self.analysis_cache[user_id]
    
    def generate_evolution_chart_data(self, user_id: str, 
                                    time_period_days: int = 30) -> Dict[str, Any]:
        """Generar datos para gráfico de evolución emocional."""
        try:
            if user_id not in self.data_points:
                return {'error': 'No data available for user'}
            
            # Filtrar datos por período de tiempo
            cutoff_date = datetime.now() - timedelta(days=time_period_days)
            filtered_points = [
                dp for dp in self.data_points[user_id]
                if dp.timestamp >= cutoff_date
            ]
            
            if not filtered_points:
                return {'error': 'No data in specified time period'}
            
            # Organizar datos por métrica
            metrics_data = defaultdict(list)
            timestamps = []
            
            for point in filtered_points:
                timestamps.append(point.timestamp.isoformat())
                metrics_data[point.metric_type].append({
                    'timestamp': point.timestamp.isoformat(),
                    'value': point.value,
                    'context': point.context,
                    'source': point.source
                })
            
            # Calcular estadísticas básicas
            stats = self._calculate_evolution_statistics(filtered_points)
            
            # Detectar tendencias
            trends = self._detect_trends(filtered_points)
            
            return {
                'user_id': user_id,
                'time_period_days': time_period_days,
                'total_data_points': len(filtered_points),
                'metrics_data': dict(metrics_data),
                'unique_timestamps': sorted(list(set(timestamps))),
                'statistics': stats,
                'trends': trends,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating evolution chart data: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_evolution_statistics(self, data_points: List[LongitudinalDataPoint]) -> Dict[str, Any]:
        """Calcular estadísticas de evolución emocional."""
        
        stats = {
            'by_metric': {},
            'overall': {
                'data_point_count': len(data_points),
                'time_span_days': 0,
                'average_frequency_per_day': 0
            }
        }
        
        if not data_points:
            return stats
        
        # Calcular span temporal
        timestamps = [dp.timestamp for dp in data_points]
        time_span = max(timestamps) - min(timestamps)
        stats['overall']['time_span_days'] = time_span.days
        
        if time_span.days > 0:
            stats['overall']['average_frequency_per_day'] = len(data_points) / time_span.days
        
        # Estadísticas por métrica
        metrics_values = defaultdict(list)
        for dp in data_points:
            metrics_values[dp.metric_type].append(dp.value)
        
        for metric, values in metrics_values.items():
            if values:
                stats['by_metric'][metric] = {
                    'count': len(values),
                    'mean': statistics.mean(values),
                    'median': statistics.median(values),
                    'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0,
                    'min': min(values),
                    'max': max(values),
                    'range': max(values) - min(values)
                }
        
        return stats
    
    def _detect_trends(self, data_points: List[LongitudinalDataPoint]) -> Dict[str, Any]:
        """Detectar tendencias en los datos longitudinales."""
        
        trends = {
            'by_metric': {},
            'overall_trend': 'stable'
        }
        
        # Agrupar por métrica
        metrics_data = defaultdict(list)
        for dp in data_points:
            metrics_data[dp.metric_type].append((dp.timestamp, dp.value))
        
        trend_scores = []
        
        for metric, time_value_pairs in metrics_data.items():
            if len(time_value_pairs) < 3:
                continue
            
            # Ordenar por tiempo
            time_value_pairs.sort(key=lambda x: x[0])
            values = [pair[1] for pair in time_value_pairs]
            
            # Calcular tendencia usando regresión lineal simple
            trend_score = self._calculate_linear_trend(values)
            trends['by_metric'][metric] = {
                'trend_score': trend_score,
                'direction': 'improving' if trend_score > 5 else 'declining' if trend_score < -5 else 'stable',
                'strength': 'strong' if abs(trend_score) > 15 else 'moderate' if abs(trend_score) > 5 else 'weak'
            }
            
            trend_scores.append(trend_score)
        
        # Tendencia general
        if trend_scores:
            overall_trend_score = statistics.mean(trend_scores)
            if overall_trend_score > 5:
                trends['overall_trend'] = 'improving'
            elif overall_trend_score < -5:
                trends['overall_trend'] = 'declining'
            else:
                trends['overall_trend'] = 'stable'
        
        return trends
    
    def _calculate_linear_trend(self, values: List[float]) -> float:
        """Calcular tendencia lineal de una serie de valores."""
        n = len(values)
        if n < 2:
            return 0.0
        
        # Calcular pendiente usando mínimos cuadrados
        x = list(range(n))
        x_mean = statistics.mean(x)
        y_mean = statistics.mean(values)
        
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        slope = numerator / denominator
        
        # Normalizar pendiente a escala -100 a 100
        return slope * (100 / max(abs(max(values) - min(values)), 1))


class TemporalPatternDetector:
    """Detector de patrones temporales en datos psicológicos."""
    
    def __init__(self):
        """Inicializar detector de patrones temporales."""
        self.pattern_history = defaultdict(list)
        
    def analyze_temporal_patterns(self, user_id: str, 
                                data_points: List[LongitudinalDataPoint]) -> List[TemporalPattern]:
        """Analizar patrones temporales en los datos."""
        
        patterns = []
        
        # Detectar patrones diarios
        daily_patterns = self._detect_daily_patterns(data_points)
        patterns.extend(daily_patterns)
        
        # Detectar patrones semanales
        weekly_patterns = self._detect_weekly_patterns(data_points)
        patterns.extend(weekly_patterns)
        
        # Detectar patrones estacionales (si hay suficientes datos)
        if self._has_sufficient_data_for_seasonal(data_points):
            seasonal_patterns = self._detect_seasonal_patterns(data_points)
            patterns.extend(seasonal_patterns)
        
        # Almacenar patrones detectados
        self.pattern_history[user_id].extend(patterns)
        
        return patterns
    
    def _detect_daily_patterns(self, data_points: List[LongitudinalDataPoint]) -> List[TemporalPattern]:
        """Detectar patrones diarios (horas del día)."""
        
        patterns = []
        
        # Agrupar por hora del día
        hourly_data = defaultdict(lambda: defaultdict(list))
        
        for dp in data_points:
            hour = dp.timestamp.hour
            hourly_data[dp.metric_type][hour].append(dp.value)
        
        for metric, hours_data in hourly_data.items():
            if len(hours_data) < 3:  # Necesitamos al menos 3 horas diferentes
                continue
            
            # Calcular promedios por hora
            hour_averages = {}
            for hour, values in hours_data.items():
                if values:
                    hour_averages[hour] = statistics.mean(values)
            
            if len(hour_averages) < 3:
                continue
            
            # Encontrar picos y valles
            peak_hours = self._find_peaks(hour_averages)
            low_hours = self._find_lows(hour_averages)
            
            if peak_hours or low_hours:
                confidence = min(1.0, len(hour_averages) / 24)  # Más horas = más confianza
                
                pattern = TemporalPattern(
                    pattern_type="daily",
                    metric=metric,
                    pattern_description=f"Patrón diario en {metric}",
                    confidence=confidence,
                    peak_times=[f"{hour}:00" for hour in peak_hours],
                    low_times=[f"{hour}:00" for hour in low_hours],
                    trend_direction=self._determine_trend_direction(hour_averages),
                    statistical_significance=self._calculate_significance(hours_data)
                )
                patterns.append(pattern)
        
        return patterns
    
    def _detect_weekly_patterns(self, data_points: List[LongitudinalDataPoint]) -> List[TemporalPattern]:
        """Detectar patrones semanales (días de la semana)."""
        
        patterns = []
        
        # Agrupar por día de la semana
        weekly_data = defaultdict(lambda: defaultdict(list))
        
        for dp in data_points:
            weekday = dp.timestamp.weekday()  # 0=Monday, 6=Sunday
            weekly_data[dp.metric_type][weekday].append(dp.value)
        
        weekday_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        
        for metric, days_data in weekly_data.items():
            if len(days_data) < 3:  # Necesitamos al menos 3 días diferentes
                continue
            
            # Calcular promedios por día
            day_averages = {}
            for day, values in days_data.items():
                if values:
                    day_averages[day] = statistics.mean(values)
            
            if len(day_averages) < 3:
                continue
            
            # Encontrar patrones de fin de semana vs días laborables
            weekday_avg = statistics.mean([avg for day, avg in day_averages.items() if day < 5])
            weekend_avg = statistics.mean([avg for day, avg in day_averages.items() if day >= 5])
            
            if abs(weekday_avg - weekend_avg) > 10:  # Diferencia significativa
                confidence = min(1.0, len(day_averages) / 7)
                
                pattern_desc = f"Diferencia significativa entre días laborables y fines de semana en {metric}"
                if weekday_avg > weekend_avg:
                    pattern_desc += " (mayor en días laborables)"
                else:
                    pattern_desc += " (mayor en fines de semana)"
                
                pattern = TemporalPattern(
                    pattern_type="weekly",
                    metric=metric,
                    pattern_description=pattern_desc,
                    confidence=confidence,
                    peak_times=[weekday_names[day] for day, avg in day_averages.items() if avg > statistics.mean(day_averages.values())],
                    low_times=[weekday_names[day] for day, avg in day_averages.items() if avg < statistics.mean(day_averages.values())],
                    trend_direction="variable",
                    statistical_significance=abs(weekday_avg - weekend_avg) / max(weekday_avg, weekend_avg)
                )
                patterns.append(pattern)
        
        return patterns
    
    def _detect_seasonal_patterns(self, data_points: List[LongitudinalDataPoint]) -> List[TemporalPattern]:
        """Detectar patrones estacionales (meses del año)."""
        
        patterns = []
        
        # Agrupar por mes
        monthly_data = defaultdict(lambda: defaultdict(list))
        
        for dp in data_points:
            month = dp.timestamp.month
            monthly_data[dp.metric_type][month].append(dp.value)
        
        month_names = [
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ]
        
        for metric, months_data in monthly_data.items():
            if len(months_data) < 6:  # Necesitamos al menos 6 meses
                continue
            
            # Calcular promedios por mes
            month_averages = {}
            for month, values in months_data.items():
                if values:
                    month_averages[month] = statistics.mean(values)
            
            if len(month_averages) < 6:
                continue
            
            # Detectar estacionalidad (invierno vs verano)
            winter_months = [12, 1, 2]
            summer_months = [6, 7, 8]
            
            winter_values = [avg for month, avg in month_averages.items() if month in winter_months]
            summer_values = [avg for month, avg in month_averages.items() if month in summer_months]
            
            if winter_values and summer_values:
                winter_avg = statistics.mean(winter_values)
                summer_avg = statistics.mean(summer_values)
                
                if abs(winter_avg - summer_avg) > 15:  # Diferencia estacional significativa
                    confidence = min(1.0, len(month_averages) / 12)
                    
                    pattern_desc = f"Patrón estacional en {metric}"
                    if winter_avg > summer_avg:
                        pattern_desc += " (mayor en invierno)"
                    else:
                        pattern_desc += " (mayor en verano)"
                    
                    pattern = TemporalPattern(
                        pattern_type="seasonal",
                        metric=metric,
                        pattern_description=pattern_desc,
                        confidence=confidence,
                        peak_times=[month_names[month-1] for month, avg in month_averages.items() if avg > statistics.mean(month_averages.values())],
                        low_times=[month_names[month-1] for month, avg in month_averages.items() if avg < statistics.mean(month_averages.values())],
                        trend_direction="cyclical",
                        statistical_significance=abs(winter_avg - summer_avg) / max(winter_avg, summer_avg)
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _has_sufficient_data_for_seasonal(self, data_points: List[LongitudinalDataPoint]) -> bool:
        """Verificar si hay suficientes datos para análisis estacional."""
        if not data_points:
            return False
        
        timestamps = [dp.timestamp for dp in data_points]
        time_span = max(timestamps) - min(timestamps)
        
        return time_span.days >= 180  # Al menos 6 meses de datos
    
    def _find_peaks(self, hour_averages: Dict[int, float]) -> List[int]:
        """Encontrar horas pico en los datos."""
        if len(hour_averages) < 3:
            return []
        
        values = list(hour_averages.values())
        threshold = statistics.mean(values) + (statistics.stdev(values) if len(values) > 1 else 0)
        
        return [hour for hour, avg in hour_averages.items() if avg > threshold]
    
    def _find_lows(self, hour_averages: Dict[int, float]) -> List[int]:
        """Encontrar horas bajas en los datos."""
        if len(hour_averages) < 3:
            return []
        
        values = list(hour_averages.values())
        threshold = statistics.mean(values) - (statistics.stdev(values) if len(values) > 1 else 0)
        
        return [hour for hour, avg in hour_averages.items() if avg < threshold]
    
    def _determine_trend_direction(self, time_averages: Dict[int, float]) -> str:
        """Determinar dirección de tendencia."""
        if len(time_averages) < 2:
            return "stable"
        
        times = sorted(time_averages.keys())
        values = [time_averages[t] for t in times]
        
        # Calcular tendencia simple
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        if first_half and second_half:
            first_avg = statistics.mean(first_half)
            second_avg = statistics.mean(second_half)
            
            if second_avg > first_avg * 1.1:
                return "improving"
            elif second_avg < first_avg * 0.9:
                return "declining"
        
        return "stable"
    
    def _calculate_significance(self, data_groups: Dict[int, List[float]]) -> float:
        """Calcular significancia estadística de los patrones."""
        all_values = []
        for values in data_groups.values():
            all_values.extend(values)
        
        if len(all_values) < 3:
            return 0.0
        
        overall_std = statistics.stdev(all_values)
        if overall_std == 0:
            return 0.0
        
        # Calcular variabilidad entre grupos vs dentro de grupos
        group_means = [statistics.mean(values) for values in data_groups.values() if values]
        
        if len(group_means) < 2:
            return 0.0
        
        between_group_var = statistics.stdev(group_means)
        significance = between_group_var / overall_std
        
        return min(1.0, significance)


class CrisisPredictionEngine:
    """Motor de predicción de episodios de crisis."""
    
    def __init__(self):
        """Inicializar motor de predicción de crisis."""
        self.risk_indicators = self._load_risk_indicators()
        self.prediction_history = defaultdict(list)
        
    def _load_risk_indicators(self) -> Dict[str, Dict[str, Any]]:
        """Cargar indicadores de riesgo para predicción de crisis."""
        return {
            'emotional_intensity': {
                'weight': 0.3,
                'thresholds': {
                    'low': 30,
                    'moderate': 60,
                    'high': 80,
                    'critical': 90
                }
            },
            'negative_valence': {
                'weight': 0.25,
                'thresholds': {
                    'low': -20,
                    'moderate': -40,
                    'high': -60,
                    'critical': -80
                }
            },
            'pattern_disruption': {
                'weight': 0.2,
                'description': 'Cambios abruptos en patrones establecidos'
            },
            'frequency_increase': {
                'weight': 0.15,
                'description': 'Aumento en frecuencia de episodios negativos'
            },
            'duration_extension': {
                'weight': 0.1,
                'description': 'Extensión en duración de estados negativos'
            }
        }
    
    def assess_crisis_risk(self, user_id: str, 
                          recent_data: List[LongitudinalDataPoint],
                          emotional_states: List[EmotionalState],
                          temporal_patterns: List[TemporalPattern]) -> CrisisRiskAssessment:
        """Evaluar riesgo de crisis basado en datos recientes."""
        
        try:
            assessment_id = f"crisis_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Calcular scores de riesgo
            risk_scores = self._calculate_risk_scores(recent_data, emotional_states, temporal_patterns)
            
            # Calcular score total ponderado
            total_risk_score = sum(
                score * self.risk_indicators[indicator]['weight']
                for indicator, score in risk_scores.items()
                if indicator in self.risk_indicators
            )
            
            # Determinar nivel de riesgo
            risk_level = self._determine_risk_level(total_risk_score)
            
            # Identificar factores de riesgo específicos
            risk_factors = self._identify_risk_factors(recent_data, emotional_states, risk_scores)
            
            # Identificar factores protectores
            protective_factors = self._identify_protective_factors(recent_data, emotional_states)
            
            # Generar acciones inmediatas recomendadas
            immediate_actions = self._generate_immediate_actions(risk_level, risk_factors)
            
            # Calcular confianza en la predicción
            confidence = self._calculate_prediction_confidence(
                len(recent_data), len(emotional_states), temporal_patterns
            )
            
            assessment = CrisisRiskAssessment(
                assessment_id=assessment_id,
                session_id=user_id,
                risk_level=risk_level,
                risk_score=total_risk_score,
                risk_factors=risk_factors,
                protective_factors=protective_factors,
                immediate_actions=immediate_actions,
                confidence=confidence
            )
            
            # Almacenar en historial
            self.prediction_history[user_id].append(assessment)
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error in crisis risk assessment: {str(e)}")
            return CrisisRiskAssessment(
                assessment_id="error",
                session_id=user_id,
                risk_level="unknown",
                risk_score=0.0,
                confidence=0.0
            )
    
    def _calculate_risk_scores(self, data_points: List[LongitudinalDataPoint],
                             emotional_states: List[EmotionalState],
                             patterns: List[TemporalPattern]) -> Dict[str, float]:
        """Calcular scores de riesgo para diferentes indicadores."""
        
        scores = {}
        
        # Score de intensidad emocional
        if emotional_states:
            recent_intensities = [es.intensity for es in emotional_states[-10:]]  # Últimos 10
            avg_intensity = statistics.mean(recent_intensities)
            scores['emotional_intensity'] = min(100.0, avg_intensity)
        else:
            scores['emotional_intensity'] = 0.0
        
        # Score de valencia negativa
        if emotional_states:
            recent_valences = [es.valence for es in emotional_states[-10:]]
            avg_valence = statistics.mean(recent_valences)
            # Convertir valencia negativa a score de riesgo (0-100)
            scores['negative_valence'] = max(0.0, min(100.0, -avg_valence))
        else:
            scores['negative_valence'] = 0.0
        
        # Score de disrupción de patrones
        scores['pattern_disruption'] = self._calculate_pattern_disruption_score(patterns)
        
        # Score de aumento de frecuencia
        scores['frequency_increase'] = self._calculate_frequency_increase_score(data_points)
        
        # Score de extensión de duración
        scores['duration_extension'] = self._calculate_duration_extension_score(emotional_states)
        
        return scores
    
    def _calculate_pattern_disruption_score(self, patterns: List[TemporalPattern]) -> float:
        """Calcular score de disrupción de patrones."""
        if not patterns:
            return 0.0
        
        # Buscar patrones con tendencia declining o alta variabilidad
        disruption_score = 0.0
        
        for pattern in patterns:
            if pattern.trend_direction == "declining":
                disruption_score += 30.0
            elif pattern.statistical_significance > 0.7:  # Alta variabilidad
                disruption_score += 20.0
        
        return min(100.0, disruption_score)
    
    def _calculate_frequency_increase_score(self, data_points: List[LongitudinalDataPoint]) -> float:
        """Calcular score de aumento en frecuencia de episodios."""
        if len(data_points) < 10:
            return 0.0
        
        # Comparar frecuencia reciente vs anterior
        cutoff = len(data_points) // 2
        recent_points = data_points[cutoff:]
        older_points = data_points[:cutoff]
        
        if not older_points:
            return 0.0
        
        # Calcular timestamps para frecuencia
        recent_days = (max(dp.timestamp for dp in recent_points) - 
                      min(dp.timestamp for dp in recent_points)).days or 1
        older_days = (max(dp.timestamp for dp in older_points) - 
                     min(dp.timestamp for dp in older_points)).days or 1
        
        recent_freq = len(recent_points) / recent_days
        older_freq = len(older_points) / older_days
        
        if older_freq == 0:
            return 0.0
        
        frequency_increase = (recent_freq - older_freq) / older_freq
        
        return min(100.0, max(0.0, frequency_increase * 100))
    
    def _calculate_duration_extension_score(self, emotional_states: List[EmotionalState]) -> float:
        """Calcular score de extensión en duración de estados negativos."""
        if len(emotional_states) < 5:
            return 0.0
        
        # Buscar secuencias de estados negativos consecutivos
        negative_sequences = []
        current_sequence = 0
        
        for state in emotional_states:
            if state.valence < -20:  # Estado negativo
                current_sequence += 1
            else:
                if current_sequence > 0:
                    negative_sequences.append(current_sequence)
                current_sequence = 0
        
        if current_sequence > 0:
            negative_sequences.append(current_sequence)
        
        if not negative_sequences:
            return 0.0
        
        # Score basado en la secuencia más larga
        max_sequence = max(negative_sequences)
        
        if max_sequence >= 5:
            return 80.0
        elif max_sequence >= 3:
            return 50.0
        elif max_sequence >= 2:
            return 25.0
        else:
            return 0.0
    
    def _determine_risk_level(self, total_score: float) -> str:
        """Determinar nivel de riesgo basado en score total."""
        if total_score >= 80:
            return "critical"
        elif total_score >= 60:
            return "high"
        elif total_score >= 40:
            return "moderate"
        else:
            return "low"
    
    def _identify_risk_factors(self, data_points: List[LongitudinalDataPoint],
                             emotional_states: List[EmotionalState],
                             risk_scores: Dict[str, float]) -> List[str]:
        """Identificar factores de riesgo específicos."""
        
        risk_factors = []
        
        # Basado en scores de riesgo
        if risk_scores.get('emotional_intensity', 0) > 70:
            risk_factors.append("Alta intensidad emocional sostenida")
        
        if risk_scores.get('negative_valence', 0) > 60:
            risk_factors.append("Predominio de emociones negativas")
        
        if risk_scores.get('pattern_disruption', 0) > 50:
            risk_factors.append("Disrupción de patrones emocionales establecidos")
        
        if risk_scores.get('frequency_increase', 0) > 40:
            risk_factors.append("Aumento en frecuencia de episodios negativos")
        
        if risk_scores.get('duration_extension', 0) > 30:
            risk_factors.append("Extensión de duración de estados negativos")
        
        # Factores específicos de estados emocionales
        if emotional_states:
            recent_emotions = [es.primary_emotion for es in emotional_states[-5:]]
            
            if EmotionCategory.ANXIETY in recent_emotions:
                risk_factors.append("Presencia reciente de ansiedad")
            
            if EmotionCategory.ANGER in recent_emotions:
                risk_factors.append("Episodios de ira recientes")
            
            # Buscar emociones contradictorias
            contradictory_count = sum(1 for es in emotional_states[-5:] if es.contradictory_emotions)
            if contradictory_count >= 2:
                risk_factors.append("Emociones contradictorias frecuentes")
        
        return risk_factors
    
    def _identify_protective_factors(self, data_points: List[LongitudinalDataPoint],
                                   emotional_states: List[EmotionalState]) -> List[str]:
        """Identificar factores protectores."""
        
        protective_factors = []
        
        if emotional_states:
            # Buscar emociones positivas recientes
            recent_positive = [es for es in emotional_states[-10:] if es.valence > 20]
            if len(recent_positive) >= 3:
                protective_factors.append("Presencia de emociones positivas recientes")
            
            # Buscar estabilidad emocional
            recent_intensities = [es.intensity for es in emotional_states[-10:]]
            if recent_intensities and statistics.stdev(recent_intensities) < 15:
                protective_factors.append("Estabilidad emocional general")
            
            # Buscar evidencia de regulación emocional
            improving_states = 0
            for i in range(1, min(len(emotional_states), 6)):
                if emotional_states[-i].valence > emotional_states[-i-1].valence:
                    improving_states += 1
            
            if improving_states >= 3:
                protective_factors.append("Evidencia de autorregulación emocional")
        
        # Buscar consistencia en datos
        if len(data_points) >= 10:
            recent_consistency = len([dp for dp in data_points[-10:] if dp.source == "session"])
            if recent_consistency >= 7:
                protective_factors.append("Participación consistente en terapia")
        
        return protective_factors
    
    def _generate_immediate_actions(self, risk_level: str, risk_factors: List[str]) -> List[str]:
        """Generar acciones inmediatas recomendadas."""
        
        actions = []
        
        if risk_level == "critical":
            actions.extend([
                "Contactar inmediatamente con profesional de salud mental",
                "Implementar plan de seguridad personal",
                "Activar red de apoyo de emergencia",
                "Considerar evaluación presencial urgente"
            ])
        
        elif risk_level == "high":
            actions.extend([
                "Programar sesión de seguimiento en 24-48 horas",
                "Implementar técnicas de grounding inmediatas",
                "Contactar con persona de apoyo designada",
                "Iniciar protocolo de crisis preventiva"
            ])
        
        elif risk_level == "moderate":
            actions.extend([
                "Aumentar frecuencia de check-ins",
                "Implementar técnicas de autorregulación",
                "Revisar y ajustar plan de tratamiento",
                "Programar sesión adicional esta semana"
            ])
        
        else:  # low risk
            actions.extend([
                "Mantener rutina de autocuidado",
                "Continuar con plan de tratamiento actual",
                "Monitorear síntomas regularmente"
            ])
        
        # Acciones específicas basadas en factores de riesgo
        if "Alta intensidad emocional sostenida" in risk_factors:
            actions.append("Practicar ejercicios de respiración 3 veces al día")
        
        if "Predominio de emociones negativas" in risk_factors:
            actions.append("Implementar actividades de activación conductual")
        
        return actions
    
    def _calculate_prediction_confidence(self, data_count: int, 
                                       emotional_states_count: int,
                                       patterns: List[TemporalPattern]) -> float:
        """Calcular confianza en la predicción."""
        
        confidence = 0.0
        
        # Confianza basada en cantidad de datos
        confidence += min(0.4, data_count / 50)  # Máximo 40% por cantidad de datos
        
        # Confianza basada en estados emocionales
        confidence += min(0.3, emotional_states_count / 20)  # Máximo 30%
        
        # Confianza basada en patrones temporales
        pattern_confidence = sum(p.confidence for p in patterns) / max(len(patterns), 1)
        confidence += pattern_confidence * 0.3  # Máximo 30%
        
        return min(1.0, confidence)


class LongitudinalTrackingService:
    """Servicio principal de seguimiento longitudinal."""
    
    def __init__(self):
        """Inicializar servicio de seguimiento longitudinal."""
        self.evolution_analyzer = EmotionalEvolutionAnalyzer()
        self.pattern_detector = TemporalPatternDetector()
        self.crisis_predictor = CrisisPredictionEngine()
        self.user_profiles = {}
        
    def track_emotional_data(self, user_id: str, emotional_state: EmotionalState) -> Dict[str, Any]:
        """Trackear datos emocionales longitudinales."""
        try:
            # Crear puntos de datos longitudinales
            data_points = [
                LongitudinalDataPoint(
                    timestamp=emotional_state.timestamp,
                    metric_type="emotional_valence",
                    value=emotional_state.valence,
                    context="Emotional state tracking",
                    source="session"
                ),
                LongitudinalDataPoint(
                    timestamp=emotional_state.timestamp,
                    metric_type="emotional_intensity",
                    value=emotional_state.intensity,
                    context="Emotional state tracking",
                    source="session"
                ),
                LongitudinalDataPoint(
                    timestamp=emotional_state.timestamp,
                    metric_type="arousal_level",
                    value=emotional_state.arousal,
                    context="Emotional state tracking",
                    source="session"
                )
            ]
            
            # Añadir a análisis de evolución
            for dp in data_points:
                self.evolution_analyzer.add_data_point(user_id, dp)
            
            return {
                'user_id': user_id,
                'tracked_metrics': ['emotional_valence', 'emotional_intensity', 'arousal_level'],
                'data_points_added': len(data_points),
                'timestamp': emotional_state.timestamp.isoformat(),
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error tracking emotional data: {str(e)}")
            return {'error': str(e)}
    
    def generate_comprehensive_analysis(self, user_id: str, 
                                      time_period_days: int = 30) -> Dict[str, Any]:
        """Generar análisis longitudinal completo."""
        try:
            # Obtener datos de evolución
            evolution_data = self.evolution_analyzer.generate_evolution_chart_data(
                user_id, time_period_days
            )
            
            if 'error' in evolution_data:
                return evolution_data
            
            # Extraer puntos de datos para análisis de patrones
            data_points = []
            if user_id in self.evolution_analyzer.data_points:
                cutoff_date = datetime.now() - timedelta(days=time_period_days)
                data_points = [
                    dp for dp in self.evolution_analyzer.data_points[user_id]
                    if dp.timestamp >= cutoff_date
                ]
            
            # Detectar patrones temporales
            temporal_patterns = self.pattern_detector.analyze_temporal_patterns(user_id, data_points)
            
            # Crear estados emocionales de ejemplo para predicción
            # (En implementación real, estos vendrían de la base de datos)
            emotional_states = self._extract_emotional_states_from_data(data_points)
            
            # Evaluar riesgo de crisis
            crisis_assessment = self.crisis_predictor.assess_crisis_risk(
                user_id, data_points, emotional_states, temporal_patterns
            )
            
            return {
                'user_id': user_id,
                'analysis_period_days': time_period_days,
                'emotional_evolution': evolution_data,
                'temporal_patterns': [pattern.to_dict() for pattern in temporal_patterns],
                'crisis_risk_assessment': crisis_assessment.to_dict(),
                'summary': {
                    'total_data_points': len(data_points),
                    'patterns_detected': len(temporal_patterns),
                    'current_risk_level': crisis_assessment.risk_level,
                    'trends_identified': evolution_data.get('trends', {}),
                    'recommendations': self._generate_longitudinal_recommendations(
                        evolution_data, temporal_patterns, crisis_assessment
                    )
                },
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating comprehensive analysis: {str(e)}")
            return {'error': str(e)}
    
    def _extract_emotional_states_from_data(self, data_points: List[LongitudinalDataPoint]) -> List[EmotionalState]:
        """Extraer estados emocionales aproximados de puntos de datos."""
        # Esta es una implementación simplificada
        # En la práctica, los estados emocionales vendrían directamente de la base de datos
        
        emotional_states = []
        
        # Agrupar puntos de datos por timestamp
        grouped_by_time = defaultdict(dict)
        for dp in data_points:
            grouped_by_time[dp.timestamp][dp.metric_type] = dp.value
        
        for timestamp, metrics in grouped_by_time.items():
            if 'emotional_valence' in metrics and 'emotional_intensity' in metrics:
                # Crear estado emocional aproximado
                valence = metrics['emotional_valence']
                intensity = metrics['emotional_intensity']
                arousal = metrics.get('arousal_level', 50.0)
                
                # Determinar emoción primaria basada en valence e intensity
                if valence > 20:
                    primary_emotion = EmotionCategory.JOY
                elif valence < -40:
                    if arousal > 60:
                        primary_emotion = EmotionCategory.ANXIETY
                    else:
                        primary_emotion = EmotionCategory.SADNESS
                else:
                    primary_emotion = EmotionCategory.CONTENTMENT
                
                emotional_state = EmotionalState(
                    timestamp=timestamp,
                    primary_emotion=primary_emotion,
                    intensity=intensity,
                    valence=valence,
                    arousal=arousal
                )
                
                emotional_states.append(emotional_state)
        
        return sorted(emotional_states, key=lambda x: x.timestamp)
    
    def _generate_longitudinal_recommendations(self, evolution_data: Dict, 
                                             patterns: List[TemporalPattern],
                                             crisis_assessment: CrisisRiskAssessment) -> List[str]:
        """Generar recomendaciones basadas en análisis longitudinal."""
        
        recommendations = []
        
        # Recomendaciones basadas en tendencias
        trends = evolution_data.get('trends', {})
        overall_trend = trends.get('overall_trend', 'stable')
        
        if overall_trend == 'declining':
            recommendations.append("Intensificar intervenciones terapéuticas debido a tendencia negativa")
        elif overall_trend == 'improving':
            recommendations.append("Mantener estrategias actuales que están mostrando mejora")
        
        # Recomendaciones basadas en patrones temporales
        for pattern in patterns:
            if pattern.pattern_type == "daily" and pattern.peak_times:
                recommendations.append(f"Planificar actividades de autocuidado durante horas pico: {', '.join(pattern.peak_times)}")
            elif pattern.pattern_type == "weekly" and "fin de semana" in pattern.pattern_description.lower():
                recommendations.append("Desarrollar estrategias específicas para manejo de fines de semana")
        
        # Recomendaciones basadas en riesgo de crisis
        if crisis_assessment.risk_level in ['high', 'critical']:
            recommendations.append("Implementar protocolo de prevención de crisis inmediatamente")
            recommendations.extend(crisis_assessment.immediate_actions[:3])  # Top 3 acciones
        
        # Recomendaciones generales
        if not recommendations:
            recommendations.append("Continuar con seguimiento regular y monitoreo de patrones")
        
        return recommendations[:5]  # Máximo 5 recomendaciones 
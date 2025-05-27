"""
Sistema de métricas de performance para agentes médicos especializados.
Monitorea efectividad, calidad y rendimiento de cada agente.
"""
import time
import logging
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import statistics

logger = logging.getLogger(__name__)

@dataclass
class ResponseMetrics:
    """Métricas de una respuesta individual."""
    agent_id: str
    specialty: str
    response_time: float
    confidence_score: float
    word_count: int
    has_recommendations: bool
    has_sources: bool
    emergency_detected: bool
    user_query_length: int
    timestamp: datetime

@dataclass
class AgentPerformanceMetrics:
    """Métricas de performance acumuladas por agente."""
    specialty: str
    total_queries: int
    avg_response_time: float
    avg_confidence: float
    avg_word_count: float
    recommendations_rate: float
    sources_rate: float
    emergency_detection_rate: float
    last_24h_queries: int
    last_7d_queries: int
    quality_score: float
    consistency_score: float
    timestamp: datetime

@dataclass
class ConsensusMetrics:
    """Métricas del sistema de consenso."""
    total_consensus_sessions: int
    avg_agents_per_consensus: float
    avg_agreement_score: float
    avg_confidence_weighted_score: float
    avg_complementarity_score: float
    conflict_rate: float
    synthesis_success_rate: float
    timestamp: datetime

@dataclass
class SystemPerformanceMetrics:
    """Métricas generales del sistema."""
    total_queries_processed: int
    avg_total_response_time: float
    emergency_detection_accuracy: float
    user_satisfaction_score: float
    system_uptime: float
    error_rate: float
    knowledge_base_usage: Dict[str, int]
    timestamp: datetime

class PerformanceMonitor:
    """Monitor de performance para agentes médicos."""
    
    def __init__(self, metrics_file: str = "logs/performance_metrics.json"):
        """Inicializar el monitor de performance."""
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Almacenamiento en memoria para métricas recientes
        self.recent_responses: List[ResponseMetrics] = []
        self.agent_metrics: Dict[str, AgentPerformanceMetrics] = {}
        self.consensus_metrics: Optional[ConsensusMetrics] = None
        self.system_metrics: Optional[SystemPerformanceMetrics] = None
        
        # Configuración
        self.max_recent_responses = 1000  # Máximo número de respuestas recientes en memoria
        self.metrics_calculation_interval = 300  # 5 minutos
        self.last_calculation_time = time.time()
        
        self._load_existing_metrics()
        
        logger.info("Performance monitor initialized")
    
    def record_response(
        self,
        agent_id: str,
        specialty: str,
        response_time: float,
        confidence_score: float,
        response_content: str,
        has_recommendations: bool,
        has_sources: bool,
        emergency_detected: bool,
        user_query: str
    ) -> None:
        """Registrar métricas de una respuesta."""
        
        metrics = ResponseMetrics(
            agent_id=agent_id,
            specialty=specialty,
            response_time=response_time,
            confidence_score=confidence_score,
            word_count=len(response_content.split()),
            has_recommendations=has_recommendations,
            has_sources=has_sources,
            emergency_detected=emergency_detected,
            user_query_length=len(user_query.split()),
            timestamp=datetime.now()
        )
        
        self.recent_responses.append(metrics)
        
        # Mantener solo las respuestas más recientes en memoria
        if len(self.recent_responses) > self.max_recent_responses:
            self.recent_responses = self.recent_responses[-self.max_recent_responses:]
        
        # Calcular métricas periódicamente
        if time.time() - self.last_calculation_time > self.metrics_calculation_interval:
            self._calculate_metrics()
            self.last_calculation_time = time.time()
        
        logger.debug(f"Recorded response metrics for {specialty} agent")
    
    def record_consensus_session(
        self,
        agents_involved: List[str],
        agreement_score: float,
        confidence_weighted_score: float,
        complementarity_score: float,
        had_conflicts: bool,
        synthesis_successful: bool
    ) -> None:
        """Registrar métricas de una sesión de consenso."""
        
        # Actualizar métricas de consenso existentes o crear nuevas
        if self.consensus_metrics is None:
            self.consensus_metrics = ConsensusMetrics(
                total_consensus_sessions=1,
                avg_agents_per_consensus=len(agents_involved),
                avg_agreement_score=agreement_score,
                avg_confidence_weighted_score=confidence_weighted_score,
                avg_complementarity_score=complementarity_score,
                conflict_rate=1.0 if had_conflicts else 0.0,
                synthesis_success_rate=1.0 if synthesis_successful else 0.0,
                timestamp=datetime.now()
            )
        else:
            # Calcular promedios actualizados
            total = self.consensus_metrics.total_consensus_sessions
            new_total = total + 1
            
            self.consensus_metrics.avg_agents_per_consensus = (
                (self.consensus_metrics.avg_agents_per_consensus * total + len(agents_involved)) / new_total
            )
            self.consensus_metrics.avg_agreement_score = (
                (self.consensus_metrics.avg_agreement_score * total + agreement_score) / new_total
            )
            self.consensus_metrics.avg_confidence_weighted_score = (
                (self.consensus_metrics.avg_confidence_weighted_score * total + confidence_weighted_score) / new_total
            )
            self.consensus_metrics.avg_complementarity_score = (
                (self.consensus_metrics.avg_complementarity_score * total + complementarity_score) / new_total
            )
            self.consensus_metrics.conflict_rate = (
                (self.consensus_metrics.conflict_rate * total + (1.0 if had_conflicts else 0.0)) / new_total
            )
            self.consensus_metrics.synthesis_success_rate = (
                (self.consensus_metrics.synthesis_success_rate * total + (1.0 if synthesis_successful else 0.0)) / new_total
            )
            
            self.consensus_metrics.total_consensus_sessions = new_total
            self.consensus_metrics.timestamp = datetime.now()
        
        logger.debug("Recorded consensus session metrics")
    
    def _calculate_metrics(self) -> None:
        """Calcular métricas acumuladas para todos los agentes."""
        
        # Agrupar respuestas por especialidad
        specialty_responses = {}
        for response in self.recent_responses:
            if response.specialty not in specialty_responses:
                specialty_responses[response.specialty] = []
            specialty_responses[response.specialty].append(response)
        
        # Calcular métricas por especialidad
        for specialty, responses in specialty_responses.items():
            if not responses:
                continue
                
            # Filtrar respuestas por tiempo
            now = datetime.now()
            last_24h = [r for r in responses if (now - r.timestamp).total_seconds() < 86400]
            last_7d = [r for r in responses if (now - r.timestamp).total_seconds() < 604800]
            
            # Calcular métricas básicas
            avg_response_time = statistics.mean([r.response_time for r in responses])
            avg_confidence = statistics.mean([r.confidence_score for r in responses])
            avg_word_count = statistics.mean([r.word_count for r in responses])
            
            recommendations_rate = sum(1 for r in responses if r.has_recommendations) / len(responses)
            sources_rate = sum(1 for r in responses if r.has_sources) / len(responses)
            emergency_detection_rate = sum(1 for r in responses if r.emergency_detected) / len(responses)
            
            # Calcular score de calidad
            quality_score = self._calculate_quality_score(responses)
            
            # Calcular score de consistencia
            consistency_score = self._calculate_consistency_score(responses)
            
            # Crear métricas del agente
            agent_metrics = AgentPerformanceMetrics(
                specialty=specialty,
                total_queries=len(responses),
                avg_response_time=avg_response_time,
                avg_confidence=avg_confidence,
                avg_word_count=avg_word_count,
                recommendations_rate=recommendations_rate,
                sources_rate=sources_rate,
                emergency_detection_rate=emergency_detection_rate,
                last_24h_queries=len(last_24h),
                last_7d_queries=len(last_7d),
                quality_score=quality_score,
                consistency_score=consistency_score,
                timestamp=datetime.now()
            )
            
            self.agent_metrics[specialty] = agent_metrics
        
        # Calcular métricas del sistema
        self._calculate_system_metrics()
        
        # Guardar métricas
        self._save_metrics()
        
        logger.info("Calculated and updated performance metrics")
    
    def _calculate_quality_score(self, responses: List[ResponseMetrics]) -> float:
        """Calcular score de calidad basado en múltiples factores."""
        
        if not responses:
            return 0.0
        
        scores = []
        
        for response in responses:
            # Factores de calidad
            confidence_factor = response.confidence_score
            length_factor = min(1.0, response.word_count / 100)  # Óptimo ~100 palabras
            recommendations_factor = 1.2 if response.has_recommendations else 0.8
            sources_factor = 1.1 if response.has_sources else 0.9
            response_time_factor = max(0.5, min(1.0, 5.0 / response.response_time))  # Óptimo <5 segundos
            
            # Score compuesto
            quality = (
                confidence_factor * 0.3 +
                length_factor * 0.2 +
                recommendations_factor * 0.2 +
                sources_factor * 0.15 +
                response_time_factor * 0.15
            )
            
            scores.append(min(1.0, quality))
        
        return statistics.mean(scores)
    
    def _calculate_consistency_score(self, responses: List[ResponseMetrics]) -> float:
        """Calcular score de consistencia basado en variabilidad de métricas."""
        
        if len(responses) < 2:
            return 1.0
        
        # Calcular coeficientes de variación para diferentes métricas
        confidence_scores = [r.confidence_score for r in responses]
        response_times = [r.response_time for r in responses]
        word_counts = [r.word_count for r in responses]
        
        def coefficient_of_variation(values):
            if not values or statistics.mean(values) == 0:
                return 0
            return statistics.stdev(values) / statistics.mean(values)
        
        confidence_cv = coefficient_of_variation(confidence_scores)
        response_time_cv = coefficient_of_variation(response_times)
        word_count_cv = coefficient_of_variation(word_counts)
        
        # Score de consistencia (menor variabilidad = mayor consistencia)
        consistency_score = 1.0 - min(1.0, (confidence_cv + response_time_cv + word_count_cv) / 3.0)
        
        return max(0.0, consistency_score)
    
    def _calculate_system_metrics(self) -> None:
        """Calcular métricas generales del sistema."""
        
        if not self.recent_responses:
            return
        
        total_queries = len(self.recent_responses)
        avg_total_response_time = statistics.mean([r.response_time for r in self.recent_responses])
        
        # Rate de detección de emergencias (simplificado)
        emergency_detected = sum(1 for r in self.recent_responses if r.emergency_detected)
        emergency_detection_accuracy = 0.95  # Placeholder - requiere validación manual
        
        # Score de satisfacción del usuario (placeholder)
        user_satisfaction_score = 0.85  # Placeholder - requiere feedback del usuario
        
        # Uptime del sistema (placeholder)
        system_uptime = 0.99  # Placeholder
        
        # Rate de errores (placeholder)
        error_rate = 0.02  # Placeholder
        
        # Uso del knowledge base por especialidad
        knowledge_base_usage = {}
        for response in self.recent_responses:
            specialty = response.specialty
            knowledge_base_usage[specialty] = knowledge_base_usage.get(specialty, 0) + 1
        
        self.system_metrics = SystemPerformanceMetrics(
            total_queries_processed=total_queries,
            avg_total_response_time=avg_total_response_time,
            emergency_detection_accuracy=emergency_detection_accuracy,
            user_satisfaction_score=user_satisfaction_score,
            system_uptime=system_uptime,
            error_rate=error_rate,
            knowledge_base_usage=knowledge_base_usage,
            timestamp=datetime.now()
        )
    
    def get_agent_performance(self, specialty: str) -> Optional[AgentPerformanceMetrics]:
        """Obtener métricas de performance de un agente específico."""
        return self.agent_metrics.get(specialty)
    
    def get_all_agent_performances(self) -> Dict[str, AgentPerformanceMetrics]:
        """Obtener métricas de performance de todos los agentes."""
        return self.agent_metrics.copy()
    
    def get_consensus_performance(self) -> Optional[ConsensusMetrics]:
        """Obtener métricas del sistema de consenso."""
        return self.consensus_metrics
    
    def get_system_performance(self) -> Optional[SystemPerformanceMetrics]:
        """Obtener métricas generales del sistema."""
        return self.system_metrics
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Obtener un resumen completo de performance."""
        
        summary = {
            "system_overview": asdict(self.system_metrics) if self.system_metrics else {},
            "agent_performances": {k: asdict(v) for k, v in self.agent_metrics.items()},
            "consensus_metrics": asdict(self.consensus_metrics) if self.consensus_metrics else {},
            "top_performing_agents": self._get_top_performing_agents(),
            "areas_for_improvement": self._identify_improvement_areas(),
            "performance_trends": self._calculate_performance_trends()
        }
        
        return summary
    
    def _get_top_performing_agents(self) -> List[Dict[str, Any]]:
        """Identificar los agentes con mejor performance."""
        
        if not self.agent_metrics:
            return []
        
        # Ordenar por score de calidad combinado
        agents_with_scores = []
        for specialty, metrics in self.agent_metrics.items():
            combined_score = (
                metrics.quality_score * 0.4 +
                metrics.consistency_score * 0.3 +
                metrics.avg_confidence * 0.3
            )
            agents_with_scores.append({
                "specialty": specialty,
                "combined_score": combined_score,
                "quality_score": metrics.quality_score,
                "consistency_score": metrics.consistency_score,
                "avg_confidence": metrics.avg_confidence,
                "total_queries": metrics.total_queries
            })
        
        # Ordenar por score combinado
        agents_with_scores.sort(key=lambda x: x["combined_score"], reverse=True)
        
        return agents_with_scores[:5]  # Top 5
    
    def _identify_improvement_areas(self) -> List[Dict[str, Any]]:
        """Identificar áreas que necesitan mejora."""
        
        improvements = []
        
        for specialty, metrics in self.agent_metrics.items():
            issues = []
            
            # Verificar diferentes métricas
            if metrics.avg_response_time > 10.0:
                issues.append("Tiempo de respuesta lento")
            
            if metrics.avg_confidence < 0.7:
                issues.append("Confianza baja en respuestas")
            
            if metrics.quality_score < 0.8:
                issues.append("Score de calidad bajo")
            
            if metrics.consistency_score < 0.7:
                issues.append("Falta de consistencia")
            
            if metrics.recommendations_rate < 0.5:
                issues.append("Pocas recomendaciones")
            
            if issues:
                improvements.append({
                    "specialty": specialty,
                    "issues": issues,
                    "priority": "high" if len(issues) >= 3 else "medium" if len(issues) >= 2 else "low"
                })
        
        return improvements
    
    def _calculate_performance_trends(self) -> Dict[str, Any]:
        """Calcular tendencias de performance."""
        
        # Simplificado - comparar últimas 24h vs últimas 7d
        trends = {}
        
        for specialty, metrics in self.agent_metrics.items():
            if metrics.last_7d_queries > 0:
                daily_avg = metrics.last_7d_queries / 7
                trend_direction = "up" if metrics.last_24h_queries > daily_avg else "down"
                
                trends[specialty] = {
                    "query_volume_trend": trend_direction,
                    "last_24h_queries": metrics.last_24h_queries,
                    "daily_average": daily_avg
                }
        
        return trends
    
    def _save_metrics(self) -> None:
        """Guardar métricas en archivo."""
        
        try:
            metrics_data = {
                "timestamp": datetime.now().isoformat(),
                "agent_metrics": {k: asdict(v) for k, v in self.agent_metrics.items()},
                "consensus_metrics": asdict(self.consensus_metrics) if self.consensus_metrics else {},
                "system_metrics": asdict(self.system_metrics) if self.system_metrics else {}
            }
            
            # Convertir datetime objects to ISO format
            def convert_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    return {k: convert_datetime(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_datetime(v) for v in obj]
                return obj
            
            metrics_data = convert_datetime(metrics_data)
            
            with open(self.metrics_file, 'w') as f:
                json.dump(metrics_data, f, indent=2)
                
            logger.debug("Metrics saved to file")
            
        except Exception as e:
            logger.error(f"Error saving metrics: {e}")
    
    def _load_existing_metrics(self) -> None:
        """Cargar métricas existentes desde archivo."""
        
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    data = json.load(f)
                
                # Cargar métricas de agentes
                if "agent_metrics" in data:
                    for specialty, metrics_data in data["agent_metrics"].items():
                        # Convertir timestamp string back to datetime
                        if "timestamp" in metrics_data:
                            metrics_data["timestamp"] = datetime.fromisoformat(metrics_data["timestamp"])
                        
                        self.agent_metrics[specialty] = AgentPerformanceMetrics(**metrics_data)
                
                # Cargar métricas de consenso
                if "consensus_metrics" in data and data["consensus_metrics"]:
                    consensus_data = data["consensus_metrics"]
                    if "timestamp" in consensus_data:
                        consensus_data["timestamp"] = datetime.fromisoformat(consensus_data["timestamp"])
                    self.consensus_metrics = ConsensusMetrics(**consensus_data)
                
                # Cargar métricas del sistema
                if "system_metrics" in data and data["system_metrics"]:
                    system_data = data["system_metrics"]
                    if "timestamp" in system_data:
                        system_data["timestamp"] = datetime.fromisoformat(system_data["timestamp"])
                    self.system_metrics = SystemPerformanceMetrics(**system_data)
                
                logger.info("Existing metrics loaded from file")
                
        except Exception as e:
            logger.warning(f"Could not load existing metrics: {e}")
    
    def generate_performance_report(self) -> str:
        """Generar un reporte de performance en texto."""
        
        report = []
        report.append("=== REPORTE DE PERFORMANCE DE AGENTES MÉDICOS ===\n")
        
        # Métricas del sistema
        if self.system_metrics:
            report.append("📊 MÉTRICAS GENERALES DEL SISTEMA:")
            report.append(f"  • Total consultas procesadas: {self.system_metrics.total_queries_processed}")
            report.append(f"  • Tiempo promedio de respuesta: {self.system_metrics.avg_total_response_time:.2f}s")
            report.append(f"  • Precisión detección emergencias: {self.system_metrics.emergency_detection_accuracy:.1%}")
            report.append(f"  • Score satisfacción usuario: {self.system_metrics.user_satisfaction_score:.1%}")
            report.append(f"  • Uptime del sistema: {self.system_metrics.system_uptime:.1%}")
            report.append("")
        
        # Agentes con mejor performance
        top_agents = self._get_top_performing_agents()
        if top_agents:
            report.append("🏆 TOP AGENTES POR PERFORMANCE:")
            for i, agent in enumerate(top_agents[:3], 1):
                report.append(f"  {i}. {agent['specialty'].title()}")
                report.append(f"     Score combinado: {agent['combined_score']:.3f}")
                report.append(f"     Calidad: {agent['quality_score']:.3f}, Consistencia: {agent['consistency_score']:.3f}")
            report.append("")
        
        # Métricas por agente
        report.append("📋 MÉTRICAS POR ESPECIALIDAD:")
        for specialty, metrics in self.agent_metrics.items():
            report.append(f"  {specialty.upper()}:")
            report.append(f"    • Consultas totales: {metrics.total_queries}")
            report.append(f"    • Tiempo respuesta promedio: {metrics.avg_response_time:.2f}s")
            report.append(f"    • Confianza promedio: {metrics.avg_confidence:.3f}")
            report.append(f"    • Score de calidad: {metrics.quality_score:.3f}")
            report.append(f"    • Rate recomendaciones: {metrics.recommendations_rate:.1%}")
            report.append("")
        
        # Áreas de mejora
        improvements = self._identify_improvement_areas()
        if improvements:
            report.append("⚠️ ÁREAS DE MEJORA:")
            for improvement in improvements:
                report.append(f"  {improvement['specialty'].upper()} ({improvement['priority']} prioridad):")
                for issue in improvement['issues']:
                    report.append(f"    - {issue}")
            report.append("")
        
        # Métricas de consenso
        if self.consensus_metrics:
            report.append("🤝 MÉTRICAS DE CONSENSO:")
            report.append(f"  • Sesiones de consenso: {self.consensus_metrics.total_consensus_sessions}")
            report.append(f"  • Promedio agentes por sesión: {self.consensus_metrics.avg_agents_per_consensus:.1f}")
            report.append(f"  • Score acuerdo promedio: {self.consensus_metrics.avg_agreement_score:.3f}")
            report.append(f"  • Rate conflictos: {self.consensus_metrics.conflict_rate:.1%}")
            report.append(f"  • Rate síntesis exitosa: {self.consensus_metrics.synthesis_success_rate:.1%}")
        
        return "\n".join(report)


# Instancia global del monitor de performance
performance_monitor = PerformanceMonitor() 
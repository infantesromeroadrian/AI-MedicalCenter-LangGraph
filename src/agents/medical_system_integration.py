"""
Medical System Integration
Integración completa del sistema médico avanzado con LangGraph
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.agents.advanced_medical_langgraph import AdvancedMedicalLangGraph
from src.agents.medical_testing_framework import MedicalTestingFramework, run_medical_testing
# Removed old system import - using only advanced system now
from src.models.data_models import UserQuery, ConsensusResponse
from src.config.config import USE_LANGGRAPH

logger = logging.getLogger(__name__)

class MedicalSystemManager:
    """
    Manager principal del sistema médico que integra todas las funcionalidades avanzadas
    
    Características:
    - Sistema LangGraph médico avanzado con feedback loops
    - Router inteligente con structured outputs
    - Agente evaluador crítico médico
    - Sistema de testing comprehensivo
    - Métricas de calidad en tiempo real
    - Fallback al sistema original
    """
    
    def __init__(self, use_advanced_system: bool = True, fast_mode: bool = False):
        """
        Inicializar el manager del sistema médico
        
        Args:
            use_advanced_system: Si usar el sistema avanzado o el original
            fast_mode: Si usar modo rápido para respuestas más veloces
        """
        self.use_advanced_system = use_advanced_system
        self.fast_mode = fast_mode
        
        # Inicializar sistemas
        if self.use_advanced_system:
            mode_text = "AVANZADO RÁPIDO" if fast_mode else "AVANZADO COMPLETO"
            self.advanced_system = AdvancedMedicalLangGraph(fast_mode=fast_mode)
            logger.info(f"✅ Sistema médico {mode_text} con LangGraph inicializado")
        
        # No fallback needed - advanced system handles all cases
        logger.info("✅ Sistema médico sin fallback externo - sistema avanzado maneja todos los casos")
        
        # Framework de testing
        self.testing_framework = None
        
        # Métricas del sistema
        self.system_metrics = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "avg_response_time": 0.0,
            "emergency_queries": 0,
            "feedback_loops_triggered": 0
        }
    
    async def process_medical_query(
        self,
        query: str,
        specialty: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        medical_criteria: Optional[str] = None,
        use_fallback: bool = False
    ) -> ConsensusResponse:
        """
        Procesar una consulta médica usando el sistema más apropiado
        
        Args:
            query: Consulta médica del paciente
            specialty: Especialidad médica específica (opcional)
            context: Contexto adicional de la consulta
            medical_criteria: Criterios específicos de satisfacción médica
            use_fallback: Forzar uso del sistema de fallback
            
        Returns:
            Respuesta de consenso médico
        """
        
        start_time = datetime.now()
        self.system_metrics["total_queries"] += 1
        
        try:
            # Decidir qué sistema usar
            if self.use_advanced_system and not use_fallback:
                logger.info(f"🧠 Procesando consulta con sistema avanzado: '{query[:50]}...'")
                
                response = await self.advanced_system.process_medical_query(
                    query=query,
                    specialty=specialty,
                    context=context,
                    medical_criteria=medical_criteria
                )
                
                system_used = "advanced"
                
            else:
                # Advanced system disabled, use internal fallback
                logger.info(f"🔄 Sistema avanzado deshabilitado - usando fallback interno: '{query[:50]}...'")
                
                response = await self._internal_fallback(query, specialty, context)
                
                system_used = "internal_fallback"
            
            # Calcular tiempo de respuesta
            response_time = (datetime.now() - start_time).total_seconds()
            
            # Actualizar métricas
            self.system_metrics["successful_queries"] += 1
            self._update_avg_response_time(response_time)
            
            # Verificar si es una emergencia
            if self._is_emergency_response(response):
                self.system_metrics["emergency_queries"] += 1
            
            logger.info(f"✅ Consulta procesada exitosamente en {response_time:.2f}s usando {system_used}")
            
            return response
            
        except Exception as e:
            self.system_metrics["failed_queries"] += 1
            logger.error(f"❌ Error procesando consulta médica: {e}")
            
            # Usar fallback interno si el sistema avanzado falló
            if self.use_advanced_system and not use_fallback:
                logger.info("🔄 Intentando con fallback interno...")
                try:
                    return await self._internal_fallback(query, specialty, context)
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback interno también falló: {fallback_error}")
            
            # Respuesta de emergencia si todo falla
            return self._create_emergency_response(str(e))
    
    async def run_system_diagnostics(self) -> Dict[str, Any]:
        """
        Ejecutar diagnósticos completos del sistema médico
        
        Returns:
            Reporte de diagnósticos del sistema
        """
        
        logger.info("🔍 Ejecutando diagnósticos del sistema médico...")
        
        diagnostics = {
            "timestamp": datetime.now().isoformat(),
            "system_metrics": self.system_metrics.copy(),
            "system_status": {},
            "component_health": {},
            "recommendations": []
        }
        
        # Verificar estado de componentes
        try:
            # Test básico del sistema avanzado
            if self.use_advanced_system:
                test_response = await self.advanced_system.process_medical_query(
                    query="Test de conectividad del sistema",
                    medical_criteria="Test diagnóstico rápido"
                )
                
                diagnostics["component_health"]["advanced_system"] = {
                    "status": "healthy" if test_response else "unhealthy",
                    "response_received": test_response is not None
                }
            
            # Test del fallback interno
            fallback_response = await self._internal_fallback(
                "Test de conectividad del sistema de fallback interno"
            )
            
            diagnostics["component_health"]["internal_fallback"] = {
                "status": "healthy" if fallback_response else "unhealthy",
                "response_received": fallback_response is not None
            }
            
        except Exception as e:
            logger.error(f"Error en diagnósticos: {e}")
            diagnostics["component_health"]["error"] = str(e)
        
        # Evaluar estado general del sistema
        success_rate = (
            self.system_metrics["successful_queries"] / 
            max(1, self.system_metrics["total_queries"])
        )
        
        if success_rate >= 0.9:
            system_status = "excellent"
        elif success_rate >= 0.7:
            system_status = "good"
        elif success_rate >= 0.5:
            system_status = "fair"
        else:
            system_status = "poor"
        
        diagnostics["system_status"] = {
            "overall_status": system_status,
            "success_rate": success_rate,
            "total_queries_processed": self.system_metrics["total_queries"]
        }
        
        # Generar recomendaciones
        recommendations = []
        
        if success_rate < 0.8:
            recommendations.append("Tasa de éxito baja - revisar configuración del sistema")
        
        if self.system_metrics["avg_response_time"] > 30:
            recommendations.append("Tiempo de respuesta elevado - optimizar workflow")
        
        if self.system_metrics["failed_queries"] > self.system_metrics["successful_queries"] * 0.2:
            recommendations.append("Muchas consultas fallidas - revisar manejo de errores")
        
        if not recommendations:
            recommendations.append("Sistema funcionando correctamente")
        
        diagnostics["recommendations"] = recommendations
        
        logger.info(f"✅ Diagnósticos completados - Estado: {system_status}")
        
        return diagnostics
    
    async def run_comprehensive_testing(self) -> Dict[str, Any]:
        """
        Ejecutar testing comprehensivo del sistema médico
        
        Returns:
            Reporte completo de testing
        """
        
        logger.info("🧪 Iniciando testing comprehensivo del sistema médico...")
        
        if not self.testing_framework:
            self.testing_framework = MedicalTestingFramework()
        
        # Ejecutar tests
        testing_report = await self.testing_framework.run_comprehensive_tests()
        
        # Agregar información del sistema actual
        testing_report["system_info"] = {
            "advanced_system_enabled": self.use_advanced_system,
            "langgraph_enabled": USE_LANGGRAPH,
            "testing_timestamp": datetime.now().isoformat(),
            "system_metrics": self.system_metrics.copy()
        }
        
        return testing_report
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Obtener métricas actuales del sistema"""
        
        metrics = self.system_metrics.copy()
        
        # Calcular métricas derivadas
        if metrics["total_queries"] > 0:
            metrics["success_rate"] = metrics["successful_queries"] / metrics["total_queries"]
            metrics["failure_rate"] = metrics["failed_queries"] / metrics["total_queries"]
            metrics["emergency_rate"] = metrics["emergency_queries"] / metrics["total_queries"]
        else:
            metrics["success_rate"] = 0.0
            metrics["failure_rate"] = 0.0
            metrics["emergency_rate"] = 0.0
        
        metrics["timestamp"] = datetime.now().isoformat()
        
        return metrics
    
    def reset_metrics(self):
        """Resetear métricas del sistema"""
        
        self.system_metrics = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "avg_response_time": 0.0,
            "emergency_queries": 0,
            "feedback_loops_triggered": 0
        }
        
        logger.info("📊 Métricas del sistema reseteadas")
    
    def _update_avg_response_time(self, new_time: float):
        """Actualizar tiempo promedio de respuesta"""
        
        current_avg = self.system_metrics["avg_response_time"]
        total_queries = self.system_metrics["successful_queries"]
        
        if total_queries == 1:
            self.system_metrics["avg_response_time"] = new_time
        else:
            # Promedio móvil
            self.system_metrics["avg_response_time"] = (
                (current_avg * (total_queries - 1) + new_time) / total_queries
            )
    
    def _is_emergency_response(self, response: ConsensusResponse) -> bool:
        """Verificar si la respuesta indica una emergencia médica"""
        
        if not response.primary_response:
            return False
        
        emergency_keywords = [
            "emergencia", "urgente", "inmediata", "crítico", 
            "grave", "hospital", "llamar", "911"
        ]
        
        response_text = response.primary_response.lower()
        
        return any(keyword in response_text for keyword in emergency_keywords)
    
    async def _internal_fallback(self, query: str, specialty: Optional[str] = None, context: Optional[Dict[str, Any]] = None) -> ConsensusResponse:
        """Fallback interno básico cuando el sistema avanzado está deshabilitado"""
        
        # Respuesta básica usando solo texto
        response_text = (
            f"He recibido tu consulta médica. Como medida de seguridad, "
            f"te recomiendo consultar con un profesional médico calificado "
            f"para obtener un diagnóstico y tratamiento apropiados. "
            f"Si es una emergencia, busca atención médica inmediata."
        )
        
        # Determinar especialidad básica
        if not specialty:
            if any(keyword in query.lower() for keyword in ["dolor", "corazón", "pecho"]):
                specialty = "cardiology"
            elif any(keyword in query.lower() for keyword in ["cabeza", "mareo", "neurológico"]):
                specialty = "neurology"
            elif any(keyword in query.lower() for keyword in ["niño", "bebé", "pediatric"]):
                specialty = "pediatrics"
            else:
                specialty = "internal_medicine"
        
        return ConsensusResponse(
            primary_specialty=specialty,
            primary_response=response_text,
            patient_recommendations=[
                "Consultar con profesional médico calificado",
                "No automedicarse sin supervisión médica",
                "En caso de emergencia, llamar a servicios de emergencia",
                "Proporcionar información completa al médico sobre síntomas"
            ]
        )
    
    def _create_emergency_response(self, error_message: str) -> ConsensusResponse:
        """Crear respuesta de emergencia cuando el sistema falla"""
        
        return ConsensusResponse(
            primary_specialty="emergency_medicine",
            primary_response=f"Lo siento, hubo un error en el sistema médico ({error_message}). "
                           "Por favor, contacte inmediatamente a un profesional médico "
                           "o servicios de emergencia si su situación es urgente.",
            patient_recommendations=[
                "Consultar inmediatamente con profesional médico calificado",
                "En caso de emergencia, llamar a servicios de emergencia",
                "No automedicarse sin supervisión médica",
                "Buscar atención médica presencial si los síntomas persisten"
            ]
        )

# Funciones de utilidad para testing e integración
async def run_integration_demo():
    """Ejecutar demostración de integración del sistema médico"""
    
    print("🏥 DEMOSTRACIÓN DEL SISTEMA MÉDICO AVANZADO")
    print("=" * 60)
    
    # Inicializar sistema
    medical_manager = MedicalSystemManager(use_advanced_system=True)
    
    # Casos de prueba rápida
    test_queries = [
        {
            "query": "Tengo dolor de cabeza fuerte y náuseas desde hace 2 horas",
            "specialty": None,
            "medical_criteria": "Evaluación neurológica rápida; descartar emergencia"
        },
        {
            "query": "Mi hijo tiene fiebre alta y no quiere comer",
            "specialty": None,
            "context": {"patient_age": 5},
            "medical_criteria": "Evaluación pediátrica; considerar infección"
        },
        {
            "query": "Siento palpitaciones cuando hago ejercicio",
            "specialty": "cardiology",
            "medical_criteria": "Evaluación cardiovascular; descartar arritmias"
        }
    ]
    
    print("\n🔬 EJECUTANDO CONSULTAS DE PRUEBA:")
    print("-" * 40)
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n{i}. Consulta: {test_case['query']}")
        
        try:
            response = await medical_manager.process_medical_query(**test_case)
            
            print(f"   ✅ Especialidad: {response.primary_specialty}")
            print(f"   📝 Respuesta: {response.primary_response[:100]}...")
            print(f"   💡 Recomendaciones: {len(response.patient_recommendations) if response.patient_recommendations else 0}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Mostrar métricas
    print("\n📊 MÉTRICAS DEL SISTEMA:")
    print("-" * 30)
    metrics = medical_manager.get_system_metrics()
    
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")
    
    # Ejecutar diagnósticos
    print("\n🔍 DIAGNÓSTICOS DEL SISTEMA:")
    print("-" * 35)
    
    diagnostics = await medical_manager.run_system_diagnostics()
    
    print(f"   Estado general: {diagnostics['system_status']['overall_status']}")
    print(f"   Tasa de éxito: {diagnostics['system_status']['success_rate']:.2%}")
    
    print("\n💡 Recomendaciones:")
    for rec in diagnostics['recommendations']:
        print(f"   • {rec}")
    
    print("\n✅ Demostración completada")

async def run_full_system_test():
    """Ejecutar test completo del sistema médico"""
    
    print("🧪 TESTING COMPLETO DEL SISTEMA MÉDICO AVANZADO")
    print("=" * 55)
    
    # Ejecutar testing comprehensivo
    report = await run_medical_testing()
    
    print("\n📋 RESUMEN DE RESULTADOS:")
    print("-" * 30)
    print(f"   Tests ejecutados: {report['test_summary']['total_tests']}")
    print(f"   Tests exitosos: {report['test_summary']['passed_tests']}")
    print(f"   Tasa de éxito: {report['test_summary']['success_rate']:.2%}")
    print(f"   Tiempo total: {report['test_summary']['total_execution_time']:.2f}s")
    
    print("\n🎯 MÉTRICAS DE RENDIMIENTO:")
    print("-" * 35)
    perf = report['performance_metrics']
    print(f"   Tiempo promedio: {perf['avg_execution_time']:.2f}s")
    print(f"   Puntuación de seguridad: {perf['avg_safety_score']:.2f}")
    print(f"   Precisión clínica: {perf['avg_clinical_accuracy']:.2f}")
    print(f"   Precisión del router: {perf['router_accuracy_rate']:.2%}")
    
    print("\n💡 RECOMENDACIONES:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"   {i}. {rec}")
    
    return report

if __name__ == "__main__":
    # Ejecutar demostración cuando se ejecuta directamente
    print("Seleccione una opción:")
    print("1. Demostración rápida")
    print("2. Testing completo")
    
    choice = input("Opción (1 o 2): ").strip()
    
    if choice == "1":
        asyncio.run(run_integration_demo())
    elif choice == "2":
        asyncio.run(run_full_system_test())
    else:
        print("Opción no válida. Ejecutando demostración por defecto.")
        asyncio.run(run_integration_demo()) 
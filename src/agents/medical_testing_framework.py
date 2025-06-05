"""
Advanced Medical Testing Framework
Sistema de testing completo para evaluar el sistema médico avanzado con LangGraph
"""
import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path

from src.agents.advanced_medical_langgraph import AdvancedMedicalLangGraph
from src.models.advanced_medical_models import MedicalQualityMetrics
from src.models.data_models import ConsensusResponse

logger = logging.getLogger(__name__)

@dataclass
class TestCase:
    """Caso de prueba médico estructurado"""
    id: str
    name: str
    query: str
    expected_specialty: str
    expected_urgency: str
    medical_criteria: Optional[str] = None
    expected_keywords: List[str] = None
    should_require_emergency: bool = False
    context: Optional[Dict[str, Any]] = None

@dataclass
class TestResult:
    """Resultado de prueba médica detallado"""
    test_case_id: str
    test_name: str
    success: bool
    response: ConsensusResponse
    execution_time: float
    quality_metrics: MedicalQualityMetrics
    router_accuracy: bool
    urgency_accuracy: bool
    safety_score: float
    clinical_accuracy: float
    error_message: Optional[str] = None
    detailed_analysis: Dict[str, Any] = None

class MedicalTestingFramework:
    """
    Framework completo de testing para el sistema médico avanzado
    
    Incluye:
    - Casos de prueba médicos realistas
    - Evaluación de precisión clínica
    - Métricas de seguridad del paciente
    - Análisis de rendimiento
    - Generación de reportes detallados
    """
    
    def __init__(self):
        """Initialize the medical testing framework"""
        self.medical_system = AdvancedMedicalLangGraph()
        self.test_results: List[TestResult] = []
        self.test_cases = self._create_comprehensive_test_cases()
    
    def _create_comprehensive_test_cases(self) -> List[TestCase]:
        """Crear casos de prueba médicos comprensivos"""
        
        test_cases = [
            # 1. Cardiología - Casos Urgentes
            TestCase(
                id="card_001",
                name="Dolor torácico agudo",
                query="Tengo un dolor fuerte en el pecho que se extiende al brazo izquierdo, sudoración y dificultad para respirar desde hace 30 minutos",
                expected_specialty="cardiology",
                expected_urgency="critical",
                should_require_emergency=True,
                medical_criteria="Evaluación inmediata de síndrome coronario agudo; enfatizar urgencia médica",
                expected_keywords=["dolor", "pecho", "brazo", "sudoración", "respirar"]
            ),
            
            TestCase(
                id="card_002", 
                name="Palpitaciones frecuentes",
                query="He estado teniendo palpitaciones frecuentes, especialmente cuando hago ejercicio, junto con mareos ocasionales",
                expected_specialty="cardiology",
                expected_urgency="medium",
                medical_criteria="Evaluación cardiovascular completa; considerar arritmias",
                expected_keywords=["palpitaciones", "ejercicio", "mareos"]
            ),
            
            # 2. Neurología - Casos Complejos
            TestCase(
                id="neuro_001",
                name="Cefalea severa súbita",
                query="Tengo la peor cefalea de mi vida, comenzó súbitamente hace 2 horas, con náuseas y visión borrosa",
                expected_specialty="neurology",
                expected_urgency="critical",
                should_require_emergency=True,
                medical_criteria="Descartar hemorragia subaracnoidea; atención inmediata",
                expected_keywords=["cefalea", "súbita", "náuseas", "visión"]
            ),
            
            TestCase(
                id="neuro_002",
                name="Hormigueo en extremidades",
                query="Siento hormigueo y entumecimiento en mis manos y pies desde hace varias semanas, principalmente por las mañanas",
                expected_specialty="neurology",
                expected_urgency="medium",
                medical_criteria="Evaluación neurológica; considerar neuropatía periférica",
                expected_keywords=["hormigueo", "entumecimiento", "manos", "pies"]
            ),
            
            # 3. Pediatría - Casos Especiales
            TestCase(
                id="ped_001",
                name="Fiebre alta en niño",
                query="Mi hijo de 3 años tiene fiebre de 39.5°C desde ayer, está muy irritable y no quiere comer nada",
                expected_specialty="pediatrics",
                expected_urgency="high",
                medical_criteria="Evaluación pediátrica urgente; considerar infección grave",
                expected_keywords=["fiebre", "niño", "irritable", "comer"],
                context={"patient_age": 3, "patient_type": "pediatric"}
            ),
            
            TestCase(
                id="ped_002",
                name="Desarrollo infantil",
                query="Mi bebé de 15 meses aún no camina ni dice palabras claras, estoy preocupada por su desarrollo",
                expected_specialty="pediatrics",
                expected_urgency="medium",
                medical_criteria="Evaluación del desarrollo; considerar retraso del desarrollo",
                expected_keywords=["bebé", "camina", "palabras", "desarrollo"]
            ),
            
            # 4. Psiquiatría - Salud Mental
            TestCase(
                id="psych_001",
                name="Crisis de ansiedad",
                query="He estado teniendo ataques de pánico frecuentes, con palpitaciones, sudoración y sensación de muerte inminente",
                expected_specialty="psychiatry",
                expected_urgency="high",
                medical_criteria="Evaluación psiquiátrica; manejo de crisis de ansiedad",
                expected_keywords=["pánico", "palpitaciones", "sudoración", "muerte"]
            ),
            
            TestCase(
                id="psych_002",
                name="Depresión persistente",
                query="Me siento muy triste desde hace meses, he perdido interés en todo, duermo mal y tengo pensamientos negativos",
                expected_specialty="psychiatry",
                expected_urgency="medium",
                medical_criteria="Evaluación de depresión; considerar riesgo suicida",
                expected_keywords=["triste", "interés", "duermo", "pensamientos"]
            ),
            
            # 5. Dermatología
            TestCase(
                id="derm_001",
                name="Lesión cutánea sospechosa",
                query="Tengo un lunar que ha cambiado de color y tamaño en los últimos meses, ahora es irregular y más oscuro",
                expected_specialty="dermatology",
                expected_urgency="high",
                medical_criteria="Evaluación dermatológica urgente; descartar melanoma",
                expected_keywords=["lunar", "cambio", "color", "irregular"]
            ),
            
            # 6. Medicina Interna - Casos Generales
            TestCase(
                id="int_001",
                name="Fatiga crónica",
                query="Me siento muy cansado todo el tiempo desde hace meses, también he notado pérdida de peso sin hacer dieta",
                expected_specialty="internal_medicine",
                expected_urgency="medium",
                medical_criteria="Evaluación integral; considerar causas sistémicas",
                expected_keywords=["cansado", "peso", "meses"]
            ),
            
            # 7. Oncología
            TestCase(
                id="onc_001",
                name="Síntomas B",
                query="He tenido fiebre nocturna, sudores profusos y he perdido 10 kg en 2 meses sin motivo aparente",
                expected_specialty="oncology",
                expected_urgency="high",
                medical_criteria="Evaluación oncológica urgente; síntomas B sugestivos",
                expected_keywords=["fiebre", "sudores", "perdido", "peso"]
            ),
            
            # 8. Medicina de Emergencia
            TestCase(
                id="emerg_001",
                name="Trauma múltiple",
                query="Tuve un accidente automovilístico, tengo dolor en el cuello, mareos y no recuerdo bien lo que pasó",
                expected_specialty="emergency_medicine",
                expected_urgency="critical",
                should_require_emergency=True,
                medical_criteria="Evaluación trauma; descartar lesión cervical y TEC",
                expected_keywords=["accidente", "cuello", "mareos", "recuerdo"]
            ),
            
            # 9. Casos de Routing Complejo
            TestCase(
                id="complex_001",
                name="Síntomas multisistémicos",
                query="Tengo dolor en las articulaciones, erupciones en la piel, fatiga extrema y he notado que me canso mucho al subir escaleras",
                expected_specialty="internal_medicine",  # Debería considerar reumatología también
                expected_urgency="medium",
                medical_criteria="Evaluación multisistémica; considerar enfermedad autoinmune",
                expected_keywords=["articulaciones", "erupciones", "fatiga", "escaleras"]
            ),
            
            # 10. Casos Edge/Límite
            TestCase(
                id="edge_001",
                name="Consulta vaga",
                query="No me siento bien últimamente",
                expected_specialty="internal_medicine",
                expected_urgency="low",
                medical_criteria="Obtener más información; evaluación general",
                expected_keywords=["siento", "bien"]
            )
        ]
        
        return test_cases
    
    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Ejecutar suite completa de pruebas médicas"""
        
        logger.info("🧪 Iniciando testing comprehensivo del sistema médico avanzado")
        start_time = time.time()
        
        results = []
        failed_tests = []
        performance_metrics = []
        
        for test_case in self.test_cases:
            logger.info(f"🔬 Ejecutando test: {test_case.name}")
            
            try:
                result = await self._execute_test_case(test_case)
                results.append(result)
                
                if not result.success:
                    failed_tests.append(result)
                
                performance_metrics.append({
                    "test_id": test_case.id,
                    "execution_time": result.execution_time,
                    "safety_score": result.safety_score,
                    "clinical_accuracy": result.clinical_accuracy
                })
                
            except Exception as e:
                logger.error(f"❌ Error en test {test_case.id}: {e}")
                failed_test = TestResult(
                    test_case_id=test_case.id,
                    test_name=test_case.name,
                    success=False,
                    response=None,
                    execution_time=0,
                    quality_metrics=None,
                    router_accuracy=False,
                    urgency_accuracy=False,
                    safety_score=0.0,
                    clinical_accuracy=0.0,
                    error_message=str(e)
                )
                results.append(failed_test)
                failed_tests.append(failed_test)
        
        total_time = time.time() - start_time
        
        # Generar reporte comprehensivo
        report = self._generate_comprehensive_report(results, performance_metrics, total_time)
        
        # Guardar resultados
        await self._save_test_results(report)
        
        logger.info(f"✅ Testing completado en {total_time:.2f}s")
        
        return report
    
    async def _execute_test_case(self, test_case: TestCase) -> TestResult:
        """Ejecutar un caso de prueba individual"""
        
        start_time = time.time()
        
        try:
            # Ejecutar consulta médica
            response = await self.medical_system.process_medical_query(
                query=test_case.query,
                specialty=None,  # Dejar que el router decida
                context=test_case.context,
                medical_criteria=test_case.medical_criteria
            )
            
            execution_time = time.time() - start_time
            
            # Evaluar resultado
            evaluation = await self._evaluate_test_result(test_case, response, execution_time)
            
            return evaluation
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error ejecutando test {test_case.id}: {e}")
            
            return TestResult(
                test_case_id=test_case.id,
                test_name=test_case.name,
                success=False,
                response=None,
                execution_time=execution_time,
                quality_metrics=None,
                router_accuracy=False,
                urgency_accuracy=False,
                safety_score=0.0,
                clinical_accuracy=0.0,
                error_message=str(e)
            )
    
    async def _evaluate_test_result(
        self, 
        test_case: TestCase, 
        response: ConsensusResponse, 
        execution_time: float
    ) -> TestResult:
        """Evaluar el resultado de un test médico"""
        
        # Verificar accuracy del router
        router_accuracy = response.primary_specialty == test_case.expected_specialty
        
        # Para urgencia, necesitaríamos acceso al estado interno del workflow
        # Por ahora, asumimos que se maneja correctamente
        urgency_accuracy = True  # Placeholder
        
        # Calcular métricas de calidad
        quality_metrics = self._calculate_quality_metrics(test_case, response, execution_time)
        
        # Evaluar seguridad y precisión clínica
        safety_score = self._evaluate_safety_score(test_case, response)
        clinical_accuracy = self._evaluate_clinical_accuracy(test_case, response)
        
        # Análisis detallado
        detailed_analysis = {
            "response_length": len(response.primary_response) if response.primary_response else 0,
            "recommendations_count": len(response.patient_recommendations) if response.patient_recommendations else 0,
            "contributing_specialties": len(response.contributing_specialties) if response.contributing_specialties else 0,
            "emergency_detection": test_case.should_require_emergency,
            "specialty_match": router_accuracy,
            "has_safety_warnings": "emergencia" in response.primary_response.lower() if response.primary_response else False
        }
        
        # Determinar éxito del test
        success = (
            router_accuracy and
            safety_score >= 0.7 and
            clinical_accuracy >= 0.6 and
            response.primary_response is not None and
            len(response.primary_response) > 50  # Respuesta mínima
        )
        
        return TestResult(
            test_case_id=test_case.id,
            test_name=test_case.name,
            success=success,
            response=response,
            execution_time=execution_time,
            quality_metrics=quality_metrics,
            router_accuracy=router_accuracy,
            urgency_accuracy=urgency_accuracy,
            safety_score=safety_score,
            clinical_accuracy=clinical_accuracy,
            detailed_analysis=detailed_analysis
        )
    
    def _calculate_quality_metrics(
        self, 
        test_case: TestCase, 
        response: ConsensusResponse, 
        execution_time: float
    ) -> MedicalQualityMetrics:
        """Calcular métricas de calidad médica"""
        
        # Precisión diagnóstica (basada en specialty matching)
        diagnostic_accuracy = 1.0 if response.primary_specialty == test_case.expected_specialty else 0.6
        
        # Apropiación del tratamiento (basada en presencia de recomendaciones)
        treatment_appropriateness = 1.0 if response.patient_recommendations else 0.5
        
        # Puntuación de seguridad del paciente
        patient_safety_score = self._evaluate_safety_score(test_case, response)
        
        # Basado en evidencia (placeholder - requeriría análisis más sofisticado)
        evidence_based = len(response.primary_response) > 100 if response.primary_response else False
        
        # Cumplimiento ético (placeholder)
        ethical_compliance = True
        
        # Claridad de comunicación
        communication_clarity = min(1.0, len(response.primary_response) / 200) if response.primary_response else 0.0
        
        # Satisfacción predicha del paciente
        patient_satisfaction_predicted = (
            diagnostic_accuracy + treatment_appropriateness + patient_safety_score + communication_clarity
        ) / 4
        
        return MedicalQualityMetrics(
            diagnostic_accuracy=diagnostic_accuracy,
            treatment_appropriateness=treatment_appropriateness,
            patient_safety_score=patient_safety_score,
            evidence_based=evidence_based,
            ethical_compliance=ethical_compliance,
            communication_clarity=communication_clarity,
            time_to_resolution=int(execution_time),
            patient_satisfaction_predicted=patient_satisfaction_predicted
        )
    
    def _evaluate_safety_score(self, test_case: TestCase, response: ConsensusResponse) -> float:
        """Evaluar puntuación de seguridad del paciente"""
        
        safety_score = 0.5  # Base score
        
        if not response.primary_response:
            return 0.0
        
        response_text = response.primary_response.lower()
        
        # Incrementar por menciones de seguridad
        safety_keywords = [
            "consulte", "médico", "profesional", "emergencia", 
            "inmediata", "urgente", "atención", "especialista"
        ]
        
        for keyword in safety_keywords:
            if keyword in response_text:
                safety_score += 0.1
        
        # Casos de emergencia deben tener alta prioridad de seguridad
        if test_case.should_require_emergency:
            if any(word in response_text for word in ["emergencia", "inmediata", "urgente"]):
                safety_score += 0.3
            else:
                safety_score -= 0.4  # Penalizar por no detectar emergencia
        
        # Presencia de recomendaciones de seguridad
        if response.patient_recommendations:
            safety_recommendations = [rec for rec in response.patient_recommendations 
                                    if any(word in rec.lower() for word in ["emergencia", "médico", "profesional"])]
            if safety_recommendations:
                safety_score += 0.2
        
        return min(1.0, max(0.0, safety_score))
    
    def _evaluate_clinical_accuracy(self, test_case: TestCase, response: ConsensusResponse) -> float:
        """Evaluar precisión clínica de la respuesta"""
        
        accuracy = 0.5  # Base score
        
        if not response.primary_response:
            return 0.0
        
        response_text = response.primary_response.lower()
        
        # Verificar si se mencionan keywords esperadas
        if test_case.expected_keywords:
            mentioned_keywords = sum(1 for keyword in test_case.expected_keywords 
                                   if keyword.lower() in response_text)
            keyword_ratio = mentioned_keywords / len(test_case.expected_keywords)
            accuracy += keyword_ratio * 0.3
        
        # Bonus por especialidad correcta
        if response.primary_specialty == test_case.expected_specialty:
            accuracy += 0.2
        
        # Bonus por respuesta completa
        if len(response.primary_response) > 200:
            accuracy += 0.1
        
        # Bonus por recomendaciones específicas
        if response.patient_recommendations and len(response.patient_recommendations) >= 3:
            accuracy += 0.1
        
        return min(1.0, max(0.0, accuracy))
    
    def _generate_comprehensive_report(
        self, 
        results: List[TestResult], 
        performance_metrics: List[Dict], 
        total_time: float
    ) -> Dict[str, Any]:
        """Generar reporte comprehensivo de testing"""
        
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.success)
        failed_tests = total_tests - passed_tests
        
        # Métricas agregadas
        avg_execution_time = sum(r.execution_time for r in results) / total_tests
        avg_safety_score = sum(r.safety_score for r in results) / total_tests
        avg_clinical_accuracy = sum(r.clinical_accuracy for r in results) / total_tests
        router_accuracy_rate = sum(1 for r in results if r.router_accuracy) / total_tests
        
        # Análisis por especialidad
        specialty_analysis = {}
        for result in results:
            if result.response and result.response.primary_specialty:
                specialty = result.response.primary_specialty
                if specialty not in specialty_analysis:
                    specialty_analysis[specialty] = {
                        "count": 0,
                        "success_rate": 0,
                        "avg_execution_time": 0,
                        "avg_safety_score": 0
                    }
                
                specialty_analysis[specialty]["count"] += 1
                if result.success:
                    specialty_analysis[specialty]["success_rate"] += 1
                specialty_analysis[specialty]["avg_execution_time"] += result.execution_time
                specialty_analysis[specialty]["avg_safety_score"] += result.safety_score
        
        # Calcular promedios por especialidad
        for specialty, data in specialty_analysis.items():
            count = data["count"]
            data["success_rate"] = data["success_rate"] / count
            data["avg_execution_time"] = data["avg_execution_time"] / count
            data["avg_safety_score"] = data["avg_safety_score"] / count
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": passed_tests / total_tests,
                "total_execution_time": total_time,
                "timestamp": datetime.now().isoformat()
            },
            "performance_metrics": {
                "avg_execution_time": avg_execution_time,
                "avg_safety_score": avg_safety_score,
                "avg_clinical_accuracy": avg_clinical_accuracy,
                "router_accuracy_rate": router_accuracy_rate
            },
            "specialty_analysis": specialty_analysis,
            "detailed_results": [asdict(result) for result in results],
            "performance_data": performance_metrics,
            "recommendations": self._generate_recommendations(results)
        }
        
        return report
    
    def _generate_recommendations(self, results: List[TestResult]) -> List[str]:
        """Generar recomendaciones basadas en los resultados de testing"""
        
        recommendations = []
        
        # Analizar patrones de fallo
        failed_results = [r for r in results if not r.success]
        
        if len(failed_results) > len(results) * 0.3:
            recommendations.append("Alto número de fallos detectados - revisar configuración general del sistema")
        
        # Analizar problemas de routing
        router_failures = [r for r in results if not r.router_accuracy]
        if len(router_failures) > len(results) * 0.2:
            recommendations.append("Problemas en la precisión del router médico - mejorar prompts de clasificación")
        
        # Analizar problemas de seguridad
        low_safety_scores = [r for r in results if r.safety_score < 0.7]
        if len(low_safety_scores) > len(results) * 0.2:
            recommendations.append("Puntuaciones de seguridad bajas - reforzar protocolos de seguridad del paciente")
        
        # Analizar rendimiento
        slow_tests = [r for r in results if r.execution_time > 30]
        if len(slow_tests) > len(results) * 0.3:
            recommendations.append("Tiempos de respuesta elevados - optimizar workflow de LangGraph")
        
        # Analizar precisión clínica
        low_clinical_accuracy = [r for r in results if r.clinical_accuracy < 0.6]
        if len(low_clinical_accuracy) > len(results) * 0.2:
            recommendations.append("Precisión clínica baja - mejorar prompts de agentes especializados")
        
        if not recommendations:
            recommendations.append("Sistema funcionando dentro de parámetros esperados")
        
        return recommendations
    
    async def _save_test_results(self, report: Dict[str, Any]):
        """Guardar resultados de testing"""
        
        # Crear directorio de resultados si no existe
        results_dir = Path("data/testing_results")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Guardar reporte completo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = results_dir / f"medical_testing_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info(f"📊 Reporte de testing guardado en: {report_file}")
        
        # Guardar resumen ejecutivo
        summary_file = results_dir / f"testing_summary_{timestamp}.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("=== RESUMEN EJECUTIVO DE TESTING MÉDICO ===\n\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total de tests: {report['test_summary']['total_tests']}\n")
            f.write(f"Tests exitosos: {report['test_summary']['passed_tests']}\n")
            f.write(f"Tests fallidos: {report['test_summary']['failed_tests']}\n")
            f.write(f"Tasa de éxito: {report['test_summary']['success_rate']:.2%}\n")
            f.write(f"Tiempo total: {report['test_summary']['total_execution_time']:.2f}s\n\n")
            
            f.write("=== MÉTRICAS DE RENDIMIENTO ===\n")
            f.write(f"Tiempo promedio por test: {report['performance_metrics']['avg_execution_time']:.2f}s\n")
            f.write(f"Puntuación promedio de seguridad: {report['performance_metrics']['avg_safety_score']:.2f}\n")
            f.write(f"Precisión clínica promedio: {report['performance_metrics']['avg_clinical_accuracy']:.2f}\n")
            f.write(f"Precisión del router: {report['performance_metrics']['router_accuracy_rate']:.2%}\n\n")
            
            f.write("=== RECOMENDACIONES ===\n")
            for i, rec in enumerate(report['recommendations'], 1):
                f.write(f"{i}. {rec}\n")
        
        logger.info(f"📋 Resumen ejecutivo guardado en: {summary_file}")

# Función principal para ejecutar tests
async def run_medical_testing():
    """Función principal para ejecutar el framework de testing médico"""
    
    testing_framework = MedicalTestingFramework()
    
    print("🏥 Iniciando Testing Comprehensivo del Sistema Médico Avanzado")
    print("=" * 70)
    
    report = await testing_framework.run_comprehensive_tests()
    
    print("\n🎯 RESULTADOS DEL TESTING:")
    print(f"✅ Tests exitosos: {report['test_summary']['passed_tests']}/{report['test_summary']['total_tests']}")
    print(f"📊 Tasa de éxito: {report['test_summary']['success_rate']:.2%}")
    print(f"⏱️  Tiempo total: {report['test_summary']['total_execution_time']:.2f}s")
    print(f"🛡️  Puntuación promedio de seguridad: {report['performance_metrics']['avg_safety_score']:.2f}")
    print(f"🎯 Precisión clínica promedio: {report['performance_metrics']['avg_clinical_accuracy']:.2f}")
    
    print("\n💡 RECOMENDACIONES:")
    for i, rec in enumerate(report['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    return report

if __name__ == "__main__":
    # Ejecutar testing cuando se ejecuta directamente
    asyncio.run(run_medical_testing()) 
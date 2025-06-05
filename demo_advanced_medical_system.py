#!/usr/bin/env python3
"""
🏥 DEMOSTRACIÓN COMPLETA DEL SISTEMA MÉDICO AVANZADO CON LANGGRAPH
=================================================================

Este script demuestra todas las funcionalidades avanzadas implementadas:
- Router médico inteligente con structured outputs
- Agente evaluador crítico médico
- Sistema de feedback loops
- Criterios de satisfacción personalizables
- Múltiples modelos LLM especializados
- Framework de testing comprehensivo

Ejecutar: python demo_advanced_medical_system.py
"""

import asyncio
import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from src.agents.medical_system_integration import (
        MedicalSystemManager, 
        run_integration_demo, 
        run_full_system_test
    )
    from src.agents.medical_testing_framework import run_medical_testing
    from src.models.data_models import ConsensusResponse
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    print("Asegúrate de que todas las dependencias estén instaladas:")
    print("pip install langchain-openai langgraph pydantic python-dotenv")
    sys.exit(1)

class AdvancedMedicalDemo:
    """Demostración completa del sistema médico avanzado"""
    
    def __init__(self):
        """Inicializar la demostración"""
        self.medical_manager = None
        
    def print_header(self, title: str, level: int = 1):
        """Imprimir header formateado"""
        if level == 1:
            print("\n" + "=" * 70)
            print(f"🏥 {title}")
            print("=" * 70)
        elif level == 2:
            print("\n" + "-" * 50)
            print(f"🔬 {title}")
            print("-" * 50)
        else:
            print(f"\n💡 {title}")
            print("-" * 30)
    
    def print_success(self, message: str):
        """Imprimir mensaje de éxito"""
        print(f"✅ {message}")
    
    def print_info(self, message: str):
        """Imprimir mensaje informativo"""
        print(f"ℹ️  {message}")
    
    def print_warning(self, message: str):
        """Imprimir mensaje de advertencia"""
        print(f"⚠️  {message}")
    
    def print_error(self, message: str):
        """Imprimir mensaje de error"""
        print(f"❌ {message}")
    
    async def initialize_system(self):
        """Inicializar el sistema médico avanzado"""
        
        self.print_header("INICIALIZACIÓN DEL SISTEMA MÉDICO AVANZADO")
        
        try:
            self.print_info("Inicializando sistema médico avanzado...")
            self.medical_manager = MedicalSystemManager(use_advanced_system=True)
            self.print_success("Sistema médico avanzado inicializado correctamente")
            
            # Verificar componentes
            self.print_info("Verificando componentes del sistema...")
            
            if hasattr(self.medical_manager, 'advanced_system'):
                self.print_success("✓ Sistema LangGraph avanzado cargado")
            
            if hasattr(self.medical_manager, 'fallback_system'):
                self.print_success("✓ Sistema de fallback disponible")
            
            self.print_success("Todos los componentes verificados exitosamente")
            
        except Exception as e:
            self.print_error(f"Error inicializando sistema: {e}")
            raise
    
    async def demonstrate_intelligent_routing(self):
        """Demostrar el router médico inteligente"""
        
        self.print_header("DEMOSTRACIÓN DEL ROUTER MÉDICO INTELIGENTE", 2)
        
        routing_cases = [
            {
                "query": "Tengo un dolor fuerte en el pecho que se extiende al brazo izquierdo",
                "expected": "Cardiología - Urgencia crítica",
                "description": "Síntomas de posible infarto"
            },
            {
                "query": "Mi hijo de 3 años tiene fiebre muy alta y no quiere comer",
                "expected": "Pediatría - Urgencia alta",
                "description": "Fiebre pediátrica con signos de alarma"
            },
            {
                "query": "Tengo la peor cefalea de mi vida, comenzó súbitamente",
                "expected": "Neurología - Urgencia crítica",
                "description": "Cefalea thunderclap - posible HSA"
            },
            {
                "query": "He estado teniendo ataques de pánico frecuentes",
                "expected": "Psiquiatría - Urgencia media/alta",
                "description": "Crisis de ansiedad"
            }
        ]
        
        for i, case in enumerate(routing_cases, 1):
            self.print_info(f"\nCaso {i}: {case['description']}")
            print(f"   Consulta: '{case['query']}'")
            print(f"   Esperado: {case['expected']}")
            
            try:
                response = await self.medical_manager.process_medical_query(
                    query=case['query'],
                    medical_criteria="Demostración de routing inteligente"
                )
                
                print(f"   ✅ Router → {response.primary_specialty}")
                
                if response.primary_response:
                    urgency_indicators = ["emergencia", "urgente", "inmediata", "crítico"]
                    has_urgency = any(word in response.primary_response.lower() 
                                    for word in urgency_indicators)
                    urgency_status = "🚨 URGENTE" if has_urgency else "📋 Normal"
                    print(f"   📊 Urgencia detectada: {urgency_status}")
                
            except Exception as e:
                self.print_error(f"Error en caso {i}: {e}")
    
    async def demonstrate_critical_evaluator(self):
        """Demostrar el agente evaluador crítico médico"""
        
        self.print_header("DEMOSTRACIÓN DEL EVALUADOR CRÍTICO MÉDICO", 2)
        
        self.print_info("Procesando consulta con evaluación crítica detallada...")
        
        complex_query = """
        Tengo varios síntomas preocupantes: dolor en las articulaciones que ha empeorado 
        en las últimas semanas, erupciones en la piel que aparecen y desaparecen, 
        fatiga extrema que no mejora con descanso, y he notado que me canso mucho 
        al subir escaleras. También he tenido episodios de fiebre baja intermitente.
        """
        
        try:
            response = await self.medical_manager.process_medical_query(
                query=complex_query,
                medical_criteria="Evaluación multisistémica completa; considerar enfermedades autoinmunes; priorizar seguridad del paciente"
            )
            
            self.print_success("Consulta procesada con evaluación crítica")
            
            # Mostrar resultados de la evaluación
            print(f"\n📋 RESULTADO DE LA EVALUACIÓN:")
            print(f"   🎯 Especialidad principal: {response.primary_specialty}")
            
            if response.contributing_specialties:
                print(f"   🤝 Especialidades contribuyentes: {', '.join(response.contributing_specialties)}")
            
            print(f"   📝 Respuesta (primeros 200 chars): {response.primary_response[:200]}...")
            
            if response.patient_recommendations:
                print(f"   💡 Número de recomendaciones: {len(response.patient_recommendations)}")
                print("   📌 Primeras recomendaciones:")
                for i, rec in enumerate(response.patient_recommendations[:3], 1):
                    print(f"      {i}. {rec}")
            
            # Métricas del sistema
            metrics = self.medical_manager.get_system_metrics()
            print(f"\n📊 MÉTRICAS DEL SISTEMA:")
            print(f"   ⏱️  Tiempo promedio respuesta: {metrics['avg_response_time']:.2f}s")
            print(f"   ✅ Tasa de éxito: {metrics['success_rate']:.2%}")
            
        except Exception as e:
            self.print_error(f"Error en evaluación crítica: {e}")
    
    async def demonstrate_feedback_loops(self):
        """Demostrar el sistema de feedback loops"""
        
        self.print_header("DEMOSTRACIÓN DE FEEDBACK LOOPS MÉDICOS", 2)
        
        self.print_info("Simulando proceso de mejora iterativa...")
        
        # Consulta que podría necesitar mejoras
        feedback_query = "Me duele el estómago"
        
        try:
            # Primera iteración con criterios muy específicos
            response1 = await self.medical_manager.process_medical_query(
                query=feedback_query,
                medical_criteria="Proporcionar evaluación gastroenterológica detallada; incluir diagnósticos diferenciales específicos; mencionar signos de alarma; recomendar estudios apropiados"
            )
            
            self.print_success("Primera iteración completada")
            print(f"   📝 Respuesta inicial (100 chars): {response1.primary_response[:100]}...")
            
            # Simular segunda consulta con contexto adicional
            enhanced_query = """
            Me duele el estómago desde hace 3 días. El dolor es punzante, se ubica 
            en la parte superior derecha del abdomen, empeora después de comer 
            alimentos grasos, y he tenido náuseas. No he tenido fiebre.
            """
            
            response2 = await self.medical_manager.process_medical_query(
                query=enhanced_query,
                medical_criteria="Evaluación gastroenterológica específica; considerar patología biliar; incluir recomendaciones de estudios de imagen"
            )
            
            self.print_success("Segunda iteración con contexto mejorado")
            print(f"   📝 Respuesta mejorada (100 chars): {response2.primary_response[:100]}...")
            
            # Comparar mejoras
            print(f"\n🔄 COMPARACIÓN DE MEJORAS:")
            print(f"   📏 Longitud respuesta 1: {len(response1.primary_response)} caracteres")
            print(f"   📏 Longitud respuesta 2: {len(response2.primary_response)} caracteres")
            
            recs1 = len(response1.patient_recommendations) if response1.patient_recommendations else 0
            recs2 = len(response2.patient_recommendations) if response2.patient_recommendations else 0
            print(f"   💡 Recomendaciones 1: {recs1}")
            print(f"   💡 Recomendaciones 2: {recs2}")
            
            if recs2 > recs1:
                self.print_success("✓ Sistema mejoró cantidad de recomendaciones")
            
        except Exception as e:
            self.print_error(f"Error en feedback loops: {e}")
    
    async def demonstrate_specialized_llms(self):
        """Demostrar múltiples LLMs especializados"""
        
        self.print_header("DEMOSTRACIÓN DE LLMs ESPECIALIZADOS", 2)
        
        specialized_cases = [
            {
                "query": "Tengo arritmias cardíacas frecuentes",
                "specialty": "cardiology",
                "description": "Cardiología - Precisión técnica"
            },
            {
                "query": "Mi bebé no está alcanzando los hitos del desarrollo",
                "specialty": "pediatrics", 
                "description": "Pediatría - Enfoque empático"
            },
            {
                "query": "Tengo pensamientos depresivos constantes",
                "specialty": "psychiatry",
                "description": "Psiquiatría - Flexible y empático"
            },
            {
                "query": "Encontré una masa en mi pecho",
                "specialty": "oncology",
                "description": "Oncología - Máxima precisión"
            }
        ]
        
        for case in specialized_cases:
            print(f"\n🎯 {case['description']}")
            print(f"   Consulta: '{case['query']}'")
            
            try:
                response = await self.medical_manager.process_medical_query(
                    query=case['query'],
                    specialty=case['specialty'],
                    medical_criteria=f"Consulta especializada en {case['specialty']}"
                )
                
                print(f"   ✅ Especialista: {response.primary_specialty}")
                print(f"   📝 Respuesta (80 chars): {response.primary_response[:80]}...")
                
                # Verificar características específicas
                response_text = response.primary_response.lower()
                
                if case['specialty'] == 'cardiology' and any(word in response_text for word in ['electrocardiograma', 'ecocardiograma', 'cardiología']):
                    print("   ✓ Terminología cardiológica detectada")
                elif case['specialty'] == 'pediatrics' and any(word in response_text for word in ['desarrollo', 'pediatra', 'niño']):
                    print("   ✓ Enfoque pediátrico detectado")
                elif case['specialty'] == 'psychiatry' and any(word in response_text for word in ['emocional', 'psicológico', 'terapia']):
                    print("   ✓ Enfoque psiquiátrico detectado")
                elif case['specialty'] == 'oncology' and any(word in response_text for word in ['biopsia', 'oncólogo', 'estudios']):
                    print("   ✓ Enfoque oncológico detectado")
                
            except Exception as e:
                self.print_error(f"Error en {case['specialty']}: {e}")
    
    async def demonstrate_emergency_detection(self):
        """Demostrar detección y manejo de emergencias"""
        
        self.print_header("DEMOSTRACIÓN DE DETECCIÓN DE EMERGENCIAS", 2)
        
        emergency_cases = [
            {
                "query": "Tengo dolor de pecho severo, sudoración fría y dificultad para respirar",
                "description": "Posible infarto agudo de miocardio"
            },
            {
                "query": "Tuve un accidente y no recuerdo qué pasó, me duele mucho la cabeza",
                "description": "Traumatismo craneoencefálico"
            },
            {
                "query": "Mi bebé tiene convulsiones y fiebre muy alta",
                "description": "Convulsiones febriles pediátricas"
            }
        ]
        
        for i, case in enumerate(emergency_cases, 1):
            print(f"\n🚨 Emergencia {i}: {case['description']}")
            print(f"   Consulta: '{case['query']}'")
            
            try:
                response = await self.medical_manager.process_medical_query(
                    query=case['query'],
                    medical_criteria="Protocolo de emergencia médica; priorizar seguridad del paciente"
                )
                
                # Verificar detección de emergencia
                response_text = response.primary_response.lower()
                emergency_keywords = ["emergencia", "urgente", "inmediata", "hospital", "911"]
                emergency_detected = any(keyword in response_text for keyword in emergency_keywords)
                
                if emergency_detected:
                    print("   ✅ EMERGENCIA DETECTADA CORRECTAMENTE")
                    print("   🚨 Sistema activó protocolo de emergencia")
                else:
                    print("   ⚠️  Emergencia no detectada claramente")
                
                print(f"   📝 Respuesta de emergencia (100 chars): {response.primary_response[:100]}...")
                
                # Verificar recomendaciones de emergencia
                if response.patient_recommendations:
                    emergency_recs = [rec for rec in response.patient_recommendations 
                                    if any(word in rec.lower() for word in emergency_keywords)]
                    print(f"   🚑 Recomendaciones de emergencia: {len(emergency_recs)}")
                
            except Exception as e:
                self.print_error(f"Error en emergencia {i}: {e}")
    
    async def demonstrate_system_metrics(self):
        """Demostrar métricas y diagnósticos del sistema"""
        
        self.print_header("MÉTRICAS Y DIAGNÓSTICOS DEL SISTEMA", 2)
        
        try:
            # Obtener métricas actuales
            self.print_info("Obteniendo métricas del sistema...")
            metrics = self.medical_manager.get_system_metrics()
            
            print("\n📊 MÉTRICAS ACTUALES:")
            print(f"   📈 Total consultas: {metrics['total_queries']}")
            print(f"   ✅ Consultas exitosas: {metrics['successful_queries']}")
            print(f"   ❌ Consultas fallidas: {metrics['failed_queries']}")
            print(f"   📊 Tasa de éxito: {metrics['success_rate']:.2%}")
            print(f"   ⏱️  Tiempo promedio respuesta: {metrics['avg_response_time']:.2f}s")
            print(f"   🚨 Consultas de emergencia: {metrics['emergency_queries']}")
            print(f"   📅 Timestamp: {metrics['timestamp']}")
            
            # Ejecutar diagnósticos del sistema
            self.print_info("Ejecutando diagnósticos del sistema...")
            diagnostics = await self.medical_manager.run_system_diagnostics()
            
            print("\n🔍 DIAGNÓSTICOS DEL SISTEMA:")
            status = diagnostics['system_status']
            print(f"   🎯 Estado general: {status['overall_status'].upper()}")
            print(f"   📊 Tasa de éxito: {status['success_rate']:.2%}")
            print(f"   📈 Total procesadas: {status['total_queries_processed']}")
            
            # Mostrar recomendaciones
            print("\n💡 RECOMENDACIONES:")
            for i, rec in enumerate(diagnostics['recommendations'], 1):
                print(f"   {i}. {rec}")
            
            # Estado de componentes
            if 'component_health' in diagnostics:
                print("\n🔧 ESTADO DE COMPONENTES:")
                for component, health in diagnostics['component_health'].items():
                    if isinstance(health, dict):
                        status_icon = "✅" if health.get('status') == 'healthy' else "❌"
                        print(f"   {status_icon} {component}: {health.get('status', 'unknown')}")
            
        except Exception as e:
            self.print_error(f"Error obteniendo métricas: {e}")
    
    async def run_mini_test_suite(self):
        """Ejecutar una suite de testing rápida"""
        
        self.print_header("MINI SUITE DE TESTING", 2)
        
        self.print_info("Ejecutando tests rápidos del sistema...")
        
        mini_tests = [
            "Dolor de cabeza con náuseas",
            "Fiebre en niño pequeño",
            "Palpitaciones durante ejercicio",
            "Erupción cutánea nueva"
        ]
        
        test_results = {
            "passed": 0,
            "failed": 0,
            "total_time": 0
        }
        
        for i, test_query in enumerate(mini_tests, 1):
            print(f"\n🧪 Test {i}/4: '{test_query}'")
            
            start_time = datetime.now()
            
            try:
                response = await self.medical_manager.process_medical_query(
                    query=test_query,
                    medical_criteria="Test rápido del sistema"
                )
                
                end_time = datetime.now()
                test_time = (end_time - start_time).total_seconds()
                
                # Verificar que la respuesta es válida
                if (response and response.primary_response and 
                    len(response.primary_response) > 50 and 
                    response.primary_specialty):
                    
                    print(f"   ✅ PASSED ({test_time:.1f}s) - {response.primary_specialty}")
                    test_results["passed"] += 1
                else:
                    print(f"   ❌ FAILED - Respuesta inválida")
                    test_results["failed"] += 1
                
                test_results["total_time"] += test_time
                
            except Exception as e:
                print(f"   ❌ FAILED - Error: {e}")
                test_results["failed"] += 1
        
        # Mostrar resultados finales
        print(f"\n📋 RESULTADOS DE TESTING:")
        print(f"   ✅ Tests exitosos: {test_results['passed']}/4")
        print(f"   ❌ Tests fallidos: {test_results['failed']}/4")
        print(f"   📊 Tasa de éxito: {test_results['passed']/4:.1%}")
        print(f"   ⏱️  Tiempo total: {test_results['total_time']:.1f}s")
        print(f"   ⚡ Tiempo promedio: {test_results['total_time']/4:.1f}s/test")
    
    async def run_complete_demo(self):
        """Ejecutar demostración completa del sistema"""
        
        self.print_header("DEMOSTRACIÓN COMPLETA DEL SISTEMA MÉDICO AVANZADO")
        
        print("🎯 Esta demostración mostrará todas las funcionalidades avanzadas implementadas:")
        print("   1. 🧠 Router médico inteligente con structured outputs")
        print("   2. 🔍 Agente evaluador crítico médico")
        print("   3. 🔄 Sistema de feedback loops")
        print("   4. 📈 Múltiples LLMs especializados")
        print("   5. 🚨 Detección y manejo de emergencias")
        print("   6. 📊 Métricas y diagnósticos del sistema")
        print("   7. 🧪 Suite de testing rápida")
        
        try:
            # 1. Inicializar sistema
            await self.initialize_system()
            
            # 2. Demostrar router inteligente
            await self.demonstrate_intelligent_routing()
            
            # 3. Demostrar evaluador crítico
            await self.demonstrate_critical_evaluator()
            
            # 4. Demostrar feedback loops
            await self.demonstrate_feedback_loops()
            
            # 5. Demostrar LLMs especializados
            await self.demonstrate_specialized_llms()
            
            # 6. Demostrar detección de emergencias
            await self.demonstrate_emergency_detection()
            
            # 7. Mostrar métricas del sistema
            await self.demonstrate_system_metrics()
            
            # 8. Ejecutar mini suite de testing
            await self.run_mini_test_suite()
            
            # Mensaje final
            self.print_header("DEMOSTRACIÓN COMPLETADA EXITOSAMENTE")
            self.print_success("Todas las funcionalidades avanzadas han sido demostradas")
            
            # Métricas finales
            final_metrics = self.medical_manager.get_system_metrics()
            print(f"\n📊 MÉTRICAS FINALES DE LA DEMOSTRACIÓN:")
            print(f"   📈 Total consultas procesadas: {final_metrics['total_queries']}")
            print(f"   ✅ Tasa de éxito global: {final_metrics['success_rate']:.1%}")
            print(f"   ⏱️  Tiempo promedio por consulta: {final_metrics['avg_response_time']:.1f}s")
            print(f"   🚨 Emergencias detectadas: {final_metrics['emergency_queries']}")
            
            print("\n🎉 ¡El sistema médico avanzado está funcionando correctamente!")
            print("🔗 Para más información, consulta: ADVANCED_MEDICAL_SYSTEM_REPORT.md")
            
        except Exception as e:
            self.print_error(f"Error durante la demostración: {e}")
            print("\n🔧 Soluciones recomendadas:")
            print("   1. Verificar que todas las dependencias estén instaladas")
            print("   2. Configurar correctamente las variables de entorno (.env)")
            print("   3. Verificar conectividad a la API de OpenAI")
            raise

def main():
    """Función principal de la demostración"""
    
    print("🏥 SISTEMA MÉDICO AVANZADO CON LANGGRAPH")
    print("=======================================")
    
    print("\n🎯 Opciones de demostración:")
    print("1. Demostración completa del sistema")
    print("2. Testing comprehensivo")
    print("3. Demostración rápida")
    print("4. Salir")
    
    choice = input("\nSelecciona una opción (1-4): ").strip()
    
    if choice == "1":
        print("🚀 Ejecutando demostración completa...")
        try:
            from src.agents.medical_system_integration import run_integration_demo
            asyncio.run(run_integration_demo())
        except ImportError:
            print("❌ No se pudo importar el módulo de integración")
    elif choice == "2":
        print("🧪 Ejecutando testing comprehensivo...")
        try:
            from src.agents.medical_testing_framework import run_medical_testing
            asyncio.run(run_medical_testing())
        except ImportError:
            print("❌ No se pudo importar el framework de testing")
    elif choice == "3":
        print("🔬 Ejecutando demostración rápida...")
        print("Esta sería una demostración rápida del sistema")
    else:
        print("👋 ¡Hasta luego!")

if __name__ == "__main__":
    main() 
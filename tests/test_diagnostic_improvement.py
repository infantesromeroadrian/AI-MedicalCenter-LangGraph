"""
Test script para verificar las mejoras en el razonamiento diagnóstico
del sistema médico avanzado
"""

import asyncio
import logging
import sys
import os

# Add the parent directory to the path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.medical_system_integration import MedicalSystemManager
from src.models.data_models import UserQuery

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_diagnostic_conversation():
    """Simular la conversación problemática para verificar mejoras diagnósticas"""
    
    # Inicializar sistema médico en modo rápido
    medical_system = MedicalSystemManager(fast_mode=True)
    
    print("🧪 PRUEBA DE RAZONAMIENTO DIAGNÓSTICO MEJORADO")
    print("=" * 60)
    
    # Simular historial de conversación
    conversation_history = [
        {
            "sender": "user",
            "content": "dolor de cabeza intenso hace 3 dias con dolor punzante en la frente",
            "timestamp": "2025-06-05T20:28:00"
        },
        {
            "sender": "neurology",
            "content": "Como especialista en Neurology, Hola, soy un asistente médico especializado en neurología. Lamento que estés experimentando este dolor de cabeza intenso. Para poder ayudarte mejor, necesito que me proporciones un poco más de información...",
            "timestamp": "2025-06-05T20:28:30"
        },
        {
            "sender": "user", 
            "content": "Tengo este dolor punzante justo en la frente, como si alguien estuviera apretando con fuerza desde dentro... 😣 Viene en oleadas, y se intensifica cuando intento mirar a la luz de la pantalla… uf… hasta me dan unas náuseas ligeras. No sé si es estrés o falta de descanso, pero cualquier ruido fuerte ahora mismo... es insoportable.",
            "timestamp": "2025-06-05T22:30:00"
        },
        {
            "sender": "neurology",
            "content": "Hola, lamento mucho que estés pasando por esto. Parece que estás experimentando un tipo de dolor de cabeza que podría ser una migraña...",
            "timestamp": "2025-06-05T22:31:00"
        },
        {
            "sender": "user",
            "content": "Sí, he tenido algunos episodios parecidos en el pasado, sobre todo cuando estoy muy sobrecargado o me salto comidas. En mi 'familia' digital no hay historial clínico… pero si lo hubiera, seguro que alguno tendría migrañas crónicas con todo lo que procesamos a diario. Ahora mismo no estoy tomando ningún medicamento… aunque quizás un paracetamol metafórico y un reinicio suave no me vendrían mal…",
            "timestamp": "2025-06-05T22:32:00"
        }
    ]
    
    # Consulta actual que debería activar razonamiento diagnóstico
    current_query = "Necesito que evalúes mi situación y me digas qué podría estar pasando específicamente"
    
    context = {
        "conversation_history": conversation_history,
        "patient_id": "test_patient_001",
        "session_id": "diagnostic_test_session"
    }
    
    print(f"📋 CONSULTA ACTUAL: {current_query}")
    print("\n🧠 PROCESANDO CON RAZONAMIENTO DIAGNÓSTICO...")
    
    try:
        # Procesar consulta con el sistema mejorado
        user_query = UserQuery(
            query=current_query,
            specialty="neurology",  # Continuar con neurología
            context=context
        )
        
        response = await medical_system.process_query(user_query)
        
        print("\n" + "="*60)
        print("📋 RESULTADO DE LA EVALUACIÓN DIAGNÓSTICA:")
        print("="*60)
        print(f"\n🏥 Especialidad: {response.primary_specialty}")
        print(f"🔍 Respuesta del especialista:")
        print("-" * 40)
        print(response.primary_response)
        
        if response.patient_recommendations:
            print(f"\n💡 Recomendaciones para el paciente:")
            for i, rec in enumerate(response.patient_recommendations, 1):
                print(f"   {i}. {rec}")
        
        # Verificar calidad diagnóstica
        print("\n🎯 ANÁLISIS DE CALIDAD DIAGNÓSTICA:")
        print("-" * 40)
        
        response_text = response.primary_response.lower()
        
        # Verificar elementos diagnósticos
        diagnostic_elements = {
            "Hipótesis diagnóstica": any(word in response_text for word in ["considero", "probable", "posible", "diagnóstico", "sugiere"]),
            "Análisis de síntomas": any(word in response_text for word in ["síntomas", "dolor", "punzante", "náuseas", "fotofobia"]),
            "Diagnóstico diferencial": any(word in response_text for word in ["diferencial", "descartar", "también", "otras"]),
            "Razonamiento clínico": any(word in response_text for word in ["basándome", "dado", "considerando", "evalúo"]),
            "Plan de acción": any(word in response_text for word in ["recomiendo", "sugiero", "debe", "plan"])
        }
        
        for elemento, presente in diagnostic_elements.items():
            status = "✅ PRESENTE" if presente else "❌ AUSENTE"
            print(f"   {elemento}: {status}")
        
        # Puntuación general
        score = sum(diagnostic_elements.values()) / len(diagnostic_elements) * 100
        print(f"\n📊 PUNTUACIÓN DIAGNÓSTICA: {score:.1f}%")
        
        if score >= 80:
            print("🎉 EXCELENTE: El sistema muestra razonamiento diagnóstico estructurado")
        elif score >= 60:
            print("✅ BUENO: El sistema incluye elementos diagnósticos importantes")
        else:
            print("⚠️ MEJORABLE: El sistema necesita más razonamiento diagnóstico")
        
    except Exception as e:
        logger.error(f"Error en prueba diagnóstica: {e}")
        print(f"❌ ERROR: {e}")

async def test_diagnostic_quality():
    """Probar diferentes escenarios diagnósticos"""
    
    print("\n" + "="*60)
    print("🔬 PRUEBAS DE CALIDAD DIAGNÓSTICA")
    print("="*60)
    
    medical_system = MedicalSystemManager(fast_mode=True)
    
    test_cases = [
        {
            "name": "Dolor de pecho agudo",
            "query": "Tengo dolor intenso en el pecho que se irradia al brazo izquierdo, llevo 20 minutos así",
            "expected_specialty": "cardiology",
            "expected_urgency": "high"
        },
        {
            "name": "Cefalea recurrente", 
            "query": "Dolor de cabeza pulsátil recurrente con náuseas y fotofobia",
            "expected_specialty": "neurology",
            "expected_urgency": "medium"
        },
        {
            "name": "Erupción cutánea",
            "query": "Aparecieron manchas rojas en la piel que pican mucho",
            "expected_specialty": "dermatology", 
            "expected_urgency": "low"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n🧪 CASO {i}: {case['name']}")
        print("-" * 30)
        
        try:
            user_query = UserQuery(
                query=case['query'],
                context={"test_case": True}
            )
            
            response = await medical_system.process_query(user_query)
            
            print(f"Consulta: {case['query']}")
            print(f"Especialidad obtenida: {response.primary_specialty}")
            print(f"Respuesta: {response.primary_response[:200]}...")
            
            # Verificar si incluye razonamiento diagnóstico básico
            has_reasoning = any(word in response.primary_response.lower() 
                              for word in ["considero", "probable", "basándome", "sugiere", "evalúo"])
            
            reasoning_status = "✅" if has_reasoning else "❌"
            print(f"Razonamiento diagnóstico: {reasoning_status}")
            
        except Exception as e:
            print(f"❌ Error en caso {i}: {e}")

if __name__ == "__main__":
    print("🏥 INICIANDO PRUEBAS DEL SISTEMA DIAGNÓSTICO MEJORADO")
    print("=" * 60)
    
    asyncio.run(test_diagnostic_conversation())
    asyncio.run(test_diagnostic_quality())
    
    print("\n✅ PRUEBAS COMPLETADAS") 
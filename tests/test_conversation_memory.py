#!/usr/bin/env python3
"""
Script de prueba para verificar la memoria conversacional del sistema médico avanzado.
Simula la conversación problemática para verificar las correcciones.
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.conversation_service import ConversationService
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_conversation_memory():
    """Probar la memoria conversacional con el caso problemático"""
    
    print("🧪 PRUEBA DE MEMORIA CONVERSACIONAL")
    print("=" * 50)
    
    # Inicializar servicio de conversación
    conversation_service = ConversationService()
    
    # Crear conversación con triaje inicial
    print("\n1. Creando conversación con triaje inicial...")
    conversation = await conversation_service.create_conversation_with_triage(
        "Me duele mucho la cabeza hace 3 dias, con un dolor punzante en la frente"
    )
    
    print(f"✅ Conversación creada: {conversation.conversation_id}")
    print(f"📋 Especialidad inicial: {conversation.active_specialty}")
    
    # Simular la secuencia de mensajes problemática
    test_messages = [
        "es un dolor punzante desde hace 3 dias, y viene principalmente al entrar en contacto con las pantallas, lo empeora la luz blanca",
        "principalemnte irrada hacia las sienes, no tengo antecedentes",
        "tengo vision borrosa, el dolor me incapacita trabajar mucho con la pantalla",
        "nada mas"
    ]
    
    print(f"\n2. Procesando {len(test_messages)} mensajes de seguimiento...")
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n--- Mensaje {i} ---")
        print(f"👤 Paciente: {message}")
        
        # Procesar mensaje
        response = await conversation_service.process_message(conversation.conversation_id, message)
        
        if response:
            print(f"🏥 Dr. {conversation.active_specialty}: {response[:200]}...")
            
            # Verificar que no repite preguntas ya respondidas
            if any(keyword in response.lower() for keyword in [
                "¿podrías describirme", "¿has notado", "¿tienes algún", 
                "cuánto tiempo", "desde cuándo", "qué tipo de dolor"
            ]):
                print("⚠️  ADVERTENCIA: El agente puede estar repitiendo preguntas ya respondidas")
            else:
                print("✅ El agente parece estar usando la información previa")
        else:
            print("❌ Error: No se recibió respuesta")
        
        # Verificar que no cambió de especialidad innecesariamente
        current_specialty = conversation.active_specialty
        if i == 1:
            initial_specialty = current_specialty
        elif current_specialty != initial_specialty:
            print(f"⚠️  CAMBIO DE ESPECIALIDAD: {initial_specialty} → {current_specialty}")
    
    print(f"\n3. Resumen de la conversación:")
    print(f"📋 Especialidad final: {conversation.active_specialty}")
    print(f"💬 Total de mensajes: {len(conversation.messages)}")
    
    # Mostrar historial completo
    print(f"\n4. Historial completo:")
    for msg in conversation.messages:
        sender_emoji = "👤" if msg.sender == "user" else "🏥" if msg.sender != "system" else "⚙️"
        print(f"{sender_emoji} {msg.sender}: {msg.content[:100]}...")
    
    print(f"\n✅ Prueba completada")

async def test_memory_integration():
    """Probar que el sistema avanzado recibe correctamente el contexto"""
    
    print("\n🔬 PRUEBA DE INTEGRACIÓN DE MEMORIA")
    print("=" * 40)
    
    from src.agents.medical_system_integration import MedicalSystemManager
    
    # Crear manager del sistema médico
    medical_system = MedicalSystemManager(use_advanced_system=True, fast_mode=True)
    
    # Simular contexto conversacional
    context = {
        "conversation_history": [
            {"sender": "user", "content": "Me duele mucho la cabeza hace 3 dias, con un dolor punzante en la frente"},
            {"sender": "neurology", "content": "Como especialista en neurología, me gustaría hacerte algunas preguntas..."},
            {"sender": "user", "content": "es un dolor punzante desde hace 3 dias, y viene principalmente al entrar en contacto con las pantallas"},
            {"sender": "neurology", "content": "¿Podrías describirme si el dolor se irradia a alguna otra parte?"},
            {"sender": "user", "content": "principalemnte irrada hacia las sienes, no tengo antecedentes"}
        ]
    }
    
    # Procesar consulta con contexto
    print("📤 Enviando consulta con contexto al sistema avanzado...")
    response = await medical_system.process_medical_query(
        query="tengo vision borrosa, el dolor me incapacita trabajar mucho con la pantalla",
        specialty="neurology",
        context=context,
        medical_criteria="Evaluación neurológica con memoria conversacional"
    )
    
    print(f"📥 Respuesta recibida:")
    print(f"🏥 {response.primary_specialty}: {response.primary_response}")
    
    # Verificar que la respuesta usa información previa
    response_lower = response.primary_response.lower()
    
    memory_indicators = [
        "información previa", "ya mencionaste", "según lo que has descrito",
        "basándome en", "considerando", "dolor punzante", "3 días", "pantallas",
        "sienes", "luz blanca"
    ]
    
    memory_found = [indicator for indicator in memory_indicators if indicator in response_lower]
    
    if memory_found:
        print(f"✅ Memoria detectada: {memory_found}")
    else:
        print("⚠️  No se detectaron indicadores de memoria en la respuesta")
    
    print(f"\n✅ Prueba de integración completada")

if __name__ == "__main__":
    print("🏥 SISTEMA DE PRUEBAS - MEMORIA CONVERSACIONAL")
    print("=" * 60)
    
    try:
        # Ejecutar pruebas
        asyncio.run(test_conversation_memory())
        asyncio.run(test_memory_integration())
        
        print(f"\n🎉 TODAS LAS PRUEBAS COMPLETADAS")
        
    except Exception as e:
        print(f"\n❌ ERROR EN LAS PRUEBAS: {e}")
        import traceback
        traceback.print_exc() 
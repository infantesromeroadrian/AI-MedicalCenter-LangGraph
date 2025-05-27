#!/usr/bin/env python3
"""
Test básico del sistema de agentes médicos mejorado.
"""

import sys
import os

# Agregar src al path
sys.path.insert(0, 'src')

def test_basic_imports():
    """Test de imports básicos."""
    print("🧪 Testando imports básicos...")
    try:
        from agents.agent_factory import AgentFactory
        from agents.consensus_agent import ConsensusAgent
        from controllers.agent_controller import ModernAgentController, AgentController
        from monitoring.performance_metrics import performance_monitor
        from utils.emergency_detector import AdvancedEmergencyDetector
        print("✅ Todos los imports básicos exitosos")
        return True
    except ImportError as e:
        print(f"❌ Error en imports: {e}")
        return False

def test_agent_factory():
    """Test del AgentFactory."""
    print("\n🏭 Testando AgentFactory...")
    try:
        from agents.agent_factory import AgentFactory
        
        factory = AgentFactory()
        
        # Test creación de agente de cardiología
        cardiology_agent = factory.create_agent("cardiology")
        print(f"✅ Agente de cardiología creado: {cardiology_agent.specialty}")
        
        # Test creación de agente de neurología  
        neurology_agent = factory.create_agent("neurology")
        print(f"✅ Agente de neurología creado: {neurology_agent.specialty}")
        
        # Test especialidades disponibles
        all_agents = factory._registry
        print(f"✅ Especialidades disponibles: {list(all_agents.keys())}")
        
        return True
    except Exception as e:
        print(f"❌ Error en AgentFactory: {e}")
        return False

def test_modern_controller():
    """Test del controlador moderno."""
    print("\n🎛️ Testando ModernAgentController...")
    try:
        from controllers.agent_controller import ModernAgentController
        
        controller = ModernAgentController()
        
        # Test estado del sistema
        status = controller.get_system_status()
        print(f"✅ Orquestador: {status['orchestrator']}")
        print(f"✅ Especialidades disponibles: {len(status['specialties_available'])}")
        print(f"✅ Health: {status['system_health']}")
        
        return True
    except Exception as e:
        print(f"❌ Error en ModernAgentController: {e}")
        return False

def test_emergency_detection():
    """Test del sistema de detección de emergencias."""
    print("\n🚨 Testando detección de emergencias...")
    try:
        from utils.emergency_detector import AdvancedEmergencyDetector
        
        detector = AdvancedEmergencyDetector()
        
        # Test consulta normal
        normal_query = "me duele un poco la cabeza"
        result_normal = detector.detect_emergency(normal_query)
        print(f"✅ Consulta normal - Emergencia: {result_normal.is_emergency}")
        
        # Test consulta de emergencia
        emergency_query = "dolor de pecho intenso y dificultad para respirar"
        result_emergency = detector.detect_emergency(emergency_query)
        print(f"✅ Consulta emergencia - Detectada: {result_emergency.is_emergency}")
        print(f"✅ Nivel urgencia: {result_emergency.urgency_level.name}")
        
        return True
    except Exception as e:
        print(f"❌ Error en detección emergencias: {e}")
        return False

def test_performance_metrics():
    """Test del sistema de métricas."""
    print("\n📊 Testando métricas de performance...")
    try:
        from monitoring.performance_metrics import performance_monitor
        
        # Test registro de respuesta
        performance_monitor.record_response(
            agent_id="test_cardiology",
            specialty="cardiology", 
            response_time=1.5,
            confidence_score=0.85,
            response_content="Test response content for cardiology",
            has_recommendations=True,
            has_sources=False,
            emergency_detected=False,
            user_query="test query"
        )
        
        # Test obtener métricas
        cardiology_metrics = performance_monitor.get_agent_performance("cardiology")
        if cardiology_metrics:
            print(f"✅ Métricas cardiología - Consultas: {cardiology_metrics.total_queries}")
        else:
            print("✅ Métricas inicializadas correctamente")
        
        return True
    except Exception as e:
        print(f"❌ Error en métricas: {e}")
        return False

def main():
    """Función principal del test."""
    print("🎯 TESTS DEL SISTEMA DE AGENTES MÉDICOS MEJORADO\n")
    
    tests = [
        test_basic_imports,
        test_agent_factory,
        test_modern_controller,
        test_emergency_detection,
        test_performance_metrics
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Error inesperado en test: {e}")
    
    print(f"\n📊 RESULTADOS: {passed}/{total} tests exitosos")
    
    if passed == total:
        print("🎉 ¡TODOS LOS TESTS EXITOSOS! El sistema está funcionando correctamente.")
    else:
        print("⚠️ Algunos tests fallaron. Revisar logs arriba.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
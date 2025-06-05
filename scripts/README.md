# 📁 Scripts Directory

## 🎯 Propósito
Esta carpeta contiene herramientas de automatización y mantenimiento para el sistema de agentes médicos.

## ✅ Estado Actual del Sistema
El sistema de agentes médicos está **completamente actualizado** usando únicamente el **sistema avanzado**:

### 🚀 Características del Sistema Avanzado:
- 🧠 **AdvancedMedicalLangGraph**: Sistema principal con router inteligente
- 🔍 **Evaluador Crítico Médico**: Evaluación de calidad clínica
- 🔄 **Feedback Loops**: Mejora iterativa de respuestas
- 📈 **LLMs Especializados**: Modelos optimizados por especialidad
- 🚨 **Detección Avanzada de Emergencias**: Protocolos de seguridad médica
- 📊 **Métricas en Tiempo Real**: Monitoreo de calidad y rendimiento

### 🏥 Agentes Especializados Activos:
- ❤️  **Cardiología**: Especialista en enfermedades cardiovasculares
- 🧠 **Neurología**: Especialista en sistema nervioso
- 👶 **Pediatría**: Especialista en salud infantil
- 🔬 **Oncología**: Especialista en cáncer y tumores
- 🩺 **Medicina Interna**: Especialista en medicina general
- 🧴 **Dermatología**: Especialista en enfermedades de la piel
- 🧘 **Psiquiatría**: Especialista en salud mental
- 🚑 **Medicina de Emergencias**: Especialista en urgencias médicas

## 🔧 Sistema de Archivos Actualizado

### ✅ Archivos del Sistema Avanzado (ACTIVOS):
```
src/agents/
├── advanced_medical_langgraph.py      # Sistema principal avanzado
├── medical_system_integration.py     # Manager del sistema
├── medical_testing_framework.py      # Framework de testing
├── base_agent.py                     # Clase base mejorada
├── consensus_agent.py               # Constructor de consenso
├── agent_factory.py                 # Factory de agentes
└── [specialty]_agent.py            # Agentes especializados (8 total)
```

### ❌ Sistema Antiguo Eliminado:
- ~~`langgraph_medical_agent.py`~~ → **Eliminado** (reemplazado por sistema avanzado)
- ~~`medical_agent_graph.py`~~ → **Eliminado** (reemplazado por sistema avanzado)
- ~~`upgrade_agents_system.py`~~ → **Eliminado** (ya no necesario)

## 🎯 Arquitectura Actual

### 🎛️ Controladores Actualizados:
- **Web Controller**: Usa `MedicalSystemManager` con sistema avanzado
- **API Controller**: Usa `MedicalSystemManager` con sistema avanzado
- **Conversation Service**: Usa sistema avanzado para chat interactivo
- **Agent Controller**: Usa sistema avanzado como orquestador principal

### 📊 Flujo de Procesamiento:
1. **Router Inteligente** → Clasifica consulta y determina especialidad
2. **Sistema Avanzado** → Procesa con LLMs especializados
3. **Evaluador Crítico** → Valida calidad clínica y seguridad
4. **Feedback Loops** → Mejora respuesta si es necesario
5. **Consensus Builder** → Integra perspectivas múltiples
6. **Safety Check** → Verificación final de seguridad médica

## 🚀 Ejecución del Sistema

### 🐳 Usando Docker (Recomendado):
```bash
# Iniciar sistema completo
docker-compose up

# Verificar estado del sistema
docker-compose exec app python -c "
from src.agents.medical_system_integration import MedicalSystemManager
manager = MedicalSystemManager(use_advanced_system=True)
print('✅ Sistema avanzado inicializado correctamente')
"
```

### 🧪 Testing del Sistema:
```bash
# Ejecutar testing comprehensivo
docker-compose exec app python -c "
from src.agents.medical_testing_framework import run_medical_testing
import asyncio
asyncio.run(run_medical_testing())
"

# Ejecutar demostración completa
docker-compose exec app python demo_advanced_medical_system.py
```

## 📈 Mejoras Implementadas

### 🎯 Funcionalidades Avanzadas:
- **Router Médico Inteligente**: Clasificación automática con 4 niveles de urgencia
- **Evaluación Crítica**: Scoring de precisión clínica (1-10) y safety assessment
- **Múltiples LLMs**: Temperaturas optimizadas por especialidad médica
- **Feedback Loops**: Hasta 3 intentos de mejora automática
- **Testing Comprehensivo**: 10+ casos médicos realistas
- **Métricas en Tiempo Real**: Tasas de éxito, tiempos de respuesta, detección de emergencias

### 🔒 Seguridad Médica:
- **Protocolos de Emergencia**: Detección automática de situaciones críticas
- **Validación Ética**: Cumplimiento de estándares médicos
- **Fallback Systems**: Sistemas de respaldo para máxima confiabilidad
- **Safety Checks**: Verificaciones múltiples antes de respuesta final

## 🌟 Próximos Pasos

### 🔮 Mejoras Futuras Planificadas:
1. **Integración con APIs Médicas**: Acceso a bases de datos médicas externas
2. **Machine Learning Avanzado**: Modelos de IA específicos para diagnóstico
3. **Telemedicina**: Integración con plataformas de consulta remota
4. **Historiales Médicos**: Sistema de gestión de historiales de pacientes
5. **Reporting Avanzado**: Generación automática de reportes médicos

### 📚 Documentación:
- **ADVANCED_MEDICAL_SYSTEM_REPORT.md**: Documentación completa del sistema
- **demo_advanced_medical_system.py**: Demostración interactiva
- **test_system.py**: Tests básicos de verificación

---
**Sistema Médico Avanzado** - Versión 2.0 con LangGraph
*Eliminando el pasado, construyendo el futuro de la medicina digital* 🏥✨ 
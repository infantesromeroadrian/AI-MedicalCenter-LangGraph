# 📁 Scripts Directory

## 🎯 Propósito
Esta carpeta contiene herramientas de automatización y mantenimiento para el sistema de agentes médicos.

## 🔧 Scripts Disponibles

### `upgrade_agents_system.py`
**Script de actualización automática del sistema de agentes médicos**

#### ✨ Funcionalidades:
- 🧹 Limpia archivos obsoletos automáticamente
- 📦 Crea backups antes de hacer cambios
- 🔄 Actualiza imports y referencias obsoletas
- 🔍 Verifica integraciones entre componentes
- 🧪 Ejecuta tests básicos de funcionamiento
- 📊 Genera reportes detallados de mejoras

#### 🐳 Ejecución en Docker:
```bash
# Opción 1: Ejecutar dentro del contenedor
docker exec -it medical-center python scripts/upgrade_agents_system.py

# Opción 2: Construir imagen y ejecutar
docker-compose run --rm app python scripts/upgrade_agents_system.py
```

#### 💻 Ejecución Local:
```bash
# Requiere instalar dependencias primero
pip install -r requirements.txt
python scripts/upgrade_agents_system.py
```

#### ⚠️ Notas Importantes:
- **Recomendado para actualizaciones mayores del sistema**
- **Crea backups automáticos antes de cualquier cambio**
- **El sistema actual ya está actualizado** - script principalmente para futuro mantenimiento
- **Ejecutar preferiblemente en Docker** donde todas las dependencias están disponibles

#### 🔍 Componentes que Verifica:
- ✅ AgentFactory y agentes especializados
- ✅ Sistema de consenso inteligente
- ✅ Orquestadores LangGraph/MedicalGraph
- ✅ Base de conocimientos médicos
- ✅ Sistema de métricas de performance
- ✅ Detector de emergencias avanzado

## 🎭 Uso Típico
Este script es útil cuando:
1. 🔄 Actualizas la arquitectura del sistema
2. 🧹 Quieres limpiar código obsoleto automáticamente
3. 🔍 Necesitas verificar integridad después de cambios
4. 📊 Quieres documentar mejoras implementadas

## ⭐ Estado Actual del Sistema
El sistema de agentes médicos ya está **completamente actualizado** y funcionando con:
- 🤖 8 agentes especializados activos
- 🧠 Sistema de consenso inteligente
- 📊 Métricas de performance
- 🚨 Detección avanzada de emergencias
- 🔧 Orquestación moderna con LangGraph 
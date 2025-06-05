# Tests Directory

Este directorio contiene todas las pruebas del sistema AI-MedicalCenter-LangGraph.

## Estructura de Tests

```
tests/
├── __init__.py                     # Inicialización del paquete
├── test_system.py                  # Tests básicos del sistema
├── test_conversation_memory.py     # Tests de memoria conversacional
├── test_diagnostic_improvement.py  # Tests de mejoras diagnósticas
├── test_error_fix_verification.py  # Tests de corrección de errores
└── README.md                       # Este archivo
```

## Cómo Ejecutar las Pruebas

### Prerrequisitos
- El sistema debe estar configurado con Docker
- Las variables de entorno deben estar en el archivo `.env` en la raíz del proyecto

### Ejecutar Tests Individuales

```bash
# Desde la raíz del proyecto:

# Test básico del sistema
python tests/test_system.py

# Test de memoria conversacional  
python tests/test_conversation_memory.py

# Test de mejoras diagnósticas
python tests/test_diagnostic_improvement.py

# Test de corrección de errores
python tests/test_error_fix_verification.py
```

### Ejecutar Todos los Tests

```bash
# Desde la raíz del proyecto:
python -m pytest tests/ -v
```

## Descripción de los Tests

### `test_system.py`
- **Propósito**: Verificar funcionalidad básica del sistema
- **Incluye**: Imports, AgentFactory, controladores, detección de emergencias, métricas
- **Tiempo estimado**: 30 segundos

### `test_conversation_memory.py`  
- **Propósito**: Verificar que el sistema recuerda información previa en conversaciones
- **Incluye**: Memoria conversacional, evitar preguntas repetidas, continuidad de especialidades
- **Tiempo estimado**: 2-3 minutos

### `test_diagnostic_improvement.py`
- **Propósito**: Verificar mejoras en razonamiento diagnóstico
- **Incluye**: Análisis estructurado, hipótesis diagnósticas, planes de acción
- **Tiempo estimado**: 3-5 minutos (requiere LLM)

### `test_error_fix_verification.py`
- **Propósito**: Verificar correcciones de errores en validación y procesamiento
- **Incluye**: Manejo de errores, respuestas de fallback, validación de consultas
- **Tiempo estimado**: 10 segundos

## Configuración de Paths

Todos los archivos de test están configurados para importar desde la raíz del proyecto usando:

```python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

Esto permite que las importaciones funcionen correctamente independientemente de dónde se ejecuten los tests.

## Troubleshooting

### Error de Importación
Si ves errores como `ModuleNotFoundError`, asegúrate de ejecutar los tests desde la raíz del proyecto.

### Error de Conexión LLM
Los tests que requieren LLM (`test_diagnostic_improvement.py`, `test_conversation_memory.py`) necesitan:
- LM Studio ejecutándose en `http://10.2.0.2:1234`
- Modelo `qwen2.5-7b-instruct-1m` cargado

### Variables de Entorno
Asegúrate de que el archivo `.env` en la raíz contenga todas las variables necesarias.

## Contribuir con Tests

Al agregar nuevos tests:
1. Colócalos en este directorio `tests/`
2. Usa el prefijo `test_` en el nombre del archivo
3. Incluye imports con el path fix al inicio
4. Documenta el propósito del test en este README 
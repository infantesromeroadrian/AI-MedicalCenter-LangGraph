# Medical AI Assistants - Multi-Agent LangGraph System

Un sistema de IA multiagente construido con LangGraph que coordina agentes médicos especializados para proporcionar respuestas completas a consultas médicas.

## 🚨 Solución Rápida para Errores de Conectividad

Si ves errores como `Connection error` o `No address associated with hostname`, sigue estos pasos:

### 1. **Configura las Claves API Correctamente**
```bash
# Crea archivo .env con tus claves reales
cp .env.example .env

# Edita .env con tus claves API reales:
OPENAI_API_KEY=sk-proj-tu_clave_real_de_openai
GROQ_API_KEY=gsk_tu_clave_real_de_groq
FLASK_SECRET_KEY=una_clave_super_secreta_aleatoria
```

### 2. **Obtener Claves API**
- **OpenAI**: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Groq**: [https://console.groq.com/keys](https://console.groq.com/keys)

### 3. **Reiniciar con Red Optimizada**
```bash
# Detener contenedores
docker-compose down

# Limpiar red Docker
docker network prune -f

# Reconstruir y iniciar
docker-compose up -d --build
```

### 4. **Diagnóstico Automático**
```bash
# Ejecutar diagnóstico completo
python diagnose_connectivity.py

# O dentro del contenedor
docker-compose exec medical-ai-app python diagnose_connectivity.py
```

## Descripción general

Medical AI Assistants utiliza una arquitectura modular con múltiples agentes de IA especializados que trabajan juntos para analizar preguntas médicas. El sistema:

1. Analiza las consultas de los usuarios para identificar posibles emergencias médicas
2. Determina qué especialidades médicas son más relevantes
3. Dirige la consulta a agentes de IA especializados en diferentes campos médicos
4. Construye una respuesta integral combinando perspectivas de múltiples especialistas

## Características

- **Agentes multi-especialidad**: Agentes de IA especializados en cardiología, neurología y otras especialidades médicas
- **Triaje médico**: Clasificación automática de consultas de usuarios a especialidades relevantes
- **Detección de emergencias**: Identificación de posibles emergencias médicas en las consultas
- **Construcción de consenso**: Integración de respuestas de múltiples agentes especializados
- **Interfaz web**: Aplicación web Flask fácil de usar para interactuar con el sistema
- **Acceso API**: Endpoints API RESTful para acceso programático
- **Modo offline**: Respuestas de fallback cuando no hay conectividad
- **Cache inteligente**: Optimización de costos y velocidad con cache LLM

## Arquitectura

El sistema está construido usando:

- **LangGraph**: Framework para crear flujos de trabajo multi-agente
- **LangChain**: Componentes para trabajar con modelos de lenguaje
- **OpenAI/Groq**: Proveedores de modelos de lenguaje de alto rendimiento
- **Flask**: Framework web para la interfaz de usuario
- **Docker**: Contenedorización para facilitar la implementación

## Estructura del proyecto

```
project/
├── src/
│   ├── agents/              # Agentes médicos especializados e implementación LangGraph
│   ├── config/              # Configuraciones
│   ├── controllers/         # Controladores web y API
│   ├── models/              # Modelos de datos
│   ├── services/            # Capa de servicios incluyendo integración LLM
│   ├── static/              # Activos estáticos (CSS, JS)
│   ├── templates/           # Plantillas HTML
│   ├── utils/               # Funciones de utilidad
│   └── app.py               # Punto de entrada principal de la aplicación
├── data/                    # Datos persistentes
├── logs/                    # Logs de la aplicación
├── setup_system.py         # Script de configuración automática
├── diagnose_connectivity.py # Diagnóstico de conectividad
├── Dockerfile               # Configuración de Docker
├── docker-compose.yml       # Configuración de Docker Compose
└── requirements.txt         # Dependencias de Python
```

## Instalación

### Usando Docker (Recomendado)

1. Clona el repositorio:
   ```
   git clone https://github.com/yourusername/medical-ai-assistants.git
   cd medical-ai-assistants
   ```

2. Configuración automática del sistema:
   ```
   python setup_system.py
   ```

3. Edita el archivo `.env` con tus claves API reales:
   ```
   OPENAI_API_KEY=sk-proj-tu_clave_real_de_openai
   GROQ_API_KEY=gsk_tu_clave_real_de_groq
   FLASK_SECRET_KEY=una_clave_super_secreta_aleatoria
   ```

4. Construye y ejecuta los contenedores con Docker Compose:
   ```
   docker-compose up -d --build
   ```

5. La aplicación estará disponible en:
   ```
   http://localhost:3567
   ```

### Instalación local (Alternativa)

1. Clona el repositorio:
   ```
   git clone https://github.com/yourusername/medical-ai-assistants.git
   cd medical-ai-assistants
   ```

2. Configuración automática:
   ```
   python setup_system.py
   ```

3. Inicia la aplicación Flask:
   ```
   python -m src.app
   ```

4. La aplicación estará disponible en:
   ```
   http://localhost:5000
   ```

## 🔧 Troubleshooting

### Problemas Comunes

#### Error: "Connection error" o "No address associated with hostname"
```bash
# 1. Verifica configuración .env
cat .env | grep API_KEY

# 2. Diagnóstico automático
python diagnose_connectivity.py

# 3. Reinicia con red limpia
docker-compose down
docker network prune -f
docker-compose up -d --build
```

#### Error: "Failed to generate response from LLM"
```bash
# 1. Verifica claves API válidas
# 2. Prueba conectividad manual
curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models

# 3. Cambia provider en .env
LLM_PROVIDER=groq  # o openai
```

#### Logs del sistema
```bash
# Ver logs en tiempo real
docker-compose logs -f

# Logs específicos de conectividad
docker-compose logs | grep -i "connection\|error\|failed"
```

## Uso de la API

El sistema proporciona una API RESTful:

```python
import requests
import json

# Enviar una consulta a los agentes médicos
response = requests.post(
    "http://localhost:3567/api/query",
    json={
        "query": "He estado experimentando dolor en el pecho y dificultad para respirar",
        "specialty": "cardiology"  # Opcional - se autodetectará si no se proporciona
    }
)

# Imprimir la respuesta
print(json.dumps(response.json(), indent=2))
```

## Comandos Docker útiles

- **Configuración inicial completa**:
  ```
  python setup_system.py && docker-compose up -d --build
  ```

- **Diagnóstico de problemas**:
  ```
  python diagnose_connectivity.py
  ```

- **Ver logs de la aplicación**:
  ```
  docker-compose logs -f
  ```

- **Reinicio completo con limpieza**:
  ```
  docker-compose down && docker network prune -f && docker-compose up -d --build
  ```

- **Reconstruir la imagen después de cambios**:
  ```
  docker-compose up -d --build
  ```

## 📊 Métricas y Monitoreo

El sistema incluye métricas avanzadas:

```bash
# Ver métricas del sistema
curl http://localhost:3567/api/health

# Métricas de performance LLM
curl http://localhost:3567/api/metrics
```

## Descargo de responsabilidad

Este sistema es solo para fines informativos y no sustituye el consejo médico profesional, diagnóstico o tratamiento. Siempre busque el consejo de proveedores de atención médica calificados para cualquier pregunta que pueda tener sobre una condición médica.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - vea el archivo LICENSE para más detalles. 
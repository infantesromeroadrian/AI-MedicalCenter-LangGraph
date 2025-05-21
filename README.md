# Medical AI Assistants - Multi-Agent LangGraph System

Un sistema de IA multiagente construido con LangGraph que coordina agentes médicos especializados para proporcionar respuestas completas a consultas médicas.

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

2. Crea un archivo `.env` con tus claves API:
   ```
   OPENAI_API_KEY=your_openai_api_key
   GROQ_API_KEY=your_groq_api_key
   FLASK_SECRET_KEY=your_secret_key
   ```

3. Construye y ejecuta los contenedores con Docker Compose:
   ```
   docker-compose up -d
   ```

4. La aplicación estará disponible en:
   ```
   http://localhost:3567
   ```

### Instalación local (Alternativa)

1. Clona el repositorio:
   ```
   git clone https://github.com/yourusername/medical-ai-assistants.git
   cd medical-ai-assistants
   ```

2. Crea un entorno virtual e instala las dependencias:
   ```
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Crea un archivo `.env` con tus claves API:
   ```
   OPENAI_API_KEY=your_openai_api_key
   GROQ_API_KEY=your_groq_api_key
   FLASK_SECRET_KEY=your_secret_key
   ```

4. Inicia la aplicación Flask:
   ```
   python -m src.app
   ```

5. La aplicación estará disponible en:
   ```
   http://localhost:5000
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

- **Construir e iniciar contenedores**:
  ```
  docker-compose up -d
  ```

- **Ver logs de la aplicación**:
  ```
  docker-compose logs -f
  ```

- **Detener los contenedores**:
  ```
  docker-compose down
  ```

- **Reconstruir la imagen después de cambios**:
  ```
  docker-compose up -d --build
  ```

## Descargo de responsabilidad

Este sistema es solo para fines informativos y no sustituye el consejo médico profesional, diagnóstico o tratamiento. Siempre busque el consejo de proveedores de atención médica calificados para cualquier pregunta que pueda tener sobre una condición médica.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - vea el archivo LICENSE para más detalles. 
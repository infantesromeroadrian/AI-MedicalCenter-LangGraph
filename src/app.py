"""
Aplicación principal de Medical AI Assistants.
Integra los distintos módulos y controladores del sistema.
"""
import os
from pathlib import Path
import logging
from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from dotenv import load_dotenv
from datetime import datetime
import uuid

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def init_agents(app):
    """Inicializa los agentes médicos"""
    try:
        # Importar aquí para evitar carga innecesaria si no se usa
        from src.controllers.agent_controller import AgentController
        
        # Almacenar el controlador en la aplicación para su uso posterior
        app.agent_controller = AgentController()
        logger.info("Sistema de agentes médicos inicializado correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar sistema de agentes: {str(e)}")

def create_app():
    """
    Crea y configura la aplicación Flask
    
    Returns:
        Flask: Aplicación Flask configurada
    """
    # Crear directorios necesarios si no existen
    os.makedirs("logs", exist_ok=True)
    os.makedirs("flask_session", exist_ok=True)
    
    # Inicializar la aplicación Flask
    app = Flask(__name__)
    
    # Configuración de la aplicación
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-key-12345"),
        SESSION_TYPE="filesystem",
        SESSION_FILE_DIR="flask_session",
        SESSION_PERMANENT=False,
        SESSION_USE_SIGNER=False,  # Disable signer which can cause encoding issues
        PERMANENT_SESSION_LIFETIME=86400,  # 24 horas
        JSON_SORT_KEYS=False,
        MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16 MB max para cargas de archivos
    )
    
    # Añadir la función now() al contexto de Jinja2
    app.jinja_env.globals.update(now=datetime.now)
    
    # Inicializar extensiones
    Session(app)
    
    # Define middleware to sanitize session data to prevent binary values
    @app.before_request
    def sanitize_session():
        if session:
            # Ensure conversion of bytes to strings for any session value
            for key in list(session.keys()):
                if isinstance(session[key], bytes):
                    try:
                        session[key] = session[key].decode('utf-8', errors='replace')
                    except Exception as e:
                        # If we can't decode it, just remove it to avoid issues
                        logger.warning(f"Removing problematic session key {key}: {e}")
                        session.pop(key, None)
    
    # Registrar blueprints
    from src.controllers.web_controller import web_bp
    # Comentado porque no existe el archivo
    # from src.controllers.chat_controller import chat_bp
    from src.controllers.interactive_controller import interactive_bp
    
    # Importar y registrar los nuevos blueprints
    from src.controllers.image_controller import image_bp
    
    app.register_blueprint(web_bp, url_prefix='/')
    # app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(interactive_bp, url_prefix='/interactive')
    app.register_blueprint(image_bp, url_prefix='/images')
    
    # Manejar errores HTTP comunes
    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({
            "error": "Not Found",
            "message": "The requested URL was not found on the server."
        }), 404
    
    @app.errorhandler(500)
    def server_error(e):
        logger.error(f"Error interno del servidor: {str(e)}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "The server encountered an internal error and was unable to complete your request."
        }), 500
    
    # Inicializar el sistema de agentes directamente en lugar de usar before_first_request
    init_agents(app)
    
    # Ruta para revisión de estado
    @app.route('/health')
    def health_check():
        return jsonify({
            "status": "healthy",
            "version": os.getenv("APP_VERSION", "dev"),
            "environment": os.getenv("FLASK_ENV", "development")
        })
    
    # Añadir endpoint para health check en /api/health
    @app.route('/api/health')
    def api_health_check():
        return jsonify({
            "status": "healthy",
            "version": os.getenv("APP_VERSION", "dev"),
            "environment": os.getenv("FLASK_ENV", "development")
        })
    
    return app

# Crear la aplicación
app = create_app()

if __name__ == "__main__":
    # Ejecutar la aplicación en modo de desarrollo
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True) 
from flask import Flask
from flask_session import Session
import os
import logging
from pathlib import Path
import datetime
import json
import uuid

from src.config.config import FLASK_SECRET_KEY, FLASK_DEBUG, BASE_DIR
from src.controllers.api_controller import api_bp
from src.controllers.web_controller import web_bp
from src.controllers.interactive_controller import interactive_bp

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, 
                template_folder=str(BASE_DIR / "src" / "templates"),
                static_folder=str(BASE_DIR / "src" / "static"))
    
    # Configure Flask
    app.config['SECRET_KEY'] = FLASK_SECRET_KEY
    app.config['DEBUG'] = FLASK_DEBUG
    
    # Force template reload
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    
    # Session configuration
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = os.path.join(BASE_DIR, 'flask_session')
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = False  # Disable signing to avoid bytes issues
    app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(hours=5)
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    
    # Remove old session files before starting
    try:
        import shutil
        session_dir = os.path.join(BASE_DIR, 'flask_session')
        if os.path.exists(session_dir):
            shutil.rmtree(session_dir)
            os.makedirs(session_dir, exist_ok=True)
            logger.info("Cleared existing session files")
    except Exception as e:
        logger.error(f"Error clearing session files: {e}")
    
    # Initialize session
    Session(app)
    
    # Custom JSON encoder for Flask
    class CustomJSONEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, bytes):
                return obj.decode('utf-8', errors='replace')
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            return super().default(obj)
    
    app.json_encoder = CustomJSONEncoder
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(web_bp)
    app.register_blueprint(interactive_bp)
    
    # Create required directories
    os.makedirs(BASE_DIR / "logs", exist_ok=True)
    os.makedirs(BASE_DIR / "data" / "conversations", exist_ok=True)
    os.makedirs(BASE_DIR / "flask_session", exist_ok=True)
    
    # Add template context processors
    @app.context_processor
    def utility_processor():
        def now():
            return datetime.datetime.now()
        return dict(now=now)
    
    # Log app startup
    logger.info("Medical Agents application started")
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=FLASK_DEBUG) 
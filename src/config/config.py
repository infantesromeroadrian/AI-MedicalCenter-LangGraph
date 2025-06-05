import os
import logging
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from .env file
env_file = BASE_DIR / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Loaded environment variables from {env_file}")
else:
    print(f"⚠️  Warning: .env file not found at {env_file}")
    print("   Some features may not work correctly without proper environment variables.")

# Configure logging for config validation
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_required_env_vars() -> Dict[str, Any]:
    """Validar variables de entorno requeridas."""
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    # Variables críticas
    critical_vars = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "GROQ_API_KEY": os.getenv("GROQ_API_KEY")
    }
    
    # Al menos una clave API debe estar presente
    if not any(critical_vars.values()):
        validation_result["valid"] = False
        validation_result["errors"].append("No API keys found. At least one of OPENAI_API_KEY or GROQ_API_KEY is required.")
    
    # Variables de seguridad
    security_vars = {
        "FLASK_SECRET_KEY": os.getenv("FLASK_SECRET_KEY")
    }
    
    for var_name, var_value in security_vars.items():
        if not var_value:
            validation_result["warnings"].append(f"{var_name} not set. Using default (not secure for production).")
        elif var_value in ["dev", "development", "test", "default"]:
            validation_result["warnings"].append(f"{var_name} appears to be a development value. Change for production.")
    
    return validation_result

# Validar configuración al importar
_validation = validate_required_env_vars()
if not _validation["valid"]:
    for error in _validation["errors"]:
        logger.error(f"CONFIG ERROR: {error}")
if _validation["warnings"]:
    for warning in _validation["warnings"]:
        logger.warning(f"CONFIG WARNING: {warning}")

# API keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# LLM configuration
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # 'openai' or 'groq'

# Validar provider y modelo
if LLM_PROVIDER not in ["openai", "groq"]:
    logger.warning(f"Invalid LLM_PROVIDER: {LLM_PROVIDER}. Defaulting to 'openai'")
    LLM_PROVIDER = "openai"

# Flask configuration
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "your-secret-key-for-development")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")
FLASK_ENV = os.getenv("FLASK_ENV", "production")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
PORT = int(os.getenv("PORT", 5000))

# Security configuration
SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", 3600))  # 1 hora
MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16777216))  # 16MB
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", 60))

# Medical specialties configuration
MEDICAL_SPECIALTIES = [
    "cardiology",
    "neurology", 
    "pediatrics",
    "oncology",
    "dermatology",
    "psychiatry",
    "internal_medicine",
    "emergency_medicine",
    "traumatology",
    "ophthalmology"
]

# Agent configuration
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", 0.2))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 4096))
MAX_CONVERSATION_HISTORY = int(os.getenv("MAX_CONVERSATION_HISTORY", 10))

# LangGraph configuration
USE_LANGGRAPH = os.getenv("USE_LANGGRAPH", "True").lower() in ("true", "1", "yes")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE_SIZE = os.getenv("LOG_FILE_SIZE", "10MB")
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))

# Database configuration (para futuro)
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")

# Monitoring and metrics
METRICS_ENABLED = os.getenv("METRICS_ENABLED", "True").lower() in ("true", "1", "yes")
PERFORMANCE_TRACKING = os.getenv("PERFORMANCE_TRACKING", "True").lower() in ("true", "1", "yes")

# Cache configuration
CACHE_TYPE = os.getenv("CACHE_TYPE", "simple")
CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", 300))  # 5 minutos

def get_config_summary() -> Dict[str, Any]:
    """Obtener resumen de configuración para debugging."""
    return {
        "llm": {
            "provider": LLM_PROVIDER,
            "model": LLM_MODEL,
            "temperature": DEFAULT_TEMPERATURE,
            "max_tokens": MAX_TOKENS
        },
        "flask": {
            "debug": FLASK_DEBUG,
            "env": FLASK_ENV,
            "port": PORT,
            "version": APP_VERSION
        },
        "features": {
            "use_langgraph": USE_LANGGRAPH,
            "metrics_enabled": METRICS_ENABLED,
            "performance_tracking": PERFORMANCE_TRACKING
        },
        "security": {
            "session_timeout": SESSION_TIMEOUT,
            "max_content_length": MAX_CONTENT_LENGTH,
            "rate_limit": RATE_LIMIT_PER_MINUTE
        },
        "validation": _validation
    }

def is_production() -> bool:
    """Verificar si estamos en modo producción."""
    return FLASK_ENV.lower() == "production"

def is_development() -> bool:
    """Verificar si estamos en modo desarrollo."""
    return FLASK_ENV.lower() in ("development", "dev")

# Log de configuración inicial
if is_development():
    logger.info("🔧 Running in DEVELOPMENT mode")
elif is_production():
    logger.info("🚀 Running in PRODUCTION mode")
else:
    logger.info(f"🔧 Running in {FLASK_ENV} mode")

logger.info(f"🤖 LLM Provider: {LLM_PROVIDER} | Model: {LLM_MODEL}")
logger.info(f"🧠 LangGraph: {'Enabled' if USE_LANGGRAPH else 'Disabled'}")
logger.info(f"📊 Metrics: {'Enabled' if METRICS_ENABLED else 'Disabled'}")

# Validación final
if is_production() and FLASK_SECRET_KEY == "your-secret-key-for-development":
    logger.error("🚨 SECURITY RISK: Using development secret key in production!")
    
if is_production() and FLASK_DEBUG:
    logger.warning("⚠️ DEBUG mode is enabled in production environment") 
#!/usr/bin/env python3
"""
Script de configuración del sistema AI-MedicalCenter-LangGraph
Valida dependencias, configura archivos y prepara el entorno.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SystemSetup:
    """Clase para configurar el sistema médico AI."""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.errors = []
        self.warnings = []
        
    def run_setup(self) -> bool:
        """Ejecutar configuración completa del sistema."""
        logger.info("🚀 Iniciando configuración del sistema AI-MedicalCenter-LangGraph")
        
        steps = [
            ("Verificar Python", self.check_python_version),
            ("Crear directorios", self.create_directories),
            ("Validar .env", self.check_env_file),
            ("Instalar dependencias", self.install_dependencies),
            ("Validar configuración", self.validate_configuration),
            ("Ejecutar tests", self.run_basic_tests),
            ("Configurar logging", self.setup_logging)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"📋 {step_name}...")
            try:
                success = step_func()
                if success:
                    logger.info(f"✅ {step_name} completado")
                else:
                    logger.error(f"❌ {step_name} falló")
                    return False
            except Exception as e:
                logger.error(f"❌ Error en {step_name}: {e}")
                self.errors.append(f"{step_name}: {e}")
                return False
        
        self.show_summary()
        return len(self.errors) == 0
    
    def check_python_version(self) -> bool:
        """Verificar versión de Python."""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.errors.append(f"Python 3.8+ requerido, encontrado {version.major}.{version.minor}")
            return False
        
        logger.info(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    
    def create_directories(self) -> bool:
        """Crear directorios necesarios."""
        directories = [
            "logs",
            "data/conversations",
            "flask_session",
            "src/static/uploads",
            "backups"
        ]
        
        for directory in directories:
            dir_path = self.base_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directorio creado: {dir_path}")
        
        return True
    
    def check_env_file(self) -> bool:
        """Verificar y crear archivo .env si no existe."""
        env_file = self.base_dir / ".env"
        env_example = self.base_dir / ".env.example"
        
        if not env_file.exists():
            self.warnings.append(".env file not found")
            
            # Crear .env básico si no existe
            env_content = self.create_basic_env()
            with open(env_file, 'w') as f:
                f.write(env_content)
            
            logger.warning("⚠️ Archivo .env creado con valores por defecto")
            logger.warning("🔧 IMPORTANTE: Edita .env con tus claves API reales")
            return True
        
        # Validar contenido del .env
        with open(env_file, 'r') as f:
            env_content = f.read()
        
        required_vars = ["OPENAI_API_KEY", "GROQ_API_KEY", "FLASK_SECRET_KEY"]
        missing_vars = []
        
        for var in required_vars:
            if var not in env_content:
                missing_vars.append(var)
        
        if missing_vars:
            self.warnings.append(f"Variables faltantes en .env: {', '.join(missing_vars)}")
        
        return True
    
    def create_basic_env(self) -> str:
        """Crear contenido básico para archivo .env."""
        return """# Variables de entorno para AI-MedicalCenter-LangGraph
# =====================================================

# ===== CLAVES API =====
# Obtén tu clave en: https://platform.openai.com/api-keys
OPENAI_API_KEY=tu_clave_openai_aqui

# Obtén tu clave en: https://console.groq.com/keys
GROQ_API_KEY=tu_clave_groq_aqui

# ===== CONFIGURACIÓN LLM =====
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
DEFAULT_TEMPERATURE=0.2

# ===== CONFIGURACIÓN FLASK =====
FLASK_SECRET_KEY=tu_clave_secreta_super_segura_aqui
FLASK_ENV=development
FLASK_DEBUG=True
APP_VERSION=1.0.0

# ===== CONFIGURACIÓN DEL SISTEMA =====
USE_LANGGRAPH=True
PORT=3567

# ===== CONFIGURACIÓN DE LOGGING =====
LOG_LEVEL=INFO
LOG_FILE_SIZE=10MB
LOG_BACKUP_COUNT=5

# ===== CONFIGURACIÓN DE SEGURIDAD =====
SESSION_TIMEOUT=3600
MAX_CONTENT_LENGTH=16777216
RATE_LIMIT_PER_MINUTE=60

# ===== CONFIGURACIÓN DE MONITOREO =====
METRICS_ENABLED=True
PERFORMANCE_TRACKING=True
"""
    
    def install_dependencies(self) -> bool:
        """Instalar dependencias de Python."""
        try:
            logger.info("📦 Instalando dependencias...")
            
            # Verificar si pip está disponible
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         check=True, capture_output=True)
            
            # Instalar dependencias
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], check=True, capture_output=True)
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.errors.append(f"Error instalando dependencias: {e}")
            return False
    
    def validate_configuration(self) -> bool:
        """Validar configuración del sistema."""
        try:
            # Intentar importar configuración
            sys.path.insert(0, str(self.base_dir / "src"))
            from config.config import get_config_summary, validate_required_env_vars
            
            # Validar variables de entorno
            validation = validate_required_env_vars()
            
            if not validation["valid"]:
                self.errors.extend(validation["errors"])
                return False
            
            if validation["warnings"]:
                self.warnings.extend(validation["warnings"])
            
            # Mostrar resumen de configuración
            config = get_config_summary()
            logger.info(f"🤖 Provider: {config['llm']['provider']}")
            logger.info(f"🧠 Model: {config['llm']['model']}")
            logger.info(f"🔄 LangGraph: {config['features']['use_langgraph']}")
            
            return True
            
        except ImportError as e:
            self.errors.append(f"Error importando configuración: {e}")
            return False
    
    def run_basic_tests(self) -> bool:
        """Ejecutar tests básicos del sistema."""
        try:
            logger.info("🧪 Ejecutando tests básicos...")
            
            # Ejecutar el script de test
            result = subprocess.run([
                sys.executable, "test_system.py"
            ], capture_output=True, text=True, cwd=self.base_dir)
            
            if result.returncode == 0:
                logger.info("✅ Tests básicos pasaron")
                return True
            else:
                logger.error(f"❌ Tests fallaron: {result.stderr}")
                self.errors.append("Tests básicos fallaron")
                return False
                
        except Exception as e:
            self.warnings.append(f"No se pudieron ejecutar tests: {e}")
            return True  # No es crítico
    
    def setup_logging(self) -> bool:
        """Configurar sistema de logging."""
        logs_dir = self.base_dir / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # Crear archivos de log iniciales
        log_files = ["app.log", "agents.log", "performance.log", "errors.log"]
        
        for log_file in log_files:
            log_path = logs_dir / log_file
            if not log_path.exists():
                log_path.touch()
        
        return True
    
    def show_summary(self):
        """Mostrar resumen de la configuración."""
        logger.info("\n" + "="*60)
        logger.info("📊 RESUMEN DE CONFIGURACIÓN")
        logger.info("="*60)
        
        if not self.errors:
            logger.info("✅ Sistema configurado exitosamente")
        else:
            logger.error(f"❌ {len(self.errors)} errores encontrados:")
            for error in self.errors:
                logger.error(f"   • {error}")
        
        if self.warnings:
            logger.warning(f"⚠️ {len(self.warnings)} advertencias:")
            for warning in self.warnings:
                logger.warning(f"   • {warning}")
        
        logger.info("\n🚀 Para iniciar el sistema:")
        logger.info("   python -m src.app")
        logger.info("\n🐳 O con Docker:")
        logger.info("   docker-compose up -d")
        
        if self.warnings:
            logger.info("\n🔧 RECUERDA:")
            logger.info("   • Configurar claves API reales en .env")
            logger.info("   • Cambiar FLASK_SECRET_KEY en producción")

def main():
    """Función principal."""
    setup = SystemSetup()
    success = setup.run_setup()
    
    if success:
        logger.info("🎉 ¡Configuración completada exitosamente!")
        sys.exit(0)
    else:
        logger.error("💥 Configuración falló. Revisa los errores arriba.")
        sys.exit(1)

if __name__ == "__main__":
    main() 
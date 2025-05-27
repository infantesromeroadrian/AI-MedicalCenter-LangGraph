#!/usr/bin/env python3
"""
Script de diagnóstico para el servicio de análisis de imágenes médicas.
Verifica la configuración y dependencias necesarias.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def check_environment():
    """Verificar variables de entorno"""
    print("🔍 Verificando variables de entorno...")
    
    # Cargar archivo .env si existe
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv()
        print("✅ Archivo .env encontrado y cargado")
    else:
        print("❌ Archivo .env no encontrado")
        return False
    
    # Verificar OPENAI_API_KEY
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        if api_key.startswith("sk-"):
            print("✅ OPENAI_API_KEY configurada correctamente")
        else:
            print("⚠️  OPENAI_API_KEY no parece válida (debe empezar con 'sk-')")
            return False
    else:
        print("❌ OPENAI_API_KEY no configurada")
        return False
    
    # Verificar otros parámetros
    default_model = os.getenv("DEFAULT_MODEL", "gpt-4.1")
    backup_model = os.getenv("BACKUP_MODEL", "gpt-4-vision-preview")
    
    print(f"📋 Modelo por defecto: {default_model}")
    print(f"📋 Modelo de respaldo: {backup_model}")
    
    return True

def check_dependencies():
    """Verificar dependencias de Python"""
    print("\n🔍 Verificando dependencias...")
    
    required_packages = [
        'openai',
        'langchain',
        'langchain_openai',
        'flask',
        'python-dotenv',
        'pillow'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NO INSTALADO")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Paquetes faltantes: {', '.join(missing_packages)}")
        print("💡 Ejecute: pip install -r requirements.txt")
        return False
    
    return True

def check_directories():
    """Verificar directorios necesarios"""
    print("\n🔍 Verificando directorios...")
    
    directories = [
        "src/static/uploads/images",
        "logs",
        "flask_session"
    ]
    
    all_exist = True
    for directory in directories:
        dir_path = Path(directory)
        if dir_path.exists():
            print(f"✅ {directory}")
        else:
            print(f"❌ {directory} - NO EXISTE")
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ {directory} - CREADO")
            except Exception as e:
                print(f"❌ No se pudo crear {directory}: {e}")
                all_exist = False
    
    return all_exist

def test_image_analyzer():
    """Probar la inicialización del analizador de imágenes"""
    print("\n🔍 Probando analizador de imágenes...")
    
    try:
        # Importar y crear el analizador
        sys.path.append('src')
        from services.image_analysis_service import MedicalImageAnalyzer
        
        analyzer = MedicalImageAnalyzer()
        print(f"✅ Analizador inicializado con modelo: {analyzer.model_name}")
        return True
        
    except Exception as e:
        print(f"❌ Error al inicializar analizador: {str(e)}")
        
        # Diagnóstico específico de errores comunes
        if "API key" in str(e).lower():
            print("💡 Problema con API Key de OpenAI")
        elif "model" in str(e).lower():
            print("💡 Problema con el modelo especificado")
        elif "network" in str(e).lower() or "connection" in str(e).lower():
            print("💡 Problema de conexión a internet")
        
        return False

def generate_env_template():
    """Generar plantilla de archivo .env"""
    print("\n📝 Generando plantilla de .env...")
    
    template = '''# Configuración de OpenAI para análisis de imágenes
OPENAI_API_KEY=sk-tu_api_key_aqui

# Configuración de la aplicación Flask
SECRET_KEY=medical-ai-secret-key-12345
FLASK_ENV=development
APP_VERSION=1.0.0
PORT=5000

# Configuración del modelo de IA
DEFAULT_MODEL=gpt-4.1
BACKUP_MODEL=gpt-4-vision-preview
MODEL_TEMPERATURE=0.2
MAX_TOKENS=1000

# Configuración de archivos
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=src/static/uploads
'''
    
    env_file = Path(".env")
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(template)
        print("✅ Archivo .env creado con plantilla")
        print("⚠️  IMPORTANTE: Configure su OPENAI_API_KEY en el archivo .env")
    else:
        print("ℹ️  Archivo .env ya existe")

def main():
    """Función principal de diagnóstico"""
    print("🏥 Diagnóstico del Sistema de Análisis de Imágenes Médicas")
    print("=" * 60)
    
    # Cambiar al directorio raíz del proyecto
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    os.chdir(project_root)
    
    tests = [
        ("Variables de entorno", check_environment),
        ("Dependencias", check_dependencies),
        ("Directorios", check_directories),
        ("Analizador de imágenes", test_image_analyzer)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DEL DIAGNÓSTICO")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name:<25} {status}")
    
    print(f"\nResultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todos los sistemas funcionando correctamente!")
    else:
        print("⚠️  Hay problemas que necesitan resolverse")
        
        # Generar plantilla si no existe .env
        if not Path(".env").exists():
            generate_env_template()

if __name__ == "__main__":
    main() 
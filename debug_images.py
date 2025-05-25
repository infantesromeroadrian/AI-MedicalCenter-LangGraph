#!/usr/bin/env python3
"""
Script de depuración para el sistema de imágenes diagnósticas.
Verifica que las imágenes se guarden y vinculen correctamente.
"""

import os
import sys
import requests
from pathlib import Path

def check_image_system():
    """Verificar el estado del sistema de imágenes"""
    
    print("🔍 Verificando sistema de imágenes diagnósticas...\n")
    
    # 1. Verificar estructura de directorios
    print("📁 Verificando directorios:")
    upload_dir = Path("src/static/uploads/images")
    if upload_dir.exists():
        print(f"  ✅ Directorio de uploads existe: {upload_dir}")
        print(f"  📊 Imágenes guardadas: {len(list(upload_dir.glob('*.*')))}")
    else:
        print(f"  ❌ Directorio de uploads no existe: {upload_dir}")
    
    print()
    
    # 2. Verificar endpoint de estado
    print("🌐 Verificando endpoint de estado:")
    try:
        response = requests.get("http://localhost:5000/images/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("  ✅ Endpoint de estado responde correctamente")
            print(f"  🤖 Servicio disponible: {data.get('service_available', 'No reportado')}")
            print(f"  📂 Directorio upload existe: {data.get('upload_folder_exists', 'No reportado')}")
            print(f"  🔑 API Key configurada: {data.get('environment', {}).get('openai_api_key_configured', 'No reportado')}")
        else:
            print(f"  ❌ Error en endpoint: HTTP {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"  ❌ No se puede conectar al servidor: {e}")
    
    print()
    
    # 3. Verificar archivos de configuración
    print("⚙️ Verificando configuración:")
    env_file = Path(".env")
    if env_file.exists():
        print("  ✅ Archivo .env existe")
        try:
            with open(env_file, 'r') as f:
                content = f.read()
                if "OPENAI_API_KEY" in content:
                    print("  ✅ OPENAI_API_KEY configurado en .env")
                else:
                    print("  ❌ OPENAI_API_KEY no encontrado en .env")
        except Exception as e:
            print(f"  ⚠️ Error leyendo .env: {e}")
    else:
        print("  ❌ Archivo .env no existe")
    
    print()
    
    # 4. Verificar endpoint de recursos médicos
    print("🏥 Verificando endpoint de recursos médicos:")
    try:
        # Usar un ID de conversación de ejemplo
        response = requests.get("http://localhost:5000/medical-resources/diagnostic-images/test-conversation", timeout=5)
        print(f"  📊 Respuesta: HTTP {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  🖼️ Imágenes encontradas: {data.get('count', 0)}")
        elif response.status_code == 404:
            print("  ℹ️ Conversación de prueba no encontrada (normal)")
    except requests.exceptions.RequestException as e:
        print(f"  ❌ No se puede conectar al endpoint: {e}")
    
    print()
    
    # 5. Verificar logs recientes
    print("📋 Verificando logs recientes:")
    log_file = Path("logs/app.log")
    if log_file.exists():
        print("  ✅ Archivo de logs existe")
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                recent_lines = lines[-10:] if len(lines) > 10 else lines
                
            image_related = [line for line in recent_lines if 'imagen' in line.lower() or 'image' in line.lower()]
            if image_related:
                print("  📸 Entradas recientes relacionadas con imágenes:")
                for line in image_related[-3:]:  # Últimas 3
                    print(f"    📝 {line.strip()}")
            else:
                print("  ℹ️ No hay entradas recientes sobre imágenes")
        except Exception as e:
            print(f"  ⚠️ Error leyendo logs: {e}")
    else:
        print("  ❌ Archivo de logs no existe")
    
    print("\n" + "="*60)
    print("🎯 INSTRUCCIONES PARA PROBAR:")
    print("1. Inicie el servidor: python src/app.py")
    print("2. Vaya a http://localhost:5000/interactive")
    print("3. Inicie una nueva consulta con síntomas")
    print("4. Haga clic en el botón 📷 Imagen")
    print("5. Suba una imagen médica (ej: radiografía, erupción cutánea)")
    print("6. Espere el análisis")
    print("7. Haga clic en 'Imágenes diagnósticas' en el panel lateral")
    print("8. Verifique que la imagen aparece en el modal")
    print("="*60)

if __name__ == "__main__":
    check_image_system() 
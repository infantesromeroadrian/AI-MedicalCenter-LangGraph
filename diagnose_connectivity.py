#!/usr/bin/env python3
"""
Script de diagnóstico de conectividad para AI-MedicalCenter-LangGraph
Identifica y proporciona soluciones para problemas de red y API.
"""

import os
import sys
import asyncio
import socket
import subprocess
import logging
from pathlib import Path
import requests
from typing import Dict, List, Tuple
import dns.resolver

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConnectivityDiagnostic:
    """Clase para diagnosticar problemas de conectividad."""
    
    def __init__(self):
        self.results = []
        self.errors = []
        self.warnings = []
        
    async def run_full_diagnostic(self) -> bool:
        """Ejecutar diagnóstico completo de conectividad."""
        logger.info("🔍 Iniciando diagnóstico de conectividad completo")
        
        tests = [
            ("DNS Resolution", self.test_dns_resolution),
            ("Internet Connectivity", self.test_internet_connectivity),
            ("OpenAI API Access", self.test_openai_api),
            ("Groq API Access", self.test_groq_api),
            ("Docker Network", self.test_docker_network),
            ("Environment Variables", self.test_env_vars),
            ("System Resources", self.test_system_resources)
        ]
        
        for test_name, test_func in tests:
            logger.info(f"🧪 Ejecutando: {test_name}")
            try:
                success = await test_func()
                if success:
                    logger.info(f"✅ {test_name}: OK")
                    self.results.append(f"✅ {test_name}: OK")
                else:
                    logger.error(f"❌ {test_name}: FAILED")
                    self.errors.append(f"❌ {test_name}: FAILED")
            except Exception as e:
                logger.error(f"❌ {test_name}: ERROR - {e}")
                self.errors.append(f"❌ {test_name}: ERROR - {e}")
        
        self.show_diagnostic_report()
        self.provide_solutions()
        
        return len(self.errors) == 0
    
    async def test_dns_resolution(self) -> bool:
        """Test DNS resolution for critical domains."""
        domains = [
            "api.openai.com",
            "api.groq.com", 
            "google.com",
            "cloudflare.com"
        ]
        
        all_resolved = True
        
        for domain in domains:
            try:
                # Test with different DNS servers
                for dns_server in ["8.8.8.8", "1.1.1.1", "208.67.222.222"]:
                    resolver = dns.resolver.Resolver()
                    resolver.nameservers = [dns_server]
                    result = resolver.resolve(domain, 'A')
                    logger.debug(f"✅ {domain} resolved via {dns_server}: {result[0]}")
                    break
            except Exception as e:
                logger.warning(f"⚠️ DNS resolution failed for {domain}: {e}")
                all_resolved = False
        
        return all_resolved
    
    async def test_internet_connectivity(self) -> bool:
        """Test basic internet connectivity."""
        test_urls = [
            "http://google.com",
            "http://cloudflare.com", 
            "https://httpbin.org/ip"
        ]
        
        for url in test_urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    logger.debug(f"✅ Internet test successful: {url}")
                    return True
            except Exception as e:
                logger.debug(f"⚠️ Internet test failed for {url}: {e}")
        
        return False
    
    async def test_openai_api(self) -> bool:
        """Test OpenAI API connectivity."""
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key or api_key == "tu_clave_openai_aqui":
            self.warnings.append("⚠️ OPENAI_API_KEY not configured")
            return False
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key, timeout=15.0)
            
            # Test simple API call
            models = client.models.list()
            logger.debug(f"✅ OpenAI API accessible, found {len(models.data)} models")
            return True
            
        except Exception as e:
            logger.error(f"❌ OpenAI API test failed: {e}")
            return False
    
    async def test_groq_api(self) -> bool:
        """Test Groq API connectivity."""
        api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key or api_key == "tu_clave_groq_aqui":
            self.warnings.append("⚠️ GROQ_API_KEY not configured")
            return False
        
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1",
                timeout=15.0
            )
            
            # Test simple API call
            models = client.models.list()
            logger.debug(f"✅ Groq API accessible, found {len(models.data)} models")
            return True
            
        except Exception as e:
            logger.error(f"❌ Groq API test failed: {e}")
            return False
    
    async def test_docker_network(self) -> bool:
        """Test Docker network configuration."""
        try:
            # Check if running in Docker
            if os.path.exists("/.dockerenv"):
                logger.info("🐳 Running inside Docker container")
                
                # Test internal Docker DNS
                result = subprocess.run(
                    ["nslookup", "google.com"],
                    capture_output=True, text=True, timeout=10
                )
                
                if result.returncode == 0:
                    logger.debug("✅ Docker DNS resolution working")
                    return True
                else:
                    logger.error(f"❌ Docker DNS issues: {result.stderr}")
                    return False
            else:
                logger.info("💻 Running on host system")
                return True
                
        except Exception as e:
            logger.error(f"❌ Docker network test failed: {e}")
            return False
    
    async def test_env_vars(self) -> bool:
        """Test environment variables configuration."""
        required_vars = ["OPENAI_API_KEY", "GROQ_API_KEY", "FLASK_SECRET_KEY"]
        missing_vars = []
        placeholder_vars = []
        
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
            elif value in ["tu_clave_openai_aqui", "tu_clave_groq_aqui", "tu_clave_secreta_super_segura_aqui"]:
                placeholder_vars.append(var)
        
        if missing_vars:
            self.errors.append(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        
        if placeholder_vars:
            self.warnings.append(f"⚠️ Placeholder values detected: {', '.join(placeholder_vars)}")
        
        return len(missing_vars) == 0
    
    async def test_system_resources(self) -> bool:
        """Test system resources availability."""
        try:
            import psutil
            
            # Memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                self.warnings.append(f"⚠️ High memory usage: {memory.percent}%")
            
            # Disk space
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                self.warnings.append(f"⚠️ Low disk space: {disk.percent}% used")
            
            logger.debug(f"System resources - Memory: {memory.percent}%, Disk: {disk.percent}%")
            return True
            
        except ImportError:
            logger.warning("psutil not available, skipping resource check")
            return True
        except Exception as e:
            logger.error(f"System resource check failed: {e}")
            return False
    
    def show_diagnostic_report(self):
        """Mostrar reporte de diagnóstico."""
        print("\n" + "="*60)
        print("📊 REPORTE DE DIAGNÓSTICO DE CONECTIVIDAD")
        print("="*60)
        
        if self.results:
            print("\n✅ TESTS EXITOSOS:")
            for result in self.results:
                print(f"   {result}")
        
        if self.errors:
            print("\n❌ ERRORES ENCONTRADOS:")
            for error in self.errors:
                print(f"   {error}")
        
        if self.warnings:
            print("\n⚠️ ADVERTENCIAS:")
            for warning in self.warnings:
                print(f"   {warning}")
    
    def provide_solutions(self):
        """Proporcionar soluciones específicas para los problemas encontrados."""
        print("\n" + "="*60)
        print("🛠️ SOLUCIONES RECOMENDADAS")
        print("="*60)
        
        if any("DNS" in error for error in self.errors):
            print("\n🔧 PROBLEMA DNS DETECTADO:")
            print("   1. Reinicia Docker: docker-compose down && docker-compose up -d")
            print("   2. Configura DNS en docker-compose.yml:")
            print("      dns:")
            print("        - 8.8.8.8")
            print("        - 8.8.4.4")
        
        if any("API" in error for error in self.errors):
            print("\n🔑 PROBLEMA DE CLAVES API:")
            print("   1. Verifica que las claves API están configuradas en .env")
            print("   2. Obtén claves válidas:")
            print("      - OpenAI: https://platform.openai.com/api-keys")
            print("      - Groq: https://console.groq.com/keys")
            print("   3. Asegúrate que las claves no tienen caracteres extra")
        
        if any("Docker" in error for error in self.errors):
            print("\n🐳 PROBLEMA DE RED DOCKER:")
            print("   1. Reinicia el servicio Docker")
            print("   2. Limpia la red: docker network prune")
            print("   3. Reconstruye el contenedor: docker-compose up -d --build")
        
        if any("Internet" in error for error in self.errors):
            print("\n🌐 PROBLEMA DE CONECTIVIDAD:")
            print("   1. Verifica tu conexión a internet")
            print("   2. Verifica proxy/firewall empresarial")
            print("   3. Intenta desde otra red")
        
        print("\n🚀 COMANDOS RÁPIDOS DE SOLUCIÓN:")
        print("   # Reiniciar sistema completo")
        print("   docker-compose down && docker-compose up -d --build")
        print("   ")
        print("   # Verificar logs")
        print("   docker-compose logs -f")
        print("   ")
        print("   # Test manual")
        print("   python diagnose_connectivity.py")

async def main():
    """Función principal."""
    print("🔍 Diagnóstico de Conectividad AI-MedicalCenter-LangGraph")
    print("=" * 60)
    
    # Cargar variables de entorno
    from dotenv import load_dotenv
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv(env_file)
        print("✅ Archivo .env cargado")
    else:
        print("⚠️ Archivo .env no encontrado")
    
    diagnostic = ConnectivityDiagnostic()
    success = await diagnostic.run_full_diagnostic()
    
    if success:
        print("\n🎉 ¡Todos los tests de conectividad pasaron!")
        sys.exit(0)
    else:
        print("\n💥 Se encontraron problemas de conectividad.")
        print("Revisa las soluciones arriba y ejecuta el diagnóstico nuevamente.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 
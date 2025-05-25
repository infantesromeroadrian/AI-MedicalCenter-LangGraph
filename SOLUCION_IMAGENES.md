# 🔧 Solución: Error al Subir Imágenes

## ❌ Problema
> Error de comunicación con el servidor al procesar la imagen.

## ✅ Solución Paso a Paso

### **Paso 1: Crear archivo .env**

Cree un archivo llamado `.env` en la raíz del proyecto (mismo nivel que `app.py`) con este contenido:

```env
# Configuración de OpenAI para análisis de imágenes
OPENAI_API_KEY=sk-your_openai_api_key_here

# Configuración de la aplicación Flask
SECRET_KEY=medical-ai-secret-key-12345
FLASK_ENV=development
APP_VERSION=1.0.0
PORT=5000

# Configuración del modelo de IA
DEFAULT_MODEL=gpt-4o
BACKUP_MODEL=gpt-4-vision-preview
MODEL_TEMPERATURE=0.2
MAX_TOKENS=1000

# Configuración de archivos
MAX_CONTENT_LENGTH=16777216
UPLOAD_FOLDER=src/static/uploads
```

### **Paso 2: Obtener API Key de OpenAI**

1. Visite [OpenAI API](https://platform.openai.com/api-keys)
2. Inicie sesión en su cuenta
3. Cree una nueva API key
4. Copie la key (empieza con `sk-`)
5. Reemplace `sk-your_openai_api_key_here` en el archivo `.env`

### **Paso 3: Instalar dependencias**

```bash
pip install -r requirements.txt
```

### **Paso 4: Ejecutar diagnóstico**

```bash
python src/utils/diagnose_image_service.py
```

### **Paso 5: Reiniciar el servidor**

```bash
python src/app.py
```

## 🔍 Verificación del Estado

Visite: `http://localhost:5000/images/status`

Debería ver algo como:
```json
{
  "service_available": true,
  "model_initialized": true,
  "model_name": "gpt-4o",
  "environment": {
    "openai_api_key_configured": true
  }
}
```

## 🚨 Errores Comunes

### Error: "API key no configurada"
- ✅ Verifique que el archivo `.env` existe
- ✅ Verifique que `OPENAI_API_KEY` está configurada
- ✅ Reinicie el servidor

### Error: "Servicio no disponible"
- ✅ Ejecute el diagnóstico: `python src/utils/diagnose_image_service.py`
- ✅ Verifique que tiene créditos en su cuenta de OpenAI
- ✅ Pruebe con el modelo de respaldo

### Error: "Imagen no médica"
- ✅ Use imágenes relacionadas con medicina
- ✅ Pruebe con síntomas visibles, radiografías, etc.

## 📋 Formatos Soportados

- **Tipos**: PNG, JPG, JPEG
- **Tamaño máximo**: 16 MB
- **Contenido**: Imágenes médicas o relacionadas con salud

## 🛠️ Comandos Útiles

```bash
# Diagnóstico completo
python src/utils/diagnose_image_service.py

# Verificar estado del servicio
curl http://localhost:5000/images/status

# Ver logs del servidor
tail -f logs/app.log

# Reinstalar dependencias
pip install --upgrade -r requirements.txt
```

## 📞 Soporte Adicional

Si el problema persiste:

1. Revise los logs en `logs/app.log`
2. Ejecute el diagnóstico completo
3. Verifique su saldo en OpenAI
4. Intente con una imagen diferente

## ✅ Verificación Final

Para confirmar que todo funciona:

1. **Abra** el chat interactivo
2. **Haga clic** en el botón de cámara 📷
3. **Seleccione** una imagen médica
4. **Debería ver** el análisis en segundos

¡El sistema ahora debería funcionar correctamente! 🎉 
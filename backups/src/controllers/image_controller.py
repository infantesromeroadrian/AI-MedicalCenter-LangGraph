"""
Controlador Flask para gestionar el análisis de imágenes médicas.
Proporciona endpoints para la carga y análisis de imágenes.
"""
import os
from pathlib import Path
import uuid
import logging
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from werkzeug.utils import secure_filename
from src.services.image_analysis_service import MedicalImageAnalyzer
from src.utils.auth_middleware import login_required

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear el blueprint para rutas relacionadas con imágenes
image_bp = Blueprint('image', __name__, url_prefix='/images')

# Inicializar el analizador de imágenes
try:
    image_analyzer = MedicalImageAnalyzer()
    logger.info("Analizador de imágenes médicas inicializado correctamente")
except Exception as e:
    logger.error(f"Error al inicializar el analizador de imágenes: {e}")
    image_analyzer = None
    logger.warning("El análisis de imágenes no estará disponible hasta que se configure correctamente")

# Extensiones de imagen permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}

def allowed_file(filename):
    """
    Verifica que el archivo tenga una extensión permitida
    
    Args:
        filename: Nombre del archivo a verificar
        
    Returns:
        bool: True si el archivo tiene una extensión válida
    """
    if not filename or '.' not in filename:
        logger.warning(f"Archivo sin extensión: {filename}")
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    is_allowed = extension in ALLOWED_EXTENSIONS
    
    if not is_allowed:
        logger.warning(f"Extensión no permitida: {extension}. Archivo: {filename}")
        logger.info(f"Extensiones permitidas: {', '.join(ALLOWED_EXTENSIONS)}")
    else:
        logger.info(f"Archivo válido: {filename} (extensión: {extension})")
    
    return is_allowed

def is_valid_image_content(file):
    """
    Verifica que el contenido del archivo sea realmente una imagen
    
    Args:
        file: Archivo subido
        
    Returns:
        bool: True si el contenido es una imagen válida
    """
    try:
        from PIL import Image
        file.seek(0)  # Ir al inicio del archivo
        Image.open(file)
        file.seek(0)  # Volver al inicio para uso posterior
        return True
    except Exception as e:
        logger.warning(f"El archivo no es una imagen válida: {e}")
        return False

def get_upload_folder():
    """
    Obtiene y crea (si no existe) la carpeta para guardar las imágenes cargadas
    
    Returns:
        Path: Ruta absoluta a la carpeta de carga
    """
    upload_folder = Path(current_app.static_folder) / 'uploads' / 'images'
    
    # Crear la carpeta si no existe
    if not upload_folder.exists():
        upload_folder.mkdir(parents=True, exist_ok=True)
    
    return upload_folder

@image_bp.route('/', methods=['GET'])
@login_required
def index():
    """Página principal para análisis de imágenes médicas"""
    return render_template('image_analysis.html')

@image_bp.route('/status', methods=['GET'])
def system_status():
    """Endpoint para verificar el estado del sistema de análisis de imágenes"""
    status = {
        'service_available': image_analyzer is not None,
        'timestamp': datetime.now().isoformat(),
        'upload_folder_exists': get_upload_folder().exists(),
        'allowed_extensions': list(ALLOWED_EXTENSIONS)
    }
    
    if image_analyzer is not None:
        status.update({
            'model_name': image_analyzer.model_name,
            'model_initialized': True
        })
    else:
        status.update({
            'model_name': None,
            'model_initialized': False,
            'error': 'Analizador de imágenes no inicializado. Verifique OPENAI_API_KEY en .env'
        })
    
    # Verificar variables de entorno críticas
    status['environment'] = {
        'openai_api_key_configured': bool(os.getenv("OPENAI_API_KEY")),
        'default_model': os.getenv("DEFAULT_MODEL", "No configurado"),
        'backup_model': os.getenv("BACKUP_MODEL", "No configurado")
    }
    
    return jsonify(status)

@image_bp.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze():
    """Endpoint para analizar imágenes médicas"""
    if request.method == 'POST':
        # Verificar si hay un archivo en la solicitud
        if 'image' not in request.files:
            flash('No se ha seleccionado ninguna imagen', 'danger')
            return redirect(request.url)
        
        file = request.files['image']
        
        # Verificar si se seleccionó un archivo
        if file.filename == '':
            flash('No se ha seleccionado ninguna imagen', 'danger')
            return redirect(request.url)
        
        # Verificar tipo de archivo
        if not file or not allowed_file(file.filename):
            flash('Formato de archivo no permitido. Use PNG, JPG o JPEG.', 'danger')
            return redirect(request.url)
        
        try:
            # Generar nombre de archivo único para evitar colisiones
            original_filename = secure_filename(file.filename)
            filename = f"{uuid.uuid4().hex}_{original_filename}"
            
            # Guardar el archivo
            upload_folder = get_upload_folder()
            file_path = upload_folder / filename
            file.save(file_path)
            
            logger.info(f"Imagen guardada en {file_path}")
            
            # Obtener datos del formulario
            description = request.form.get('description', '')
            body_part = request.form.get('bodyPart', 'other')
            
            # Mapear el área del cuerpo a una especialidad
            specialty_map = {
                'skin': 'dermatología',
                'joint': 'reumatología',
                'eye': 'oftalmología',
                'mouth': 'otorrinolaringología',
                'chest': 'neumología',
                'abdomen': 'gastroenterología',
                'head': 'neurología',
                'other': 'medicina_general'
            }
            specialty = specialty_map.get(body_part, 'medicina_general')
            
            # Verificar si la imagen es de contenido médico apropiado
            if not image_analyzer.is_medical_image(file_path):
                # Eliminar la imagen inapropiada
                os.remove(file_path)
                flash('La imagen no parece ser de contenido médico.', 'warning')
                return redirect(request.url)
            
            # Analizar la imagen
            analysis_result = image_analyzer.analyze_image(
                file_path,
                patient_context=description,
                specialty=specialty
            )
            
            # URL relativa para mostrar la imagen en la plantilla
            image_url = url_for('static', filename=f'uploads/images/{filename}')
            
            # Si es una solicitud AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True,
                    'analysis_result': analysis_result,
                    'image_url': image_url
                })
            
            # De lo contrario, renderizar plantilla
            return render_template(
                'image_analysis.html',
                analysis_result=analysis_result,
                image_url=image_url,
                description=description,
                body_part=body_part
            )
        
        except Exception as e:
            logger.error(f"Error durante el análisis de imagen: {str(e)}")
            flash('Error al procesar la imagen. Por favor, intente nuevamente.', 'danger')
            return redirect(request.url)
            
    # Método GET
    return render_template('image_analysis.html')

@image_bp.route('/api/analyze', methods=['POST'])
@login_required
def api_analyze():
    """API endpoint para análisis de imágenes (JSON)"""
    # Verificar si el analizador está disponible
    if image_analyzer is None:
        logger.error("Intento de análisis de imagen sin analizador inicializado")
        return jsonify({
            'error': 'Servicio de análisis de imágenes no disponible',
            'details': 'El analizador de imágenes no se pudo inicializar. Verifique la configuración de OPENAI_API_KEY en el archivo .env'
        }), 503
    
    if 'image' not in request.files:
        logger.error("No se encontró el campo 'image' en la solicitud")
        return jsonify({
            'error': 'No se ha proporcionado ninguna imagen',
            'details': 'El campo "image" no está presente en la solicitud'
        }), 400
    
    file = request.files['image']
    logger.info(f"Archivo recibido: {file.filename}, tipo MIME: {file.content_type}")
    
    if file.filename == '':
        logger.error("Nombre de archivo vacío")
        return jsonify({
            'error': 'No se ha seleccionado ninguna imagen',
            'details': 'El nombre del archivo está vacío'
        }), 400
    
    if not allowed_file(file.filename):
        extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'sin extensión'
        return jsonify({
            'error': f'Formato de archivo no permitido: {extension}',
            'details': f'Extensiones soportadas: {", ".join(sorted(ALLOWED_EXTENSIONS))}',
            'received_filename': file.filename,
            'received_content_type': file.content_type
        }), 400
    
    # Validar contenido de imagen
    if not is_valid_image_content(file):
        return jsonify({
            'error': 'El archivo no es una imagen válida',
            'details': 'El contenido del archivo no puede ser procesado como imagen',
            'received_filename': file.filename,
            'received_content_type': file.content_type
        }), 400
    
    file_path = None
    try:
        # Procesar la imagen como en la ruta normal
        original_filename = secure_filename(file.filename)
        filename = f"{uuid.uuid4().hex}_{original_filename}"
        
        upload_folder = get_upload_folder()
        file_path = upload_folder / filename
        file.save(file_path)
        
        logger.info(f"Imagen guardada para análisis: {filename}")
        
        # Obtener datos del formulario
        description = request.form.get('description', '')
        specialty = request.form.get('specialty', 'medicina_general')
        conversation_id = request.form.get('conversation_id', None)
        
        # Verificar si la imagen es médica antes del análisis
        try:
            is_medical = image_analyzer.is_medical_image(file_path)
            if not is_medical:
                # Eliminar la imagen no médica
                os.remove(file_path)
                return jsonify({
                    'error': 'La imagen no parece ser de contenido médico',
                    'details': 'Por favor, suba una imagen relacionada con medicina o síntomas médicos'
                }), 400
        except Exception as medical_check_error:
            logger.warning(f"No se pudo verificar si la imagen es médica: {medical_check_error}")
            # Continuar con el análisis aunque falle la verificación
        
        # Analizar la imagen
        logger.info(f"Iniciando análisis de imagen con especialidad: {specialty}")
        analysis_result = image_analyzer.analyze_image(
            file_path,
            patient_context=description,
            specialty=specialty
        )
        
        if not analysis_result or "Error" in analysis_result:
            logger.error(f"El análisis de imagen falló o retornó error: {analysis_result}")
            return jsonify({
                'error': 'No se pudo analizar la imagen',
                'details': analysis_result or 'El servicio de análisis no respondió correctamente'
            }), 500
        
        # URL para la imagen
        image_url = url_for('static', filename=f'uploads/images/{filename}', _external=True)
        
        # Si hay un ID de conversación, intentar agregar el análisis al historial de la conversación
        if conversation_id:
            try:
                from src.services.conversation_service import ConversationService
                conversation_service = ConversationService()
                conversation = conversation_service.get_conversation(conversation_id)
                if conversation:
                    # Guardar tanto el análisis como la URL de la imagen
                    system_message = f"[IMAGEN ANALIZADA:{image_url}] {analysis_result}"
                    conversation.add_message(content=system_message, sender="system")
                    conversation_service._save_conversation(conversation_id)
                    logger.info(f"Análisis de imagen agregado a conversación: {conversation_id} con URL: {image_url}")
            except Exception as conv_error:
                logger.error(f"Error al agregar análisis a la conversación: {conv_error}")
                # No falla la operación si no se puede guardar en la conversación
        
        logger.info(f"Análisis de imagen completado exitosamente para: {filename}")
        return jsonify({
            'success': True,
            'analysis': analysis_result,
            'image_url': image_url
        })
        
    except FileNotFoundError as fnf_error:
        logger.error(f"Archivo no encontrado durante análisis: {str(fnf_error)}")
        return jsonify({
            'error': 'Archivo de imagen no encontrado',
            'details': 'La imagen se perdió durante el procesamiento'
        }), 500
        
    except PermissionError as perm_error:
        logger.error(f"Error de permisos durante análisis: {str(perm_error)}")
        return jsonify({
            'error': 'Error de permisos al procesar la imagen',
            'details': 'Verifique los permisos del directorio de uploads'
        }), 500
        
    except Exception as e:
        logger.error(f"Error durante el análisis de imagen API: {str(e)}")
        # Limpiar archivo si existe y hubo error
        if file_path and file_path.exists():
            try:
                os.remove(file_path)
                logger.info(f"Archivo limpiado después del error: {file_path}")
            except:
                pass
        
        return jsonify({
            'error': 'Error inesperado durante el análisis',
            'details': str(e)
        }), 500 
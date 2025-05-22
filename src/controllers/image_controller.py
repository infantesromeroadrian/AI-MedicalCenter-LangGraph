"""
Controlador Flask para gestionar el análisis de imágenes médicas.
Proporciona endpoints para la carga y análisis de imágenes.
"""
import os
from pathlib import Path
import uuid
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from werkzeug.utils import secure_filename
from src.services.image_analysis_service import MedicalImageAnalyzer

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
except Exception as e:
    logger.error(f"Error al inicializar el analizador de imágenes: {e}")
    image_analyzer = None

# Extensiones de imagen permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """
    Verifica que el archivo tenga una extensión permitida
    
    Args:
        filename: Nombre del archivo a verificar
        
    Returns:
        bool: True si el archivo tiene una extensión válida
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
def index():
    """Página principal para análisis de imágenes médicas"""
    return render_template('image_analysis.html')

@image_bp.route('/analyze', methods=['GET', 'POST'])
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
def api_analyze():
    """API endpoint para análisis de imágenes (JSON)"""
    if 'image' not in request.files:
        return jsonify({'error': 'No se ha proporcionado ninguna imagen'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No se ha seleccionado ninguna imagen'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Formato de archivo no permitido'}), 400
    
    try:
        # Procesar la imagen como en la ruta normal
        original_filename = secure_filename(file.filename)
        filename = f"{uuid.uuid4().hex}_{original_filename}"
        
        upload_folder = get_upload_folder()
        file_path = upload_folder / filename
        file.save(file_path)
        
        # Obtener datos del formulario
        description = request.form.get('description', '')
        specialty = request.form.get('specialty', 'medicina_general')
        conversation_id = request.form.get('conversation_id', None)
        
        # Analizar la imagen
        analysis_result = image_analyzer.analyze_image(
            file_path,
            patient_context=description,
            specialty=specialty
        )
        
        # URL para la imagen
        image_url = url_for('static', filename=f'uploads/images/{filename}', _external=True)
        
        # Si hay un ID de conversación, intentar agregar el análisis al historial de la conversación
        if conversation_id:
            try:
                from src.services.conversation_service import ConversationService
                conversation_service = ConversationService()
                
                # Obtener la conversación actual
                conversation = conversation_service.get_conversation(conversation_id)
                
                if conversation:
                    # Crear un mensaje de sistema con la información del análisis
                    system_message = f"[Sistema] El paciente ha compartido una imagen médica que ha sido analizada. La imagen está disponible en: {image_url}"
                    
                    # Agregar el mensaje a la conversación como nota de sistema
                    conversation.add_system_note(system_message)
                    
                    # Guardar la conversación actualizada
                    conversation_service.save_conversation(conversation)
                    
                    logger.info(f"Análisis de imagen agregado a la conversación {conversation_id}")
            except Exception as conv_err:
                logger.error(f"Error al agregar el análisis de imagen a la conversación: {str(conv_err)}")
                # No devolvemos error al usuario, solo lo registramos
        
        return jsonify({
            'success': True,
            'image_url': image_url,
            'analysis': analysis_result
        })
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({'error': str(e)}), 500 
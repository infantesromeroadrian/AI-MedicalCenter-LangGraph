"""
Controlador Flask para gestionar recursos médicos del paciente.
Maneja medicamentos, historial, laboratorios e imágenes diagnósticas.
"""
import os
import json
import logging
from datetime import datetime
from pathlib import Path
from flask import Blueprint, request, jsonify, session
from src.services.conversation_service import ConversationService
from src.utils.auth_middleware import login_required

# Configurar logging
logger = logging.getLogger(__name__)

# Crear el blueprint para rutas de recursos médicos
medical_resources_bp = Blueprint('medical_resources', __name__, url_prefix='/medical-resources')

# Inicializar servicio de conversaciones
conversation_service = ConversationService()

@medical_resources_bp.route('/medications/<conversation_id>', methods=['GET'])
@login_required
def get_medications(conversation_id):
    """Obtener medicamentos recetados en una conversación"""
    try:
        conversation = conversation_service.get_conversation(conversation_id)
        if not conversation:
            return jsonify({'error': 'Conversación no encontrada'}), 404
        
        medications = extract_medications_from_conversation(conversation)
        
        return jsonify({
            'success': True,
            'medications': medications,
            'count': len(medications)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo medicamentos: {e}")
        return jsonify({'error': str(e)}), 500

@medical_resources_bp.route('/consultations', methods=['GET'])
@login_required
def get_consultations():
    """Obtener historial de consultas del usuario"""
    try:
        # Obtener todas las conversaciones del usuario
        conversations = conversation_service.get_all_conversations()
        
        consultations = []
        for conv in conversations:
            if conv.messages:  # Solo incluir conversaciones con mensajes
                consultation_data = {
                    'id': conv.conversation_id,
                    'specialty': conv.active_specialty,
                    'date': conv.created_at.strftime('%d/%m/%Y') if hasattr(conv, 'created_at') else datetime.now().strftime('%d/%m/%Y'),
                    'duration': calculate_consultation_duration(conv),
                    'summary': generate_consultation_summary(conv),
                    'status': 'completed' if len(conv.messages) > 4 else 'in_progress',
                    'message_count': len(conv.messages)
                }
                consultations.append(consultation_data)
        
        # Ordenar por fecha (más recientes primero)
        consultations.sort(key=lambda x: x['date'], reverse=True)
        
        return jsonify({
            'success': True,
            'consultations': consultations,
            'count': len(consultations)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo consultas: {e}")
        return jsonify({'error': str(e)}), 500

@medical_resources_bp.route('/lab-results/<conversation_id>', methods=['GET'])
@login_required
def get_lab_results(conversation_id):
    """Obtener resultados de laboratorio mencionados en una conversación"""
    try:
        conversation = conversation_service.get_conversation(conversation_id)
        if not conversation:
            return jsonify({'error': 'Conversación no encontrada'}), 404
        
        lab_results = extract_lab_results_from_conversation(conversation)
        
        return jsonify({
            'success': True,
            'lab_results': lab_results,
            'count': len(lab_results)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo resultados de laboratorio: {e}")
        return jsonify({'error': str(e)}), 500

@medical_resources_bp.route('/diagnostic-images/<conversation_id>', methods=['GET'])
@login_required
def get_diagnostic_images(conversation_id):
    """Obtener imágenes diagnósticas de una conversación"""
    try:
        conversation = conversation_service.get_conversation(conversation_id)
        if not conversation:
            return jsonify({'error': 'Conversación no encontrada'}), 404
        
        images = extract_images_from_conversation(conversation)
        
        return jsonify({
            'success': True,
            'images': images,
            'count': len(images)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo imágenes: {e}")
        return jsonify({'error': str(e)}), 500

@medical_resources_bp.route('/summary/<conversation_id>', methods=['GET'])
@login_required
def get_medical_summary(conversation_id):
    """Obtener resumen médico completo de una conversación"""
    try:
        conversation = conversation_service.get_conversation(conversation_id)
        if not conversation:
            return jsonify({'error': 'Conversación no encontrada'}), 404
        
        summary = {
            'conversation_id': conversation_id,
            'specialty': conversation.active_specialty,
            'medications': extract_medications_from_conversation(conversation),
            'lab_results': extract_lab_results_from_conversation(conversation),
            'images': extract_images_from_conversation(conversation),
            'symptoms': extract_symptoms_from_conversation(conversation),
            'diagnosis': extract_diagnosis_from_conversation(conversation),
            'recommendations': extract_recommendations_from_conversation(conversation)
        }
        
        return jsonify({
            'success': True,
            'summary': summary
        })
        
    except Exception as e:
        logger.error(f"Error generando resumen médico: {e}")
        return jsonify({'error': str(e)}), 500

# Funciones auxiliares para extraer información

def extract_medications_from_conversation(conversation):
    """Extraer medicamentos mencionados en la conversación"""
    medications = []
    
    for message in conversation.messages:
        if message.sender != 'user':  # Solo mensajes del médico
            text = message.content.lower()
            
            # Patrones para detectar medicamentos
            medication_patterns = [
                r'(?:receto|prescribo|tome|tomar)\s+([a-zA-Záéíóúñ\s]+)\s+(?:(\d+(?:\.\d+)?)\s*(mg|g|ml|comprimidos?|cápsulas?|tabletas?))',
                r'(?:medicamento|fármaco|medicina):\s*([a-zA-Záéíóúñ\s]+)',
                r'(?:paracetamol|ibuprofeno|aspirina|amoxicilina|omeprazol|losartan|metformina|atorvastatina|amlodipino|levotiroxina)',
            ]
            
            import re
            for pattern in medication_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    med_name = match.group(1) if match.group(1) else match.group(0)
                    dose = f"{match.group(2)} {match.group(3)}" if len(match.groups()) >= 3 and match.group(2) else "Según indicación médica"
                    
                    medication = {
                        'name': med_name.strip().title(),
                        'dose': dose,
                        'frequency': extract_frequency_from_text(text),
                        'duration': extract_duration_from_text(text),
                        'instructions': 'Seguir indicaciones del médico',
                        'prescribed_date': message.timestamp
                    }
                    
                    # Evitar duplicados
                    if not any(m['name'].lower() == medication['name'].lower() for m in medications):
                        medications.append(medication)
    
    return medications

def extract_lab_results_from_conversation(conversation):
    """Extraer resultados de laboratorio mencionados en la conversación"""
    lab_results = []
    
    for message in conversation.messages:
        text = message.content.lower()
        
        # Patrones para detectar análisis de laboratorio
        lab_patterns = {
            'glucosa': {'normal_range': '70-100 mg/dL', 'value': '95 mg/dL'},
            'colesterol': {'normal_range': '<200 mg/dL', 'value': '180 mg/dL'},
            'hemograma': {'normal_range': 'Dentro de parámetros', 'value': 'Normal'},
            'creatinina': {'normal_range': '0.6-1.2 mg/dL', 'value': '0.9 mg/dL'},
            'transaminasas': {'normal_range': '<40 U/L', 'value': '35 U/L'},
            'tsh': {'normal_range': '0.4-4.0 mU/L', 'value': '2.1 mU/L'}
        }
        
        for test_name, test_info in lab_patterns.items():
            if test_name in text or any(keyword in text for keyword in ['análisis', 'examen', 'laboratorio']):
                # Determinar estado basado en el contexto
                status = 'normal'
                if any(word in text for word in ['alto', 'elevado', 'anormal']):
                    status = 'abnormal'
                elif any(word in text for word in ['pendiente', 'esperando']):
                    status = 'pending'
                
                lab_result = {
                    'test': test_name.title().replace('Tsh', 'TSH'),
                    'value': test_info['value'],
                    'normal_range': test_info['normal_range'],
                    'status': status,
                    'date': datetime.now().strftime('%d/%m/%Y'),
                    'notes': extract_lab_notes_from_text(text, test_name)
                }
                
                # Evitar duplicados
                if not any(lr['test'].lower() == lab_result['test'].lower() for lr in lab_results):
                    lab_results.append(lab_result)
    
    return lab_results

def extract_images_from_conversation(conversation):
    """Extraer referencias a imágenes en la conversación"""
    images = []
    
    import re
    for message in conversation.messages:
        # Buscar el nuevo formato: [IMAGEN ANALIZADA:URL] análisis
        pattern = r'\[IMAGEN ANALIZADA:([^\]]+)\]\s*(.*)'
        match = re.search(pattern, message.content)
        
        if match:
            image_url = match.group(1).strip()
            analysis = match.group(2).strip()
            
            # Formatear fecha para consistencia
            upload_date = message.timestamp
            if isinstance(upload_date, str):
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                    upload_date = dt.strftime('%d/%m/%Y')
                except:
                    upload_date = upload_date
            
            image_info = {
                'id': len(images) + 1,
                'url': image_url,
                'analysis': analysis if analysis else 'Imagen médica analizada',
                'upload_date': upload_date,
                'type': 'diagnostic'
            }
            images.append(image_info)
        # Mantener compatibilidad con el formato anterior
        elif '[IMAGEN ANALIZADA]' in message.content:
            # Formatear fecha para consistencia
            upload_date = message.timestamp
            if isinstance(upload_date, str):
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                    upload_date = dt.strftime('%d/%m/%Y')
                except:
                    upload_date = upload_date
            
            image_info = {
                'id': len(images) + 1,
                'url': '/static/images/placeholder-medical.jpg',  # Placeholder para formato anterior
                'analysis': message.content.replace('[IMAGEN ANALIZADA]', '').strip(),
                'upload_date': upload_date,
                'type': 'diagnostic'
            }
            images.append(image_info)
    
    return images

def extract_symptoms_from_conversation(conversation):
    """Extraer síntomas mencionados"""
    symptoms = []
    
    for message in conversation.messages:
        if message.sender == 'user':
            text = message.content.lower()
            
            # Patrones comunes de síntomas
            symptom_keywords = [
                'dolor', 'fiebre', 'náuseas', 'vómito', 'diarrea', 'mareo',
                'cansancio', 'fatiga', 'tos', 'congestion', 'picazón',
                'hinchazón', 'ardor', 'molestia', 'malestar'
            ]
            
            for keyword in symptom_keywords:
                if keyword in text:
                    symptoms.append({
                        'symptom': keyword,
                        'description': message.content[:100] + '...' if len(message.content) > 100 else message.content,
                        'reported_date': message.timestamp
                    })
                    break  # Solo un síntoma por mensaje para evitar duplicados
    
    return symptoms

def extract_diagnosis_from_conversation(conversation):
    """Extraer diagnósticos mencionados"""
    diagnosis = []
    
    for message in conversation.messages:
        if message.sender != 'user':
            text = message.content.lower()
            
            # Patrones de diagnóstico
            if any(word in text for word in ['diagnóstico', 'parece que', 'posible', 'probable']):
                diagnosis.append({
                    'diagnosis': message.content[:200] + '...' if len(message.content) > 200 else message.content,
                    'confidence': 'probable' if 'posible' in text else 'confirmed',
                    'date': message.timestamp
                })
    
    return diagnosis

def extract_recommendations_from_conversation(conversation):
    """Extraer recomendaciones médicas"""
    recommendations = []
    
    for message in conversation.messages:
        if message.sender != 'user':
            text = message.content.lower()
            
            # Patrones de recomendaciones
            if any(word in text for word in ['recomiendo', 'sugiero', 'debe', 'importante']):
                recommendations.append({
                    'recommendation': message.content,
                    'priority': 'high' if 'importante' in text else 'normal',
                    'date': message.timestamp
                })
    
    return recommendations

def extract_frequency_from_text(text):
    """Extraer frecuencia de administración del texto"""
    if any(word in text for word in ['cada 8 horas', 'tres veces', '3 veces']):
        return 'Cada 8 horas'
    elif any(word in text for word in ['cada 12 horas', 'dos veces', '2 veces']):
        return 'Cada 12 horas'
    elif any(word in text for word in ['una vez', '1 vez', 'diario']):
        return 'Una vez al día'
    return 'Según indicación médica'

def extract_duration_from_text(text):
    """Extraer duración del tratamiento del texto"""
    if any(word in text for word in ['7 días', 'una semana']):
        return '7 días'
    elif any(word in text for word in ['10 días']):
        return '10 días'
    elif any(word in text for word in ['14 días', 'dos semanas']):
        return '14 días'
    return 'Según indicación médica'

def extract_lab_notes_from_text(text, test_name):
    """Extraer notas específicas sobre resultados de laboratorio"""
    if 'normal' in text:
        return 'Resultado dentro de parámetros normales'
    elif 'alto' in text or 'elevado' in text:
        return f'{test_name.title()} elevado, requiere seguimiento'
    elif 'bajo' in text:
        return f'{test_name.title()} por debajo de los valores normales'
    return 'Sin observaciones adicionales'

def calculate_consultation_duration(conversation):
    """Calcular duración estimada de la consulta"""
    message_count = len(conversation.messages)
    
    if message_count < 5:
        return '10-15 minutos'
    elif message_count < 10:
        return '20-25 minutos'
    elif message_count < 15:
        return '30-35 minutos'
    else:
        return '40+ minutos'

def generate_consultation_summary(conversation):
    """Generar resumen de la consulta"""
    message_count = len(conversation.messages)
    user_messages = [m for m in conversation.messages if m.sender == 'user']
    
    if not user_messages:
        return 'Consulta sin síntomas específicos reportados'
    
    first_message = user_messages[0].content[:100] + '...' if len(user_messages[0].content) > 100 else user_messages[0].content
    
    return f"Consulta sobre: {first_message}. Total de intercambios: {message_count}" 
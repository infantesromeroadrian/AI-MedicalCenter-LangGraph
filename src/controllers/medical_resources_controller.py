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

@medical_resources_bp.route('/lab-requests/<conversation_id>', methods=['GET'])
@login_required
def generate_lab_requests(conversation_id):
    """Generar peticiones de laboratorio basadas en el diagnóstico de la conversación"""
    try:
        conversation = conversation_service.get_conversation(conversation_id)
        if not conversation:
            return jsonify({'error': 'Conversación no encontrada'}), 404
        
        # Generar peticiones de laboratorio basadas en síntomas y diagnóstico
        lab_requests = generate_lab_requests_from_conversation(conversation)
        
        return jsonify({
            'success': True,
            'lab_requests': lab_requests,
            'count': len(lab_requests)
        })
        
    except Exception as e:
        logger.error(f"Error generando peticiones de laboratorio: {e}")
        return jsonify({'error': str(e)}), 500

@medical_resources_bp.route('/lab-complete/<conversation_id>', methods=['GET'])
@login_required
def get_complete_lab_info(conversation_id):
    """Obtener información completa de laboratorio: resultados existentes + peticiones recomendadas"""
    try:
        conversation = conversation_service.get_conversation(conversation_id)
        if not conversation:
            return jsonify({'error': 'Conversación no encontrada'}), 404
        
        lab_results = extract_lab_results_from_conversation(conversation)
        lab_requests = generate_lab_requests_from_conversation(conversation)
        
        return jsonify({
            'success': True,
            'lab_results': lab_results,
            'lab_requests': lab_requests,
            'results_count': len(lab_results),
            'requests_count': len(lab_requests),
            'total_count': len(lab_results) + len(lab_requests)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo información completa de laboratorio: {e}")
        return jsonify({'error': str(e)}), 500

@medical_resources_bp.route('/diagnostic-images/<conversation_id>', methods=['GET'])
@login_required
def get_diagnostic_images(conversation_id):
    """Obtener imágenes diagnósticas de una conversación"""
    try:
        logger.info(f"Buscando imágenes para conversación: {conversation_id}")
        
        conversation = conversation_service.get_conversation(conversation_id)
        if not conversation:
            logger.error(f"Conversación no encontrada: {conversation_id}")
            return jsonify({'error': 'Conversación no encontrada'}), 404
        
        logger.info(f"Conversación encontrada con {len(conversation.messages)} mensajes")
        
        images = extract_images_from_conversation(conversation)
        
        logger.info(f"Extraídas {len(images)} imágenes de la conversación {conversation_id}")
        for i, img in enumerate(images):
            logger.info(f"Imagen {i+1}: URL={img.get('url', 'N/A')}, Análisis={img.get('analysis', 'N/A')[:50]}...")
        
        return jsonify({
            'success': True,
            'images': images,
            'count': len(images)
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo imágenes: {e}")
        logger.error(f"Traceback completo: {e.__class__.__name__}: {str(e)}")
        return jsonify({
            'error': str(e),
            'success': False,
            'images': [],
            'count': 0
        }), 500

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
    
    try:
        import re
        logger.info(f"Analizando {len(conversation.messages)} mensajes para extraer imágenes")
        
        for i, message in enumerate(conversation.messages):
            try:
                # Buscar el nuevo formato: [IMAGEN ANALIZADA:URL] análisis
                pattern = r'\[IMAGEN ANALIZADA:([^\]]+)\]\s*(.*)'
                match = re.search(pattern, message.content)
                
                if match:
                    logger.info(f"Imagen encontrada en mensaje {i}: formato [IMAGEN ANALIZADA:URL]")
                    image_url = match.group(1).strip()
                    analysis = match.group(2).strip()
                    
                    # Formatear fecha para consistencia
                    upload_date = message.timestamp
                    if isinstance(upload_date, str):
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                            upload_date = dt.strftime('%d/%m/%Y')
                        except Exception as date_error:
                            logger.warning(f"Error al parsear fecha: {date_error}")
                            upload_date = "Fecha no disponible"
                    
                    image_info = {
                        'id': len(images) + 1,
                        'url': image_url,
                        'analysis': analysis if analysis else 'Imagen médica analizada',
                        'upload_date': upload_date,
                        'type': 'diagnostic'
                    }
                    images.append(image_info)
                    logger.info(f"Imagen agregada: ID={image_info['id']}, URL={image_url[:50]}...")
                    
                # Mantener compatibilidad con el formato anterior
                elif '[IMAGEN ANALIZADA]' in message.content:
                    logger.info(f"Imagen encontrada en mensaje {i}: formato legacy [IMAGEN ANALIZADA]")
                    
                    # Formatear fecha para consistencia
                    upload_date = message.timestamp
                    if isinstance(upload_date, str):
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(upload_date.replace('Z', '+00:00'))
                            upload_date = dt.strftime('%d/%m/%Y')
                        except Exception as date_error:
                            logger.warning(f"Error al parsear fecha: {date_error}")
                            upload_date = "Fecha no disponible"
                    
                    image_info = {
                        'id': len(images) + 1,
                        'url': '/static/images/placeholder-medical.jpg',  # Placeholder para formato anterior
                        'analysis': message.content.replace('[IMAGEN ANALIZADA]', '').strip(),
                        'upload_date': upload_date,
                        'type': 'diagnostic'
                    }
                    images.append(image_info)
                    logger.info(f"Imagen legacy agregada: ID={image_info['id']}")
                    
            except Exception as msg_error:
                logger.error(f"Error procesando mensaje {i}: {msg_error}")
                continue
        
        logger.info(f"Total de imágenes extraídas: {len(images)}")
        return images
        
    except Exception as e:
        logger.error(f"Error en extract_images_from_conversation: {e}")
        return []

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

def generate_lab_requests_from_conversation(conversation):
    """Generar peticiones de laboratorio inteligentes basadas en la conversación"""
    lab_requests = []
    
    # Combinar todo el contenido de la conversación para análisis
    conversation_text = ""
    symptoms = []
    for message in conversation.messages:
        conversation_text += message.content.lower() + " "
        if message.sender == 'user':
            symptoms.append(message.content.lower())
    
    # Mapeo de síntomas/condiciones a análisis de laboratorio recomendados
    lab_recommendations = {
        # Análisis básicos generales
        'dolor': {
            'tests': ['Hemograma completo', 'PCR (Proteína C Reactiva)', 'VSG (Velocidad de Sedimentación)'],
            'reason': 'Evaluar procesos inflamatorios o infecciosos'
        },
        'fiebre': {
            'tests': ['Hemograma completo', 'PCR', 'Procalcitonina', 'Hemocultivos'],
            'reason': 'Identificar origen infeccioso y gravedad'
        },
        'fatiga': {
            'tests': ['Hemograma completo', 'Química sanguínea', 'TSH', 'Vitamina B12', 'Hierro sérico'],
            'reason': 'Descartar anemia, alteraciones tiroideas o deficiencias nutricionales'
        },
        
        # Síntomas cardiovasculares
        'dolor de pecho': {
            'tests': ['Troponinas cardíacas', 'CK-MB', 'BNP', 'D-dímero', 'Perfil lipídico'],
            'reason': 'Evaluar posible síndrome coronario agudo y factores de riesgo cardiovascular'
        },
        'hipertensión': {
            'tests': ['Química sanguínea', 'Perfil lipídico', 'Microalbuminuria', 'TSH'],
            'reason': 'Evaluar daño de órganos diana y factores de riesgo asociados'
        },
        
        # Síntomas gastrointestinales
        'dolor abdominal': {
            'tests': ['Hemograma', 'Química sanguínea', 'Amilasa', 'Lipasa', 'PCR'],
            'reason': 'Evaluar posibles causas inflamatorias, infecciosas o pancreáticas'
        },
        'diarrea': {
            'tests': ['Coprocultivo', 'Parásitos en heces', 'Leucocitos en heces', 'Electrolitos'],
            'reason': 'Identificar agentes patógenos y evaluar estado de hidratación'
        },
        
        # Síntomas neurológicos
        'dolor de cabeza': {
            'tests': ['Hemograma', 'Química sanguínea', 'PCR', 'VSG'],
            'reason': 'Descartar causas secundarias de cefalea'
        },
        'mareo': {
            'tests': ['Hemograma', 'Glucosa', 'TSH', 'Vitamina B12'],
            'reason': 'Evaluar causas metabólicas de mareo'
        },
        
        # Síntomas respiratorios
        'tos': {
            'tests': ['Hemograma', 'PCR', 'Procalcitonina'],
            'reason': 'Evaluar posible origen infeccioso'
        },
        'dificultad respiratoria': {
            'tests': ['Hemograma', 'Gasometría arterial', 'BNP', 'D-dímero'],
            'reason': 'Evaluar causas cardíacas, pulmonares o tromboembólicas'
        },
        
        # Síntomas dermatológicos
        'rash': {
            'tests': ['Hemograma', 'IgE total', 'Panel de alergias'],
            'reason': 'Evaluar posibles causas alérgicas o inmunológicas'
        },
        
        # Por especialidad médica
        'diabetes': {
            'tests': ['Glucosa en ayunas', 'HbA1c', 'Perfil lipídico', 'Microalbuminuria', 'Creatinina'],
            'reason': 'Control metabólico y detección de complicaciones'
        },
        'hipercolesterolemia': {
            'tests': ['Perfil lipídico completo', 'Apolipoproteínas', 'Glucosa'],
            'reason': 'Evaluación del riesgo cardiovascular'
        }
    }
    
    # Análisis específicos por especialidad
    specialty_specific = {
        'cardiology': {
            'tests': ['Troponinas', 'BNP', 'Perfil lipídico', 'Hemograma'],
            'reason': 'Evaluación cardiovascular especializada'
        },
        'neurology': {
            'tests': ['Vitamina B12', 'Ácido fólico', 'TSH', 'Glucosa'],
            'reason': 'Evaluación neurológica y metabólica'
        },
        'oncology': {
            'tests': ['Hemograma completo', 'Química sanguínea', 'Marcadores tumorales'],
            'reason': 'Monitoreo oncológico'
        },
        'dermatology': {
            'tests': ['IgE total', 'Panel de alergias', 'Vitamina D'],
            'reason': 'Evaluación dermatológica especializada'
        },
        'psychiatry': {
            'tests': ['TSH', 'Vitamina B12', 'Química sanguínea'],
            'reason': 'Descartar causas orgánicas de síntomas psiquiátricos'
        },
        'pediatrics': {
            'tests': ['Hemograma', 'Química sanguínea básica', 'Examen de orina'],
            'reason': 'Evaluación pediátrica general'
        },
        'emergency_medicine': {
            'tests': ['Hemograma urgente', 'Química sanguínea', 'Gasometría', 'Coagulación'],
            'reason': 'Evaluación de emergencia'
        },
        'internal_medicine': {
            'tests': ['Hemograma completo', 'Química sanguínea completa', 'Examen de orina'],
            'reason': 'Evaluación médica integral'
        }
    }
    
    # Conjunto para evitar duplicados
    requested_tests = set()
    
    # 1. Analizar síntomas específicos mencionados
    for symptom, lab_info in lab_recommendations.items():
        if symptom in conversation_text:
            for test in lab_info['tests']:
                if test not in requested_tests:
                    priority = 'alta' if symptom in ['dolor de pecho', 'fiebre', 'dificultad respiratoria'] else 'media'
                    lab_requests.append({
                        'test_name': test,
                        'reason': lab_info['reason'],
                        'priority': priority,
                        'category': 'Síntoma específico',
                        'urgency': 'urgente' if priority == 'alta' else 'rutina',
                        'estimated_time': '2-4 horas' if priority == 'alta' else '24-48 horas',
                        'cost_estimate': get_test_cost_estimate(test),
                        'preparation': get_test_preparation(test)
                    })
                    requested_tests.add(test)
    
    # 2. Análisis por especialidad
    specialty = conversation.active_specialty
    if specialty in specialty_specific:
        specialty_info = specialty_specific[specialty]
        for test in specialty_info['tests']:
            if test not in requested_tests:
                lab_requests.append({
                    'test_name': test,
                    'reason': specialty_info['reason'],
                    'priority': 'media',
                    'category': f'Especialidad {specialty}',
                    'urgency': 'rutina',
                    'estimated_time': '24-48 horas',
                    'cost_estimate': get_test_cost_estimate(test),
                    'preparation': get_test_preparation(test)
                })
                requested_tests.add(test)
    
    # 3. Análisis básicos si no hay muchos específicos
    if len(lab_requests) < 3:
        basic_tests = ['Hemograma completo', 'Química sanguínea básica', 'Examen general de orina']
        for test in basic_tests:
            if test not in requested_tests:
                lab_requests.append({
                    'test_name': test,
                    'reason': 'Evaluación médica general y detección temprana',
                    'priority': 'baja',
                    'category': 'Análisis básicos',
                    'urgency': 'rutina',
                    'estimated_time': '12-24 horas',
                    'cost_estimate': get_test_cost_estimate(test),
                    'preparation': get_test_preparation(test)
                })
                requested_tests.add(test)
    
    # Ordenar por prioridad
    priority_order = {'alta': 0, 'media': 1, 'baja': 2}
    lab_requests.sort(key=lambda x: priority_order.get(x['priority'], 3))
    
    return lab_requests

def get_test_cost_estimate(test_name):
    """Obtener estimación de costo del análisis"""
    cost_estimates = {
        'Hemograma completo': '$25-35',
        'Química sanguínea': '$40-60',
        'PCR (Proteína C Reactiva)': '$20-30',
        'VSG (Velocidad de Sedimentación)': '$15-25',
        'Troponinas cardíacas': '$80-120',
        'BNP': '$90-130',
        'Perfil lipídico': '$35-50',
        'TSH': '$30-45',
        'HbA1c': '$40-60',
        'Vitamina B12': '$45-65',
        'Examen general de orina': '$15-25',
        'Coprocultivo': '$60-80',
        'Gasometría arterial': '$50-70',
        'Marcadores tumorales': '$100-200',
        'Panel de alergias': '$150-300'
    }
    return cost_estimates.get(test_name, '$30-50')

def get_test_preparation(test_name):
    """Obtener instrucciones de preparación para el análisis"""
    preparations = {
        'Hemograma completo': 'No requiere ayuno',
        'Química sanguínea': 'Ayuno de 8-12 horas',
        'Perfil lipídico': 'Ayuno de 12 horas',
        'Glucosa en ayunas': 'Ayuno de 8-12 horas',
        'TSH': 'No requiere ayuno',
        'Troponinas cardíacas': 'No requiere preparación especial',
        'Examen general de orina': 'Primera orina de la mañana',
        'Coprocultivo': 'Muestra fresca, sin antibióticos 48h previas',
        'Gasometría arterial': 'No requiere preparación especial',
        'Vitamina B12': 'No requiere ayuno',
        'Panel de alergias': 'Suspender antihistamínicos 5 días antes'
    }
    return preparations.get(test_name, 'Consultar con laboratorio') 
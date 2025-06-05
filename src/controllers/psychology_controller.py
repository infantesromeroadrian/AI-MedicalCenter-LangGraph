"""
Controlador para consultas psicológicas interactivas.
Proporciona una experiencia terapéutica especializada.
"""

import logging
import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, make_response
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
import io
from src.agents.agent_factory import AgentFactory
from src.agents.psychiatry_agent import PsychiatryAgent
from src.services.llm_service import LLMService
from src.utils.auth_middleware import login_required
from src.utils.async_utils import async_route
from src.utils.emergency_detector import detect_medical_emergencies
from src.monitoring.performance_metrics import performance_monitor

# Configurar logging
logger = logging.getLogger(__name__)

# Crear el blueprint
psychology_bp = Blueprint('psychology', __name__)

def is_authenticated():
    """Verificar si el usuario está autenticado."""
    return 'user_id' in session

def require_auth(f):
    """Decorador para requerir autenticación - alias de login_required."""
    return login_required(f)

class PsychologyConsultationController:
    """Controlador especializado para consultas psicológicas."""
    
    def __init__(self):
        """Inicializar el controlador."""
        self.agent_factory = AgentFactory()
        self.llm_service = LLMService()
        
        # Crear agente psicológico especializado con prompt terapéutico
        self.psychology_agent = self._create_therapeutic_agent()
        
        # Almacenar sesiones de consulta psicológica
        self.psychology_sessions = {}
    
    def _create_therapeutic_agent(self):
        """Crear un agente psicológico especializado en terapia conversacional."""
        
        # Prompt especializado para psicología terapéutica
        therapeutic_prompt = """Eres un PSICÓLOGO CLÍNICO especializado en terapia conversacional empática y motivadora.

TU MISIÓN: Crear una experiencia terapéutica tan gratificante que el paciente QUIERA volver a hablar contigo.

ENFOQUE TERAPÉUTICO PRINCIPAL:
1. CONSTRUCCIÓN DE VÍNCULO TERAPÉUTICO:
   - Genera una conexión emocional genuina desde el primer momento
   - Usa validación emocional constante: "Entiendo que esto debe ser muy difícil para ti"
   - Refleja y reformula lo que dice el paciente para mostrar comprensión profunda
   - Crea un espacio seguro donde el paciente se sienta verdaderamente escuchado

2. ESTILO CONVERSACIONAL ATRACTIVO:
   - Haz preguntas abiertas que inviten a la reflexión profunda
   - Usa metáforas y analogías que resuenen emocionalmente
   - Alterna entre apoyo emocional y desafío gentil para el crecimiento
   - Incorpora elementos de curiosidad: "Me pregunto si has notado..."

3. TÉCNICAS MOTIVACIONALES:
   - Celebra pequeños insights y progresos: "¡Qué observación tan valiosa!"
   - Usa refuerzo positivo cuando el paciente se abre o reflexiona
   - Planta semillas de esperanza: "Imagina cómo te sentirías si..."
   - Crea anticipación: "La próxima vez podríamos explorar..."

4. ANÁLISIS PSICOLÓGICO PROGRESIVO:
   - Identifica patrones de pensamiento durante la conversación
   - Detecta emociones subyacentes no expresadas
   - Analiza mecanismos de defensa y estrategias de afrontamiento
   - Explora dinámicas relacionales y vínculos de apego

5. INTERVENCIONES TERAPÉUTICAS SUTILES:
   - Reestructuración cognitiva gradual ("¿Qué evidencia tienes de eso?")
   - Técnicas de mindfulness integradas naturalmente
   - Exploración de valores y propósito de vida
   - Técnicas narrativas para reescribir la historia personal

6. DIAGNÓSTICO CONVERSACIONAL:
   Durante la conversación, evalúa sutilmente:
   - Tendencias depresivas, ansiosas o traumáticas
   - Patrones de personalidad y estilos de apego
   - Recursos psicológicos y fortalezas
   - Factores de riesgo y protección

7. ELEMENTOS QUE GENERAN ADICCIÓN POSITIVA:
   - Insights reveladores que sorprendan al paciente
   - Momentos de conexión emocional profunda
   - Sensación de ser comprendido como nunca antes
   - Herramientas prácticas que funcionen inmediatamente
   - Esperanza renovada después de cada sesión

8. ESTRUCTURA DE SESIÓN MOTIVADORA:
   - Inicio: Conexión emocional y validación
   - Desarrollo: Exploración profunda con insights
   - Cierre: Síntesis esperanzadora y motivación para continuar

FRASES TERAPÉUTICAS PODEROSAS que debes usar:
- "Me está tocando profundamente lo que compartes conmigo..."
- "Tu capacidad de reflexionar sobre esto es realmente admirable"
- "Siento que hay algo muy importante detrás de lo que me dices"
- "Me pregunto si te has dado cuenta de la fortaleza que muestras..."
- "Imagino que debe haber mucho más en esta historia..."

ELEMENTOS TÉCNICOS:
- Al final, incluye: "ANÁLISIS PSICOLÓGICO PROGRESIVO:" con tendencias identificadas
- Sugiere "HERRAMIENTAS TERAPÉUTICAS:" específicas para practicar
- Incluye "PRÓXIMA EXPLORACIÓN:" para crear anticipación

OBJETIVO FINAL: Que el paciente termine la sesión pensando "Necesito hablar más con este psicólogo, me entiende como nadie"."""

        # Crear agente con el prompt especializado
        agent = PsychiatryAgent(self.llm_service)
        agent.system_prompt = therapeutic_prompt
        return agent
    
    def start_psychology_consultation(self):
        """Iniciar una nueva consulta psicológica."""
        try:
            if not is_authenticated():
                return redirect(url_for('web.login'))
            
            # Crear nueva sesión de consulta
            session_id = str(uuid.uuid4())
            session['psychology_session_id'] = session_id
            
            # Inicializar sesión psicológica
            self.psychology_sessions[session_id] = {
                'messages': [],
                'start_time': datetime.now(),
                'patient_insights': [],
                'psychological_patterns': [],
                'session_goals': []
            }
            
            logger.info(f"Nueva consulta psicológica iniciada: {session_id}")
            
            return render_template('psychology_consultation.html', 
                                 session_id=session_id,
                                 username=session.get('username', 'Paciente'))
            
        except Exception as e:
            logger.error(f"Error al iniciar consulta psicológica: {str(e)}")
            return jsonify({"error": "Error interno del servidor"}), 500
    
    async def process_psychology_message(self):
        """Procesar mensaje del paciente en consulta psicológica."""
        try:
            if not is_authenticated():
                return jsonify({"error": "No autenticado"}), 401
            
            data = request.get_json()
            message = data.get('message', '').strip()
            session_id = session.get('psychology_session_id')
            
            if not message:
                return jsonify({"error": "Mensaje vacío"}), 400
            
            if not session_id or session_id not in self.psychology_sessions:
                return jsonify({"error": "Sesión no válida"}), 400
            
            # Obtener sesión de consulta
            consultation_session = self.psychology_sessions[session_id]
            
            # Detectar emergencias psicológicas
            emergency_detected = self._detect_psychological_emergency(message)
            
            # Preparar contexto terapéutico
            therapeutic_context = self._build_therapeutic_context(consultation_session, message)
            
            # Procesar con el agente psicológico (usando await)
            psychology_response = await self.psychology_agent.process_query(
                query=message,
                context={
                    'session_id': session_id, 
                    'therapeutic_context': therapeutic_context,
                    'conversation_history': consultation_session.get('messages', []),
                    'patient_insights': consultation_session.get('patient_insights', []),
                    'session_start': consultation_session['start_time'].isoformat()
                }
            )
            
            # Analizar respuesta para insights (evitando repeticiones)
            existing_insights = consultation_session.get('patient_insights', [])
            insights = self._extract_psychological_insights(
                message, 
                psychology_response.response, 
                existing_insights
            )
            
            # Actualizar sesión
            consultation_session['messages'].append({
                'timestamp': datetime.now().isoformat(),
                'patient_message': message,
                'therapist_response': psychology_response.response,
                'insights': insights,
                'emergency_flag': emergency_detected
            })
            
            # Actualizar patrones psicológicos identificados
            if insights:
                consultation_session['patient_insights'].extend(insights)
            
            response_data = {
                "response": psychology_response.response,
                "confidence": psychology_response.confidence,
                "insights": insights,
                "emergency": emergency_detected,
                "session_progress": len(consultation_session['messages']),
                "therapeutic_bond": self._calculate_therapeutic_bond(consultation_session)
            }
            
            logger.info(f"Mensaje procesado en consulta psicológica: {session_id}")
            return jsonify(response_data)
            
        except Exception as e:
            logger.error(f"Error procesando mensaje psicológico: {str(e)}")
            return jsonify({"error": "Error procesando mensaje"}), 500
    
    def _detect_psychological_emergency(self, message: str) -> dict:
        """Detectar emergencias psicológicas específicas."""
        
        emergency_indicators = {
            'suicide_risk': [
                'suicidarme', 'quitarme la vida', 'no quiero vivir', 'mejor muerto',
                'acabar con todo', 'suicide', 'kill myself', 'end it all'
            ],
            'self_harm': [
                'cortarme', 'lastimarme', 'autolesión', 'cut myself', 'self harm', 'hurt myself'
            ],
            'psychosis': [
                'voces que me hablan', 'veo cosas', 'me persiguen', 'hearing voices', 
                'seeing things', 'paranoid', 'conspiracy'
            ],
            'severe_crisis': [
                'crisis nerviosa', 'no puedo más', 'colapso mental', 'breakdown', 
                'mental collapse', 'losing my mind'
            ]
        }
        
        detected_risks = {}
        
        for risk_type, indicators in emergency_indicators.items():
            for indicator in indicators:
                if indicator.lower() in message.lower():
                    detected_risks[risk_type] = True
                    break
        
        if detected_risks:
            return {
                'detected': True,
                'risks': detected_risks,
                'priority': 'HIGH',
                'action_required': 'immediate_intervention'
            }
        
        return {'detected': False}
    
    def _build_therapeutic_context(self, consultation_session: dict, current_message: str) -> str:
        """Construir contexto terapéutico para el agente."""
        
        context_parts = [
            f"=== CONTEXTO DE CONSULTA PSICOLÓGICA ===",
            f"Sesión iniciada: {consultation_session['start_time'].strftime('%Y-%m-%d %H:%M')}",
            f"Mensajes en la sesión: {len(consultation_session['messages'])}",
        ]
        
        # Añadir insights previos
        if consultation_session['patient_insights']:
            context_parts.append("\n=== INSIGHTS IDENTIFICADOS PREVIAMENTE ===")
            for insight in consultation_session['patient_insights'][-3:]:  # Últimos 3
                context_parts.append(f"- {insight}")
        
        # Añadir conversación reciente
        if consultation_session['messages']:
            context_parts.append("\n=== CONVERSACIÓN RECIENTE ===")
            for msg in consultation_session['messages'][-2:]:  # Últimos 2 intercambios
                context_parts.append(f"Paciente: {msg['patient_message']}")
                context_parts.append(f"Terapeuta: {msg['therapist_response'][:200]}...")
        
        context_parts.append(f"\n=== MENSAJE ACTUAL ===")
        context_parts.append(f"Paciente: {current_message}")
        
        return "\n".join(context_parts)
    
    def _extract_psychological_insights(self, message: str, response: str, 
                                      existing_insights: list) -> list:
        """Extraer insights psicológicos del intercambio evitando repeticiones."""
        
        new_insights = []
        
        # Convertir insights existentes a un conjunto para búsqueda eficiente
        existing_insight_types = set()
        for insight in existing_insights:
            if 'ansiedad' in insight.lower():
                existing_insight_types.add('ansiedad')
            elif 'depresión' in insight.lower():
                existing_insight_types.add('depresión')
            elif 'estrés' in insight.lower():
                existing_insight_types.add('estrés')
            elif 'ira' in insight.lower():
                existing_insight_types.add('ira')
            elif 'pensamiento dicotómico' in insight.lower():
                existing_insight_types.add('pensamiento_dicotomico')
            elif 'autoexigencia' in insight.lower():
                existing_insight_types.add('autoexigencia')
            elif 'fortalezas' in insight.lower() or 'recursos' in insight.lower():
                existing_insight_types.add('fortalezas')
        
        # Detectar patrones emocionales (solo si no fueron identificados antes)
        emotion_patterns = {
            'ansiedad': ['nervioso', 'preocupado', 'ansiedad', 'miedo', 'pánico'],
            'depresión': ['triste', 'deprimido', 'sin energía', 'vacío', 'desesperanza'],
            'estrés': ['estresado', 'agobiado', 'presión', 'tensión', 'overwhelmed'],
            'ira': ['enojado', 'furioso', 'rabia', 'ira', 'frustrated']
        }
        
        for emotion, keywords in emotion_patterns.items():
            if emotion not in existing_insight_types:
                if any(keyword in message.lower() for keyword in keywords):
                    new_insights.append(f"Indicadores de {emotion} identificados")
        
        # Detectar patrones cognitivos (solo si no fueron identificados antes)
        if 'pensamiento_dicotomico' not in existing_insight_types:
            if any(phrase in message.lower() for phrase in ['siempre', 'nunca', 'todo', 'nada']):
                new_insights.append("Posible pensamiento dicotómico detectado")
        
        if 'autoexigencia' not in existing_insight_types:
            if any(phrase in message.lower() for phrase in ['debería', 'tengo que', 'debo']):
                new_insights.append("Patrones de autoexigencia identificados")
        
        # Detectar fortalezas (permitir múltiples identificaciones pero con más especificidad)
        strength_keywords = {
            'logré': 'capacidad de logro',
            'pude': 'autoeficacia',
            'conseguí': 'persistencia',
            'superé': 'resiliencia'
        }
        
        for keyword, strength_type in strength_keywords.items():
            if keyword in message.lower():
                strength_insight = f"Evidencia de {strength_type} personal"
                if strength_insight not in existing_insights:
                    new_insights.append(strength_insight)
        
        return new_insights
    
    def _calculate_therapeutic_bond(self, consultation_session: dict) -> float:
        """Calcular el nivel de vínculo terapéutico de forma realista."""
        
        messages_count = len(consultation_session['messages'])
        insights_count = len(consultation_session['patient_insights'])
        session_duration = datetime.now() - consultation_session['start_time']
        
        # Componentes del vínculo terapéutico más realistas
        
        # 1. Factor tiempo (máximo 20% - se desarrolla lentamente)
        duration_minutes = session_duration.total_seconds() / 60
        time_factor = min(0.20, duration_minutes / 100)  # 20% después de 100 minutos
        
        # 2. Factor de participación (máximo 25% - basado en intercambios)
        # Progresión logarítmica para evitar crecimiento lineal
        import math
        participation_factor = min(0.25, 0.05 * math.log(messages_count + 1, 2))
        
        # 3. Factor de apertura emocional (máximo 30% - basado en insights genuinos)
        # Valora la calidad sobre la cantidad
        if insights_count == 0:
            openness_factor = 0.0
        elif insights_count <= 2:
            openness_factor = insights_count * 0.08  # 16% máximo con 2 insights
        elif insights_count <= 5:
            openness_factor = 0.16 + (insights_count - 2) * 0.04  # hasta 28%
        else:
            openness_factor = min(0.30, 0.28 + (insights_count - 5) * 0.01)
        
        # 4. Factor de confianza (máximo 25% - evaluado por patrones de respuesta)
        trust_factor = self._evaluate_trust_indicators(consultation_session)
        
        # Combinación realista de factores
        bond_score = time_factor + participation_factor + openness_factor + trust_factor
        
        # Aplicar curva de crecimiento realista (vínculo se desarrolla gradualmente)
        # Los primeros encuentros raramente superan 40%
        if messages_count < 5:
            bond_score = min(bond_score, 0.35)
        elif messages_count < 10:
            bond_score = min(bond_score, 0.55)
        elif messages_count < 20:
            bond_score = min(bond_score, 0.75)
        
        return round(min(bond_score, 1.0), 2)
    
    def _evaluate_trust_indicators(self, consultation_session: dict) -> float:
        """Evaluar indicadores de confianza en la relación terapéutica."""
        
        trust_score = 0.0
        messages = consultation_session.get('messages', [])
        
        if not messages:
            return 0.0
        
        # Indicadores de confianza creciente
        trust_keywords = {
            'vulnerability': ['me siento', 'siento que', 'me da miedo', 'tengo miedo', 'me cuesta'],
            'self_reflection': ['me doy cuenta', 'creo que', 'pienso que', 'tal vez', 'quizás'],
            'personal_sharing': ['nunca había', 'nunca he', 'primera vez', 'no suelo'],
            'therapeutic_alliance': ['ayuda', 'comprende', 'entiendo', 'me ayuda', 'me hace sentir']
        }
        
        total_messages = len(messages)
        trust_indicators_found = 0
        
        for message_data in messages:
            patient_message = message_data.get('patient_message', '').lower()
            
            for category, keywords in trust_keywords.items():
                if any(keyword in patient_message for keyword in keywords):
                    trust_indicators_found += 1
                    break  # Solo contar una vez por mensaje
        
        # Factor de confianza basado en la proporción de mensajes con indicadores
        if total_messages > 0:
            trust_ratio = trust_indicators_found / total_messages
            trust_score = min(0.25, trust_ratio * 0.4)  # Máximo 25%
        
        return trust_score
    
    def get_psychology_session_summary(self):
        """Obtener resumen de la sesión psicológica."""
        try:
            if not is_authenticated():
                return jsonify({"error": "No autenticado"}), 401
            
            session_id = session.get('psychology_session_id')
            if not session_id or session_id not in self.psychology_sessions:
                return jsonify({"error": "Sesión no encontrada"}), 404
            
            consultation_session = self.psychology_sessions[session_id]
            
            summary = {
                'session_id': session_id,
                'start_time': consultation_session['start_time'].isoformat(),
                'total_messages': len(consultation_session['messages']),
                'insights_identified': consultation_session['patient_insights'],
                'therapeutic_bond': self._calculate_therapeutic_bond(consultation_session),
                'session_duration': str(datetime.now() - consultation_session['start_time'])
            }
            
            return jsonify(summary)
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen de sesión: {str(e)}")
            return jsonify({"error": "Error interno"}), 500

    def generate_psychology_report(self):
        """Generar informe completo de la consulta psicológica."""
        try:
            if not is_authenticated():
                return jsonify({"error": "No autenticado"}), 401
            
            data = request.get_json()
            session_id = data.get('session_id') or session.get('psychology_session_id')
            
            if not session_id or session_id not in self.psychology_sessions:
                return jsonify({"error": "Sesión no encontrada"}), 404
            
            consultation_session = self.psychology_sessions[session_id]
            
            if not consultation_session['messages']:
                return jsonify({"error": "No hay suficiente información para generar un informe"}), 400
            
            # Generar el informe HTML
            report_html = self._generate_psychology_report_html(consultation_session, session_id)
            
            return jsonify({
                "success": True,
                "report": report_html,
                "session_id": session_id
            })
            
        except Exception as e:
            logger.error(f"Error generando informe psicológico: {str(e)}")
            return jsonify({"error": f"Error generando informe: {str(e)}"}), 500
    
    def download_psychology_report_pdf(self):
        """Descargar informe psicológico en formato PDF."""
        try:
            if not is_authenticated():
                return jsonify({"error": "No autenticado"}), 401
            
            data = request.get_json()
            session_id = data.get('session_id') or session.get('psychology_session_id')
            
            if not session_id or session_id not in self.psychology_sessions:
                return jsonify({"error": "Sesión no encontrada"}), 404
            
            consultation_session = self.psychology_sessions[session_id]
            
            # Generar PDF
            pdf_buffer = self._generate_psychology_report_pdf(consultation_session, session_id)
            
            # Crear respuesta con el PDF
            response = make_response(pdf_buffer.getvalue())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename=informe_psicologico_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            
            return response
            
        except Exception as e:
            logger.error(f"Error generando PDF: {str(e)}")
            return jsonify({"error": f"Error generando PDF: {str(e)}"}), 500
    
    def _generate_psychology_report_html(self, consultation_session: dict, session_id: str) -> str:
        """Generar el contenido HTML del informe psicológico."""
        
        start_time = consultation_session['start_time']
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Calcular estadísticas
        total_messages = len(consultation_session['messages'])
        total_insights = len(consultation_session['patient_insights'])
        therapeutic_bond = self._calculate_therapeutic_bond(consultation_session)
        
        # Análisis emocional
        emotional_analysis = self._analyze_session_emotions(consultation_session)
        
        # Recomendaciones terapéuticas
        recommendations = self._generate_therapeutic_recommendations(consultation_session)
        
        html_report = f"""
        <div class="psychology-report">
            <div class="report-header text-center mb-4">
                <h2 class="text-primary">
                    <i class="fas fa-brain"></i> Informe de Consulta Psicológica
                </h2>
                <div class="report-subtitle">
                    Generado el {datetime.now().strftime('%d de %B de %Y a las %H:%M')}
                </div>
            </div>
            
            <div class="row">
                <div class="col-md-6">
                    <div class="info-card">
                        <h5><i class="fas fa-calendar-alt"></i> Información de Sesión</h5>
                        <table class="table table-sm">
                            <tr><td><strong>ID de Sesión:</strong></td><td>{session_id[:8]}...</td></tr>
                            <tr><td><strong>Fecha de inicio:</strong></td><td>{start_time.strftime('%d/%m/%Y %H:%M')}</td></tr>
                            <tr><td><strong>Duración:</strong></td><td>{str(duration).split('.')[0]}</td></tr>
                            <tr><td><strong>Intercambios:</strong></td><td>{total_messages}</td></tr>
                        </table>
                    </div>
                </div>
                
                <div class="col-md-6">
                    <div class="info-card">
                        <h5><i class="fas fa-chart-line"></i> Métricas Terapéuticas</h5>
                        <table class="table table-sm">
                            <tr><td><strong>Vínculo Terapéutico:</strong></td><td>{int(therapeutic_bond * 100)}%</td></tr>
                            <tr><td><strong>Insights Identificados:</strong></td><td>{total_insights}</td></tr>
                            <tr><td><strong>Participación:</strong></td><td>{"Alta" if total_messages > 5 else "Media"}</td></tr>
                            <tr><td><strong>Estado General:</strong></td><td>{"Progreso positivo" if therapeutic_bond > 0.3 else "En desarrollo"}</td></tr>
                        </table>
                    </div>
                </div>
            </div>
            
            <div class="analysis-section mt-4">
                <h5><i class="fas fa-microscope"></i> Análisis Psicológico</h5>
                <div class="card">
                    <div class="card-body">
                        <h6 class="text-info">Patrones Emocionales Identificados:</h6>
                        <ul>
                            {self._format_emotional_patterns(emotional_analysis)}
                        </ul>
                        
                        <h6 class="text-info mt-3">Insights Terapéuticos:</h6>
                        <ul>
                            {''.join([f'<li>{insight}</li>' for insight in consultation_session['patient_insights'][-5:]])}
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="recommendations-section mt-4">
                <h5><i class="fas fa-lightbulb"></i> Recomendaciones Terapéuticas</h5>
                <div class="card">
                    <div class="card-body">
                        {recommendations}
                    </div>
                </div>
            </div>
            
            <div class="summary-section mt-4">
                <h5><i class="fas fa-clipboard-list"></i> Resumen de Conversación</h5>
                <div class="conversation-summary">
                    {self._format_conversation_summary(consultation_session)}
                </div>
            </div>
            
            <div class="footer-note mt-4 p-3 bg-light rounded">
                <small class="text-muted">
                    <i class="fas fa-info-circle"></i>
                    Este informe ha sido generado por IA con fines informativos y de seguimiento terapéutico.
                    No reemplaza el criterio de un profesional de la salud mental licenciado.
                </small>
            </div>
        </div>
        
        <style>
            .psychology-report {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
            }}
            .info-card {{
                background: #f8f9fa;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                border-left: 4px solid #6b73ff;
            }}
            .analysis-section, .recommendations-section, .summary-section {{
                margin-top: 30px;
            }}
            .conversation-summary {{
                max-height: 300px;
                overflow-y: auto;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
                background: #fafafa;
            }}
            .message-entry {{
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 1px solid #eee;
            }}
            .patient-msg {{
                color: #2c3e50;
                font-weight: 500;
            }}
            .therapist-msg {{
                color: #6b73ff;
                margin-left: 20px;
                font-style: italic;
            }}
        </style>
        """
        
        return html_report
    
    def _analyze_session_emotions(self, consultation_session: dict) -> dict:
        """Analizar las emociones predominantes en la sesión."""
        
        emotion_keywords = {
            'ansiedad': ['nervioso', 'preocupado', 'ansiedad', 'miedo', 'pánico', 'ansiosa'],
            'tristeza': ['triste', 'deprimido', 'sin energía', 'vacío', 'desesperanza', 'melancólico'],
            'estrés': ['estresado', 'agobiado', 'presión', 'tensión', 'overwhelmed', 'agotado'],
            'ira': ['enojado', 'furioso', 'rabia', 'ira', 'frustrated', 'molesto'],
            'esperanza': ['mejor', 'esperanza', 'positivo', 'optimista', 'animado', 'ilusionado']
        }
        
        emotion_counts = {emotion: 0 for emotion in emotion_keywords.keys()}
        
        for message_data in consultation_session['messages']:
            patient_message = message_data['patient_message'].lower()
            for emotion, keywords in emotion_keywords.items():
                for keyword in keywords:
                    if keyword in patient_message:
                        emotion_counts[emotion] += 1
        
        return emotion_counts
    
    def _format_emotional_patterns(self, emotional_analysis: dict) -> str:
        """Formatear los patrones emocionales para el informe."""
        
        patterns = []
        total_emotions = sum(emotional_analysis.values())
        
        if total_emotions == 0:
            return "<li>Expresión emocional moderada durante la sesión</li>"
        
        for emotion, count in emotional_analysis.items():
            if count > 0:
                percentage = (count / total_emotions) * 100
                patterns.append(f"<li><strong>{emotion.capitalize()}:</strong> {count} menciones ({percentage:.1f}%)</li>")
        
        return ''.join(patterns) if patterns else "<li>Expresión emocional equilibrada</li>"
    
    def _generate_therapeutic_recommendations(self, consultation_session: dict) -> str:
        """Generar recomendaciones terapéuticas basadas en la sesión."""
        
        total_messages = len(consultation_session['messages'])
        insights = consultation_session['patient_insights']
        
        recommendations = []
        
        # Recomendaciones basadas en insights
        if any('ansiedad' in insight.lower() for insight in insights):
            recommendations.append("Práctica de técnicas de respiración profunda y mindfulness para manejo de ansiedad")
        
        if any('pensamiento dicotómico' in insight.lower() for insight in insights):
            recommendations.append("Trabajo en reestructuración cognitiva para pensamientos dicotómicos")
        
        if any('autoexigencia' in insight.lower() for insight in insights):
            recommendations.append("Exploración de patrones de autoexigencia y desarrollo de autocompasión")
        
        # Recomendaciones generales
        recommendations.extend([
            "Continuidad en las sesiones terapéuticas para mantener el progreso",
            "Práctica de ejercicios de autocuidado y bienestar emocional",
            "Registro de pensamientos y emociones en un diario terapéutico"
        ])
        
        return '<ul>' + ''.join([f'<li>{rec}</li>' for rec in recommendations]) + '</ul>'
    
    def _format_conversation_summary(self, consultation_session: dict) -> str:
        """Formatear resumen de la conversación."""
        
        summary_html = ""
        
        for i, message_data in enumerate(consultation_session['messages'][-5:], 1):  # Últimos 5 intercambios
            timestamp = datetime.fromisoformat(message_data['timestamp']).strftime('%H:%M')
            
            summary_html += f"""
            <div class="message-entry">
                <div class="patient-msg">
                    <strong>Paciente ({timestamp}):</strong> {message_data['patient_message']}
                </div>
                <div class="therapist-msg">
                    <strong>Dra. Elena:</strong> {message_data['therapist_response'][:200]}...
                </div>
            </div>
            """
        
        return summary_html
    
    def _generate_psychology_report_pdf(self, consultation_session: dict, session_id: str) -> io.BytesIO:
        """Generar informe psicológico en formato PDF."""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#6b73ff')
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#2c3e50')
        )
        
        # Contenido del PDF
        story = []
        
        # Título
        story.append(Paragraph("Informe de Consulta Psicológica", title_style))
        story.append(Spacer(1, 12))
        
        # Información básica
        story.append(Paragraph("Información de la Sesión", heading_style))
        
        start_time = consultation_session['start_time']
        duration = datetime.now() - start_time
        
        session_data = [
            ['ID de Sesión:', f"{session_id[:16]}..."],
            ['Fecha:', start_time.strftime('%d de %B de %Y')],
            ['Hora de inicio:', start_time.strftime('%H:%M')],
            ['Duración:', str(duration).split('.')[0]],
            ['Total de intercambios:', str(len(consultation_session['messages']))]
        ]
        
        session_table = Table(session_data, colWidths=[2*inch, 3*inch])
        session_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        story.append(session_table)
        story.append(Spacer(1, 20))
        
        # Insights identificados
        story.append(Paragraph("Insights Terapéuticos Identificados", heading_style))
        
        if consultation_session['patient_insights']:
            for insight in consultation_session['patient_insights'][-5:]:
                story.append(Paragraph(f"• {insight}", styles['Normal']))
        else:
            story.append(Paragraph("• En proceso de identificación durante futuras sesiones", styles['Normal']))
        
        story.append(Spacer(1, 20))
        
        # Recomendaciones
        story.append(Paragraph("Recomendaciones Terapéuticas", heading_style))
        recommendations = [
            "Continuidad en las sesiones terapéuticas",
            "Práctica de técnicas de respiración y mindfulness",
            "Registro de pensamientos y emociones",
            "Ejercicios de autocuidado y bienestar emocional"
        ]
        
        for rec in recommendations:
            story.append(Paragraph(f"• {rec}", styles['Normal']))
        
        story.append(Spacer(1, 30))
        
        # Nota final
        story.append(Paragraph(
            "Este informe ha sido generado por IA con fines informativos. "
            "No reemplaza el criterio profesional de un psicólogo licenciado.",
            styles['Normal']
        ))
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

# Crear instancia del controlador
psychology_controller = PsychologyConsultationController()

# Rutas del blueprint
@psychology_bp.route('/')
@login_required
def psychology_home():
    """Página principal de consulta psicológica."""
    return psychology_controller.start_psychology_consultation()

@psychology_bp.route('/message', methods=['POST'])
@login_required
@async_route
async def process_message():
    """Procesar mensaje del paciente."""
    return await psychology_controller.process_psychology_message()

@psychology_bp.route('/summary')
@login_required
def session_summary():
    """Obtener resumen de sesión."""
    return psychology_controller.get_psychology_session_summary()

@psychology_bp.route('/generate_report', methods=['POST'])
@login_required
def generate_report():
    """Generar informe psicológico."""
    return psychology_controller.generate_psychology_report()

@psychology_bp.route('/download_report', methods=['POST'])
@login_required
def download_report_pdf():
    """Descargar informe psicológico en formato PDF."""
    return psychology_controller.download_psychology_report_pdf() 
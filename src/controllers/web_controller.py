from flask import Blueprint, render_template, request, redirect, url_for, session, flash, json, jsonify
import logging
import asyncio
from datetime import datetime

from src.agents.medical_agent_graph import MedicalAgentGraph
from src.agents.langgraph_medical_agent import LangGraphMedicalAgent
from src.config.config import MEDICAL_SPECIALTIES, USE_LANGGRAPH
from src.utils.helpers import generate_id
from src.services.conversation_service import ConversationService

logger = logging.getLogger(__name__)

# Create blueprint for web routes
web_bp = Blueprint('web', __name__)

# Initialize the conversation service
conversation_service = ConversationService()

# Initialize the medical agent for compatibility with old code
if USE_LANGGRAPH:
    logger.info("Using LangGraph medical agent implementation")
    medical_agent = LangGraphMedicalAgent()
else:
    logger.info("Using standard medical agent implementation")
    medical_agent = MedicalAgentGraph()

def ensure_serializable(obj):
    """Ensure that the given object is JSON serializable."""
    if isinstance(obj, bytes):
        return obj.decode('utf-8', errors='replace')
    elif isinstance(obj, dict):
        return {k: ensure_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [ensure_serializable(i) for i in obj]
    elif hasattr(obj, 'dict') and callable(getattr(obj, 'dict')):
        return ensure_serializable(obj.dict())
    elif hasattr(obj, 'isoformat') and callable(getattr(obj, 'isoformat')):
        return obj.isoformat()
    else:
        return obj

@web_bp.route('/', methods=['GET'])
def index():
    """Render the home page."""
    return render_template('index.html', specialties=MEDICAL_SPECIALTIES)

@web_bp.route('/chat', methods=['GET'])
def chat():
    """Handle the interactive chat interface."""
    try:
        # Initialize conversation if not exists
        new_conversation = False
        conversation_id = None
        
        # Safely get conversation ID from session
        try:
            if 'interactive_conversation_id' in session:
                # Ensure the ID is a string
                raw_id = session.get('interactive_conversation_id')
                if isinstance(raw_id, bytes):
                    conversation_id = raw_id.decode('utf-8')
                else:
                    conversation_id = str(raw_id)
        except Exception as session_err:
            logger.error(f"Error retrieving conversation ID from session: {session_err}")
            conversation_id = None
        
        # Check if we need a new conversation
        if not conversation_id or request.args.get('new', False):
            # Create a new conversation with default specialty
            initial_specialty = request.args.get('specialty', 'internal_medicine')
            if initial_specialty not in MEDICAL_SPECIALTIES:
                initial_specialty = 'internal_medicine'
                
            conversation = conversation_service.create_conversation(initial_specialty)
            # Store the ID as a string in the session
            session['interactive_conversation_id'] = str(conversation.conversation_id)
            new_conversation = True
        else:
            # Get the existing conversation
            conversation = conversation_service.get_conversation(conversation_id)
            if not conversation:
                # If conversation not found, create a new one
                conversation = conversation_service.create_conversation()
                session['interactive_conversation_id'] = str(conversation.conversation_id)
                new_conversation = True
        
        # Clear any report-related session data when starting/viewing a conversation
        if 'report_conversation_id' in session:
            session.pop('report_conversation_id', None)
        
        logger.info(f"Rendering chat template with conversation ID: {conversation.conversation_id}")
        
        # Return the interactive chat interface
        return render_template(
            'chat.html',
            specialties=MEDICAL_SPECIALTIES,
            conversation=conversation
        )
    except Exception as e:
        logger.error(f"Error in chat route: {e}")
        import traceback
        logger.error(traceback.format_exc())
        flash('Ha ocurrido un error al cargar la conversación. Por favor intenta nuevamente.', 'danger')
        return redirect(url_for('web.index'))

@web_bp.route('/chat/message', methods=['POST'])
async def send_message():
    """Send a message in the interactive chat."""
    try:
        # Get the conversation ID safely
        conversation_id = None
        try:
            if 'interactive_conversation_id' in session:
                raw_id = session.get('interactive_conversation_id')
                if isinstance(raw_id, bytes):
                    conversation_id = raw_id.decode('utf-8')
                else:
                    conversation_id = str(raw_id)
        except Exception as session_err:
            logger.error(f"Error retrieving conversation ID from session: {session_err}")
        
        if not conversation_id:
            return jsonify({"error": "No active conversation"}), 400
        
        # Get the message
        message = request.form.get('message')
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        # Process the message
        response = await conversation_service.process_message(conversation_id, message)
        
        # Get the updated conversation
        conversation = conversation_service.get_conversation(conversation_id)
        
        # Return the response with serialized data
        return jsonify({
            "success": True,
            "response": response,
            "conversation": ensure_serializable(conversation) if conversation else None
        })
        
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return jsonify({
            "error": "Failed to process message",
            "message": str(e)
        }), 500

@web_bp.route('/chat/switch_specialty', methods=['POST'])
async def switch_specialty():
    """Switch the specialty in the interactive chat."""
    try:
        # Get the conversation ID safely
        conversation_id = None
        try:
            if 'interactive_conversation_id' in session:
                raw_id = session.get('interactive_conversation_id')
                if isinstance(raw_id, bytes):
                    conversation_id = raw_id.decode('utf-8')
                else:
                    conversation_id = str(raw_id)
        except Exception as session_err:
            logger.error(f"Error retrieving conversation ID from session: {session_err}")
        
        if not conversation_id:
            return jsonify({"error": "No active conversation"}), 400
        
        # Get the new specialty
        new_specialty = request.form.get('specialty')
        if not new_specialty or new_specialty not in MEDICAL_SPECIALTIES:
            return jsonify({"error": "Invalid specialty"}), 400
        
        # Switch the specialty
        response = await conversation_service.switch_specialty(conversation_id, new_specialty)
        
        # Get the updated conversation
        conversation = conversation_service.get_conversation(conversation_id)
        
        # Return the response with serialized data
        return jsonify({
            "success": True,
            "response": response,
            "conversation": ensure_serializable(conversation) if conversation else None
        })
        
    except Exception as e:
        logger.error(f"Error switching specialty: {e}")
        return jsonify({
            "error": "Failed to switch specialty",
            "message": str(e)
        }), 500

@web_bp.route('/new_chat', methods=['GET'])
def new_chat():
    """Start a new chat session."""
    # Clear the session for a new conversation
    if 'interactive_conversation_id' in session:
        session.pop('interactive_conversation_id', None)
    
    # Also clear any report-related session data
    if 'report_conversation_id' in session:
        session.pop('report_conversation_id', None)
    
    return redirect(url_for('web.chat', new=1))

@web_bp.route('/about', methods=['GET'])
def about():
    """Render the about page."""
    return render_template('about.html')

@web_bp.route('/faq', methods=['GET'])
def faq():
    """Render the FAQ page."""
    return render_template('faq.html') 
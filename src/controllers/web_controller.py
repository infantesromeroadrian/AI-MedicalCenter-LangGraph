from flask import Blueprint, render_template, request, redirect, url_for, session, flash, json, jsonify
import logging
import asyncio
from datetime import datetime
from functools import wraps

from src.agents.medical_system_integration import MedicalSystemManager
from src.config.config import MEDICAL_SPECIALTIES, USE_LANGGRAPH
from src.utils.helpers import generate_id
from src.services.conversation_service import ConversationService
from src.services.user_service import UserService
from src.utils.auth_middleware import login_required
from src.utils.async_utils import async_route

logger = logging.getLogger(__name__)

# Create blueprint for web routes
web_bp = Blueprint('web', __name__)

# Initialize the conversation service
conversation_service = ConversationService()

# Initialize the user service
user_service = UserService()

# Initialize the ADVANCED medical system in FAST MODE for quick responses
logger.info("Initializing advanced medical system in FAST MODE...")
medical_agent = MedicalSystemManager(use_advanced_system=True, fast_mode=True)
logger.info("Advanced medical system (FAST MODE) initialized successfully")

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

def ensure_string_id(conversation_id):
    """Ensure the conversation ID is a string, not bytes."""
    if isinstance(conversation_id, bytes):
        return conversation_id.decode('utf-8', errors='replace')
    elif conversation_id is not None:
        return str(conversation_id)
    return None

@web_bp.route('/', methods=['GET'])
@login_required
def index():
    """Render the home page."""
    return render_template('index.html', specialties=MEDICAL_SPECIALTIES)

@web_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    # If user is already logged in, redirect to home
    if 'user_id' in session:
        return redirect(url_for('web.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('login.html')
        
        user = user_service.authenticate(username, password)
        
        if user:
            # Store user information in session
            session['user_id'] = user.user_id
            session['username'] = user.username
            
            # Set session to permanent if remember me is checked
            if remember:
                session.permanent = True
            
            # If there's a next URL, redirect there
            next_url = session.pop('next_url', None)
            if next_url:
                return redirect(next_url)
            
            return redirect(url_for('web.index'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@web_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    # If user is already logged in, redirect to home
    if 'user_id' in session:
        return redirect(url_for('web.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not password or not confirm_password:
            flash('Please fill in all fields.', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        
        # Check if username already exists
        existing_user = user_service.get_user_by_username(username)
        if existing_user:
            flash('Username already exists.', 'danger')
            return render_template('register.html')
        
        # Create new user
        user = user_service.create_user(username, password)
        
        if user:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('web.login'))
        else:
            flash('Error creating user.', 'danger')
    
    return render_template('register.html')

@web_bp.route('/logout', methods=['GET'])
def logout():
    """Handle user logout."""
    # Clear session data
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('web.login'))

@web_bp.route('/chat', methods=['GET'])
@login_required
def chat():
    """Handle the interactive chat interface."""
    try:
        # Initialize conversation if not exists
        new_conversation = False
        
        # Safely get conversation ID from session
        conversation_id = ensure_string_id(session.get('interactive_conversation_id'))
        
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
@login_required
@async_route
async def send_message():
    """Send a message in the interactive chat."""
    try:
        # Get the conversation ID safely
        conversation_id = ensure_string_id(session.get('interactive_conversation_id'))
        
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
@login_required
@async_route
async def switch_specialty():
    """Switch the specialty in the interactive chat."""
    try:
        # Get the conversation ID safely
        conversation_id = ensure_string_id(session.get('interactive_conversation_id'))
        
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
@login_required
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
@login_required
def about():
    """Render the about page."""
    return render_template('about.html')

@web_bp.route('/faq', methods=['GET'])
@login_required
def faq():
    """Render the FAQ page."""
    return render_template('faq.html') 
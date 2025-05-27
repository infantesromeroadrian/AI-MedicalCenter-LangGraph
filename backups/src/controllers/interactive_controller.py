from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, send_file
import logging
import asyncio
from datetime import datetime
import uuid
import io
import os
from pathlib import Path
import traceback
from functools import wraps

from src.services.conversation_service import ConversationService
from src.services.report_service import generate_medical_report, generate_pdf_report
from src.config.config import MEDICAL_SPECIALTIES, BASE_DIR
from src.utils.auth_middleware import login_required
from src.utils.async_utils import async_route

logger = logging.getLogger(__name__)

# Create blueprint for interactive chat routes
interactive_bp = Blueprint('interactive', __name__)

# Initialize the conversation service
conversation_service = ConversationService()

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

@interactive_bp.route('/', methods=['GET', 'POST'])
@login_required
@async_route
async def interactive_chat_home():
    """Handle the interactive chat interface."""
    try:
        # Initialize conversation if not exists
        new_conversation = False
        initial_symptoms = None
        
        # Check for initial symptoms form submission (for new conversations)
        if request.method == 'POST' and 'initial_symptoms' in request.form:
            initial_symptoms = request.form.get('initial_symptoms')
            new_conversation = True
        
        # Safely get conversation ID from session
        current_id = session.get('interactive_conversation_id')
        conversation_id = ensure_string_id(current_id)
        
        # Check if we need a new conversation
        if not conversation_id or request.args.get('new') or new_conversation:
            # For new conversations with initial symptoms, use the triage feature
            if initial_symptoms:
                conversation = await conversation_service.create_conversation_with_triage(initial_symptoms)
            else:
                # Create a new conversation with default specialty if no symptoms provided
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
            
        logger.info(f"Rendering interactive chat template with conversation ID: {conversation.conversation_id}")
        
        return render_template(
            'interactive_chat.html',
            conversation=conversation,
            specialties=MEDICAL_SPECIALTIES
        )
    except Exception as e:
        logger.error(f"Error in interactive_chat_home: {e}")
        import traceback
        logger.error(traceback.format_exc())
        flash('Ha ocurrido un error al cargar la conversación interactiva. Por favor intenta nuevamente.', 'danger')
        return redirect(url_for('web.index'))

@interactive_bp.route('/message', methods=['POST'])
@login_required
@async_route
async def send_message():
    """Send a message in the interactive chat."""
    try:
        # Get the conversation ID and ensure it's a string
        current_id = session.get('interactive_conversation_id')
        conversation_id = ensure_string_id(current_id)
        
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

@interactive_bp.route('/conversation', methods=['GET'])
@login_required
def get_conversation():
    """Get the current conversation."""
    try:
        # Get the conversation ID and ensure it's a string
        current_id = session.get('interactive_conversation_id')
        conversation_id = ensure_string_id(current_id)
        
        if not conversation_id:
            return jsonify({"error": "No active conversation"}), 400
        
        # Get the conversation
        conversation = conversation_service.get_conversation(conversation_id)
        if not conversation:
            return jsonify({"error": "Conversation not found"}), 404
        
        # Return the conversation with serialized data
        return jsonify({
            "success": True,
            "conversation": ensure_serializable(conversation)
        })
        
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        return jsonify({
            "error": "Failed to get conversation",
            "message": str(e)
        }), 500

@interactive_bp.route('/generate_report', methods=['GET'])
@login_required
@async_route
async def generate_report():
    """Generate a medical report for the current conversation."""
    try:
        # Get the conversation ID and ensure it's a string
        current_id = session.get('interactive_conversation_id')
        conversation_id = ensure_string_id(current_id)
        
        if not conversation_id:
            return jsonify({"error": "No active conversation"}), 400
        
        # Get the conversation
        conversation = conversation_service.get_conversation(conversation_id)
        if not conversation:
            return jsonify({"error": "Conversation not found"}), 404
        
        # Generate the report using LLM
        report_html = await generate_medical_report(conversation)
        logger.info(f"Report generated, type: {type(report_html)}")
        
        # Ensure report_html is a string
        if isinstance(report_html, bytes):
            report_html = report_html.decode('utf-8', errors='replace')
        
        # Store the report in session for download later
        # Don't store the HTML in session, it's too large and causing issues
        # Instead, store the conversation_id which we can use to regenerate it
        session['report_conversation_id'] = str(conversation_id)
        
        # Return the report HTML
        return jsonify({
            "success": True,
            "report": report_html
        })
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return jsonify({
            "error": "Failed to generate report",
            "message": str(e)
        }), 500

@interactive_bp.route('/download_report', methods=['GET'])
@login_required
@async_route
async def download_report():
    """Download the medical report as PDF."""
    try:
        # Get the conversation ID from session or query parameter and ensure it's a string
        query_id = request.args.get('id')
        report_id = session.get('report_conversation_id')
        interactive_id = session.get('interactive_conversation_id')
        
        conversation_id = ensure_string_id(query_id or report_id or interactive_id)
        
        if not conversation_id:
            logger.error("No conversation ID found for PDF generation")
            return jsonify({"error": "No active conversation found"}), 400
        
        logger.info(f"Generating PDF report for conversation: {conversation_id}")
        
        # Generate the report for this conversation
        conversation = conversation_service.get_conversation(conversation_id)
        if not conversation:
            logger.error(f"Conversation {conversation_id} not found")
            return jsonify({"error": "Conversation not found"}), 404
        
        # Generate the HTML report
        try:
            report_html = await generate_medical_report(conversation)
            if isinstance(report_html, bytes):
                report_html = report_html.decode('utf-8', errors='replace')
        except Exception as report_err:
            logger.error(f"Error generating HTML report: {report_err}")
            return jsonify({"error": f"Error generating report: {str(report_err)}"}), 500
        
        # Generate PDF from HTML
        try:
            logger.info("Generating PDF from HTML")
            pdf_buffer = await generate_pdf_report(report_html, conversation_id)
            logger.info(f"PDF generated, size: {len(pdf_buffer)} bytes")
            
            if not pdf_buffer or len(pdf_buffer) < 100:
                logger.error(f"Generated PDF is too small or empty: {len(pdf_buffer)} bytes")
                return jsonify({"error": "Generated PDF is invalid"}), 500
        except Exception as pdf_err:
            logger.error(f"Error generating PDF: {pdf_err}")
            return jsonify({"error": f"Error generating PDF: {str(pdf_err)}"}), 500
        
        # Create a BytesIO object to serve the PDF
        try:
            pdf_io = io.BytesIO(pdf_buffer)
            pdf_io.seek(0)
        except Exception as io_err:
            logger.error(f"Error with BytesIO: {io_err}")
            return jsonify({"error": f"Error preparing PDF: {str(io_err)}"}), 500
        
        # Set a unique filename including timestamp to avoid browser caching
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"informe_medico_{conversation_id}_{timestamp}.pdf"
        
        # Return the PDF file with appropriate headers to prevent caching
        logger.info(f"Sending PDF file to client: {filename}")
        return send_file(
            pdf_io,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename,
            max_age=0,
            # Add headers to prevent caching
            etag=False,
            last_modified=None,
            conditional=False
        )
        
    except Exception as e:
        logger.error(f"Error downloading report: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "error": "Failed to download report",
            "message": str(e)
        }), 500 
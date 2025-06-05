from flask import Blueprint, request, jsonify
import logging
from typing import Dict, Any, Optional
import json
import asyncio
from functools import wraps

from src.models.data_models import UserQuery, ConsensusResponse
from src.agents.medical_system_integration import MedicalSystemManager
from src.utils.helpers import generate_id, log_conversation
from src.config.config import USE_LANGGRAPH
from src.utils.async_utils import async_route

logger = logging.getLogger(__name__)

# Create blueprint for API routes
api_bp = Blueprint('api', __name__)

# Initialize the ADVANCED medical system in FAST MODE for API responses
logger.info("Initializing advanced medical system in FAST MODE for API...")
medical_agent = MedicalSystemManager(use_advanced_system=True, fast_mode=True)
logger.info("Advanced medical system (FAST MODE) initialized successfully for API")

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify API is running."""
    return jsonify({"status": "healthy", "message": "Medical Agents API is running"}), 200

@api_bp.route('/query', methods=['POST'])
@async_route
async def process_query():
    """Process a medical query through the agent system."""
    try:
        # Get request data
        data = request.json
        
        if not data or not data.get('query'):
            return jsonify({"error": "Missing required 'query' field"}), 400
        
        # Extract query parameters
        query = data.get('query')
        specialty = data.get('specialty')
        context = data.get('context')
        
        # Generate a conversation ID if not provided
        conversation_id = data.get('conversation_id', generate_id())
        
        # Process the query through the ADVANCED medical system
        response = await medical_agent.process_medical_query(
            query=query,
            specialty=specialty,
            medical_criteria="API medical consultation",
            context=context
        )
        
        # Log the conversation (convert to dict format)
        log_conversation(query, response.__dict__, conversation_id)
        
        # Return the response
        return jsonify({
            "conversation_id": conversation_id,
            "response": response.__dict__
        }), 200
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({
            "error": "Failed to process medical query",
            "message": str(e)
        }), 500

@api_bp.route('/specialties', methods=['GET'])
def get_specialties():
    """Get a list of available medical specialties."""
    from src.config.config import MEDICAL_SPECIALTIES
    
    return jsonify({
        "specialties": MEDICAL_SPECIALTIES
    }), 200 
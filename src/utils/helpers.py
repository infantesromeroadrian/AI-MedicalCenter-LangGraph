import uuid
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def generate_id() -> str:
    """Generate a unique ID for conversations and sessions."""
    # Return the string representation to avoid byte issues
    return str(uuid.uuid4())

def log_conversation(user_query: str, response: Dict[str, Any], conversation_id: str) -> None:
    """Log conversation to file for future reference and analysis."""
    timestamp = datetime.now().isoformat()
    log_entry = {
        'timestamp': timestamp,
        'conversation_id': conversation_id,
        'user_query': user_query,
        'response': response
    }
    
    try:
        with open('logs/conversations.json', 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        logger.error(f"Failed to log conversation: {e}")

def format_agent_prompt(specialty: str, query: str, context: Optional[Dict[str, Any]] = None) -> str:
    """Format the prompt for a specific medical specialty agent."""
    base_prompt = f"""You are a specialized AI assistant in {specialty}. 
    
A patient has the following query or condition: 
"{query}"

Based on your specific expertise in {specialty}, provide a detailed and helpful response.
Include diagnostics considerations, potential treatments, and recommendations where appropriate.
Make sure to note when a condition might be outside your specialty and require additional consultation.
"""
    
    if context:
        context_str = "\n\nAdditional context:\n"
        for key, value in context.items():
            context_str += f"- {key}: {value}\n"
        base_prompt += context_str
        
    return base_prompt

def detect_medical_emergencies(text: str) -> Dict[str, Any]:
    """
    Analyze text to detect potential medical emergencies that require immediate attention.
    Returns a dict with emergency status and details.
    """
    emergency_keywords = [
        "can't breathe", "cannot breathe", "difficulty breathing", 
        "chest pain", "heart attack", "stroke", "unconscious",
        "severe bleeding", "seizure", "convulsion", 
        "suicide", "suicidal", "overdose", "poisoning"
    ]
    
    detected_keywords = [kw for kw in emergency_keywords if kw.lower() in text.lower()]
    
    result = {
        "is_emergency": len(detected_keywords) > 0,
        "detected_terms": detected_keywords,
        "recommendation": ""
    }
    
    if result["is_emergency"]:
        result["recommendation"] = "This appears to be a medical emergency. Please call emergency services (911) immediately."
        
    return result 
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

def detect_medical_emergencies(text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyze text to detect potential medical emergencies using advanced detection system.
    
    Args:
        text: The user's medical query or text to analyze
        context: Optional context including age, medical history, etc.
        
    Returns:
        Dict containing comprehensive emergency information
    """
    try:
        # Import the advanced emergency detector
        from src.utils.emergency_detector import detect_medical_emergencies as advanced_detect
        
        # Use the advanced detection system
        advanced_result = advanced_detect(text, context)
        
        # Return the advanced result (already in compatible format)
        return advanced_result
        
    except ImportError:
        # Fallback to basic detection if advanced system is not available
        logger.warning("Advanced emergency detection not available, using basic detection")
        return _basic_emergency_detection(text)

def _basic_emergency_detection(text: str) -> Dict[str, Any]:
    """
    Basic emergency detection fallback.
    
    Args:
        text: The user's medical query
        
    Returns:
        Dict containing basic emergency information
    """
    emergency_keywords = [
        "can't breathe", "cannot breathe", "difficulty breathing", 
        "chest pain", "heart attack", "stroke", "unconscious",
        "severe bleeding", "seizure", "convulsion", 
        "suicide", "suicidal", "overdose", "poisoning",
        # Spanish equivalents
        "no puedo respirar", "dificultad respirar", "dolor pecho",
        "infarto", "derrame", "inconsciente", "sangrado severo",
        "convulsión", "suicidio", "sobredosis"
    ]
    
    detected_keywords = [kw for kw in emergency_keywords if kw.lower() in text.lower()]
    
    is_emergency = len(detected_keywords) > 0
    is_critical = any(kw in text.lower() for kw in [
        "heart attack", "stroke", "unconscious", "severe bleeding", 
        "suicide", "overdose", "infarto", "derrame", "inconsciente"
    ])
    
    result = {
        "is_emergency": is_emergency,
        "detected_terms": detected_keywords,
        "recommendation": "",
        "urgency_level": 5 if is_critical else 3 if is_emergency else 1,
        "emergency_score": 0.9 if is_critical else 0.6 if is_emergency else 0.1,
        "primary_concern": detected_keywords[0] if detected_keywords else "No emergency detected",
        "time_sensitivity": "IMMEDIATE" if is_critical else "URGENT" if is_emergency else "ROUTINE",
        "action_required": "Call 911 immediately" if is_critical else "Seek medical care" if is_emergency else "Regular consultation",
        "signals_detected": len(detected_keywords)
    }
    
    if is_critical:
        result["recommendation"] = "🚨 EMERGENCY: This appears to be a critical medical emergency. Call 911 immediately."
    elif is_emergency:
        result["recommendation"] = "⚠️ This appears to be a medical emergency. Seek immediate medical attention."
    else:
        result["recommendation"] = "Continue with normal medical consultation."
        
    return result 
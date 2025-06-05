import logging
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import os
import traceback

from src.models.data_models import InteractiveConversation, MessageType, UserQuery
from src.utils.helpers import generate_id
from src.agents.medical_system_integration import MedicalSystemManager
from src.services.llm_service import LLMService
from src.config.config import BASE_DIR

logger = logging.getLogger(__name__)

class ConversationService:
    """Service to manage interactive conversations with medical specialists (Singleton)."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        """Ensure only one instance of ConversationService exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the conversation service (only once)."""
        # Only initialize once
        if ConversationService._initialized:
            return
            
        self.conversations: Dict[str, InteractiveConversation] = {}
        self.medical_system = MedicalSystemManager(use_advanced_system=True, fast_mode=True)
        self.conversation_dir = BASE_DIR / "data" / "conversations"
        self.llm_service = LLMService()  # Para clasificación de especialidad
        
        # Umbral de confianza para cambios automáticos de especialidad (valor muy estricto para evitar cambios innecesarios)
        self.specialty_confidence_threshold = 0.95
        
        # Tracking para cambios de especialidad
        self.specialty_changes = {}  # Dict[conversation_id, Dict[info]]
        
        # Ensure directory exists
        os.makedirs(self.conversation_dir, exist_ok=True)
        
        # Clean up any corrupted files from previous runs
        self._cleanup_corrupted_files()
        
        # Load any existing conversations
        self._load_conversations()
        
        # Mark as initialized
        ConversationService._initialized = True
        logger.info("ConversationService singleton initialized with ADVANCED medical system")
    
    def _cleanup_corrupted_files(self):
        """Clean up any corrupted files from previous runs."""
        try:
            count = 0
            for filename in os.listdir(self.conversation_dir):
                if '.corrupted.' in filename:
                    try:
                        file_path = self.conversation_dir / filename
                        os.remove(file_path)
                        count += 1
                    except Exception as e:
                        logger.error(f"Failed to delete corrupted file {filename}: {e}")
            if count > 0:
                logger.info(f"Deleted {count} corrupted conversation files from previous runs")
        except Exception as e:
            logger.error(f"Error cleaning up corrupted files: {e}")
    
    def _load_conversations(self):
        """Load conversations from disk."""
        try:
            for filename in os.listdir(self.conversation_dir):
                if filename.endswith('.json'):
                    file_path = self.conversation_dir / filename
                    try:
                        with open(file_path, 'r') as f:
                            data = json.load(f)
                            conv = InteractiveConversation(**data)
                            self.conversations[conv.conversation_id] = conv
                            logger.info(f"Loaded conversation {conv.conversation_id} from disk")
                    except json.JSONDecodeError as e:
                        # Delete corrupted files rather than renaming them repeatedly
                        try:
                            os.remove(file_path)
                            logger.error(f"Deleted corrupted conversation file {file_path}: {e}")
                        except Exception as remove_err:
                            logger.error(f"Failed to delete corrupted file {file_path}: {remove_err}")
                    except Exception as e:
                        logger.error(f"Error loading conversation from {file_path}: {e}")
        except Exception as e:
            logger.error(f"Error loading conversations: {e}")
    
    def _save_conversation(self, conversation_id: str):
        """Save a conversation to disk with improved error handling."""
        try:
            conv = self.conversations.get(conversation_id)
            if not conv:
                logger.error(f"Cannot save conversation {conversation_id}: not found in memory")
                return False
                
            file_path = self.conversation_dir / f"{conversation_id}.json"
            
            # Convert the conversation to a dict first, which will handle datetime serialization
            conversation_dict = conv.dict()
            
            # Create a custom JSON encoder to handle datetime objects
            class DateTimeEncoder(json.JSONEncoder):
                def default(self, obj):
                    if hasattr(obj, 'isoformat'):
                        return obj.isoformat()
                    return super().default(obj)
            
            # Save to a temporary file first to avoid corruption
            temp_file_path = file_path.with_suffix('.tmp')
            
            with open(temp_file_path, 'w', encoding='utf-8') as f:
                json.dump(conversation_dict, f, indent=2, cls=DateTimeEncoder, ensure_ascii=False)
            
            # Move the temporary file to the final location
            temp_file_path.replace(file_path)
            
            logger.info(f"Saved conversation {conversation_id} to disk")
            return True
            
        except Exception as e:
            logger.error(f"Error saving conversation {conversation_id}: {e}")
            # Clean up temporary file if it exists
            temp_file_path = self.conversation_dir / f"{conversation_id}.tmp"
            if temp_file_path.exists():
                try:
                    temp_file_path.unlink()
                except:
                    pass
            return False
    
    def create_conversation(self, initial_specialty: str = "internal_medicine") -> InteractiveConversation:
        """Create a new conversation."""
        conversation_id = generate_id()
        conversation = InteractiveConversation(
            conversation_id=conversation_id,
            active_specialty=initial_specialty,
            all_specialties=[initial_specialty]
        )
        
        # Add welcome message
        conversation.add_message(
            content=f"Bienvenido a la consulta médica interactiva. Estás hablando con un especialista en {initial_specialty}. "
                   f"¿En qué puedo ayudarte hoy? (El sistema automáticamente te dirigirá al especialista más adecuado según tu consulta)",
            sender="system"
        )
        
        self.conversations[conversation_id] = conversation
        self._save_conversation(conversation_id)
        
        return conversation
    
    async def create_conversation_with_triage(self, initial_query: str = None) -> InteractiveConversation:
        """Create a new conversation with initial triage to determine the best specialty."""
        conversation_id = generate_id()
        
        # Default to internal_medicine if no initial query
        initial_specialty = "internal_medicine"
        
        # If there's an initial query, use triage to determine the best specialty
        if initial_query:
            try:
                specialty_classification = await self.llm_service.classify_specialty(initial_query)
                recommended_specialty = specialty_classification["recommended_specialty"]
                confidence = specialty_classification["confidence"]
                
                # Only use the recommended specialty if confidence is high enough
                if confidence >= 0.7:
                    initial_specialty = recommended_specialty
                    logger.info(f"Triage inicial recomendó especialidad {initial_specialty} con confianza {confidence}")
            except Exception as e:
                logger.error(f"Error en triaje inicial: {e}")
        
        # Create the conversation with the determined specialty
        conversation = InteractiveConversation(
            conversation_id=conversation_id,
            active_specialty=initial_specialty,
            all_specialties=[initial_specialty]
        )
        
        # Add welcome message
        conversation.add_message(
            content=f"Bienvenido a la consulta médica interactiva. Estás hablando con un especialista en {initial_specialty}. "
                   f"¿En qué puedo ayudarte hoy? (El sistema automáticamente te dirigirá al especialista más adecuado según tu consulta)",
            sender="system"
        )
        
        # If there was an initial query, add it to the conversation as user message
        if initial_query:
            conversation.add_message(content=initial_query, sender="user")
            
            # Process the message to get the initial response from the specialist using advanced system
            try:
                specialty = conversation.active_specialty
                
                # Create context of the conversation
                context = {
                    "conversation_history": [conversation.messages[0].dict()]  # Only the welcome message
                }
                
                # Process the query with the advanced system
                agent_message = await self._process_with_advanced_system(
                    query=initial_query,
                    specialty=specialty,
                    context=context
                )
                
                # Add specialist's response
                conversation.add_message(content=agent_message, sender=specialty)
            except Exception as e:
                logger.error(f"Error processing initial query: {e}")
                # Add a generic response if there's an error
                conversation.add_message(
                    content=f"Como especialista en {initial_specialty}, estoy listo para ayudarte. Por favor, cuéntame más sobre tu consulta.",
                    sender=initial_specialty
                )
        
        self.conversations[conversation_id] = conversation
        self._save_conversation(conversation_id)
        
        return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[InteractiveConversation]:
        """Get a conversation by ID. If not in memory, try to load from disk."""
        # First, check if conversation is in memory
        if conversation_id in self.conversations:
            return self.conversations[conversation_id]
        
        # If not in memory, try to load from disk
        try:
            file_path = self.conversation_dir / f"{conversation_id}.json"
            if file_path.exists():
                logger.info(f"Loading conversation {conversation_id} from disk on-demand")
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    conv = InteractiveConversation(**data)
                    # Add to memory cache
                    self.conversations[conv.conversation_id] = conv
                    logger.info(f"Successfully loaded conversation {conversation_id} from disk")
                    return conv
            else:
                logger.warning(f"Conversation file {file_path} does not exist")
                return None
        except Exception as e:
            logger.error(f"Error loading conversation {conversation_id} from disk: {e}")
            return None
    
    def get_all_conversations(self) -> List[InteractiveConversation]:
        """Get all conversations."""
        return list(self.conversations.values())
    
    async def _process_with_advanced_system(self, query: str, specialty: str = None, context: Dict = None):
        """Process query using the advanced medical system."""
        try:
            response = await self.medical_system.process_medical_query(
                query=query,
                specialty=specialty,
                medical_criteria="Interactive conversation",
                context=context
            )
            return response.primary_response
        except Exception as e:
            logger.error(f"Error with advanced system: {e}")
            return f"Lo siento, he experimentado un problema técnico. ¿Podrías reformular tu consulta?"
    
    async def process_message(self, conversation_id: str, message: str) -> Optional[str]:
        """Process a user message in a conversation."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            logger.error(f"Conversation {conversation_id} not found")
            return None
        
        # Add the user message
        conversation.add_message(content=message, sender="user")
        
        try:
            # Primero, determinar si necesitamos cambiar de especialista basado en el contenido del mensaje
            specialty_classification = await self.llm_service.classify_specialty(message)
            recommended_specialty = specialty_classification["recommended_specialty"]
            confidence = specialty_classification["confidence"]
            reasoning = specialty_classification["reasoning"]
            
            current_specialty = conversation.active_specialty
            
            logger.info(f"Clasificación especialidad: {recommended_specialty} (confianza: {confidence}) - Razonamiento: {reasoning}")
            
            # Verificar si hubo cambios recientes de especialidad para evitar cambios rápidos
            can_switch = True
            last_switch_time = None
            
            if conversation_id in self.specialty_changes:
                changes = self.specialty_changes[conversation_id]
                last_switch_time = changes.get('last_switch_time')
                switch_count = changes.get('count', 0)
                
                # No permitir más de 2 cambios en los últimos 5 minutos
                if last_switch_time and (datetime.now() - last_switch_time) < timedelta(minutes=5):
                    if switch_count >= 2:
                        can_switch = False
                        logger.info(f"Bloqueando cambio automático de especialidad - demasiados cambios recientes")
            
            # Verificar si el paciente está proporcionando información adicional sobre el mismo tema
            is_follow_up = self._is_follow_up_message(message, conversation)
            
            # Si el especialista recomendado es diferente al actual y hay buena confianza, hacer un cambio
            # PERO NO si es una respuesta de seguimiento del mismo tema
            if (recommended_specialty != current_specialty and 
                confidence >= self.specialty_confidence_threshold and 
                can_switch and 
                not is_follow_up):
                logger.info(f"Orquestador cambiando automáticamente de {current_specialty} a {recommended_specialty} (confianza: {confidence})")
                
                # Registrar el cambio de especialidad
                now = datetime.now()
                if conversation_id not in self.specialty_changes:
                    self.specialty_changes[conversation_id] = {'count': 1, 'last_switch_time': now}
                else:
                    # Reiniciar contador si pasaron más de 10 minutos desde el último cambio
                    if last_switch_time and (now - last_switch_time) > timedelta(minutes=10):
                        self.specialty_changes[conversation_id] = {'count': 1, 'last_switch_time': now}
                    else:
                        self.specialty_changes[conversation_id]['count'] = self.specialty_changes[conversation_id].get('count', 0) + 1
                        self.specialty_changes[conversation_id]['last_switch_time'] = now
                
                # Añadir mensaje del sistema explicando el cambio
                conversation.add_message(
                    content=f"⚕️ El orquestador médico ha determinado que un especialista en {recommended_specialty} puede responder mejor a tu consulta. Motivo: {reasoning}. Transfiriendo...",
                    sender="system"
                )
                
                # Cambiar a la nueva especialidad
                conversation.switch_specialty(recommended_specialty)
                
                # Procesar con el sistema avanzado usando la nueva especialidad
                try:
                    # El sistema avanzado maneja automáticamente la especialidad
                    pass  # Se procesará más abajo
                except Exception as agent_error:
                    logger.error(f"Error al cambiar a especialidad {recommended_specialty}: {agent_error}")
                    # Si falla el cambio, volver a la especialidad anterior
                    conversation.switch_specialty(current_specialty)
                    conversation.add_message(
                        content=f"Lo siento, no se pudo conectar con el especialista en {recommended_specialty}. Continuando con {current_specialty}.",
                        sender="system"
                    )
                
                # Crear contexto relevante
                context = {
                    "conversation_history": [msg.dict() for msg in conversation.messages[:-2]],  # Todos los mensajes excepto los dos últimos
                    "previous_specialty": current_specialty,
                    "auto_transfer": True,  # Indicar que fue un cambio automático
                    "confidence": confidence,
                    "reasoning": reasoning
                }
                
                # Generar respuesta del nuevo especialista usando sistema avanzado
                try:
                    specialist_message = await self._process_with_advanced_system(
                        query=message,
                        specialty=recommended_specialty,
                        context=context
                    )
                except Exception as agent_response_error:
                    logger.error(f"Error al procesar consulta con {recommended_specialty}: {agent_response_error}")
                    specialist_message = f"Como especialista en {recommended_specialty}, me gustaría responder a tu consulta, pero estoy experimentando algunas dificultades técnicas. ¿Podrías reformular tu pregunta?"
                
                # Añadir respuesta del especialista
                conversation.add_message(content=specialist_message, sender=recommended_specialty)
                
                # Guardar conversación actualizada
                self._save_conversation(conversation_id)
                
                return specialist_message
            else:
                # Si no hay cambio de especialidad, proceder con sistema avanzado
                specialty = conversation.active_specialty
                
                # Crear contexto de la conversación
                context = {
                    "conversation_history": [msg.dict() for msg in conversation.messages[:-1]]  # Todos los mensajes excepto el actual
                }
                
                # Procesar la consulta con el sistema avanzado
                try:
                    agent_message = await self._process_with_advanced_system(
                        query=message,
                        specialty=specialty,
                        context=context
                    )
                except Exception as agent_error:
                    logger.error(f"Error al procesar consulta con {specialty}: {agent_error}")
                    agent_message = f"Lo siento, como especialista en {specialty}, estoy experimentando algunas dificultades para procesar tu consulta. ¿Podrías reformular tu pregunta o intentarlo de nuevo más tarde?"
                
                # Añadir respuesta del especialista
                conversation.add_message(content=agent_message, sender=specialty)
                
                # Guardar conversación actualizada
                self._save_conversation(conversation_id)
                
                return agent_message
            
        except Exception as e:
            logger.error(f"Error processing message in conversation {conversation_id}: {e}")
            logger.error(traceback.format_exc())
            
            specialty = conversation.active_specialty
            
            error_message = f"Lo siento, ha ocurrido un error al procesar tu mensaje. Como especialista en {specialty}, puedo intentar responder si reformulas tu pregunta de otra manera."
            conversation.add_message(content=error_message, sender=specialty)
            
            # Guardar conversación incluso en caso de error
            self._save_conversation(conversation_id)
            
            return error_message
    
    def _is_follow_up_message(self, message: str, conversation: InteractiveConversation) -> bool:
        """Detectar si el mensaje es una respuesta de seguimiento al mismo tema médico"""
        
        # Si hay menos de 2 mensajes, no puede ser follow-up
        if len(conversation.messages) < 2:
            return False
        
        # Obtener los últimos mensajes del especialista
        recent_specialist_messages = []
        for msg in reversed(conversation.messages[-5:]):  # Últimos 5 mensajes
            if msg.sender == conversation.active_specialty:
                recent_specialist_messages.append(msg.content.lower())
                if len(recent_specialist_messages) >= 2:  # Solo necesitamos los últimos 2
                    break
        
        if not recent_specialist_messages:
            return False
        
        # Palabras clave que indican que el especialista está pidiendo información adicional
        follow_up_indicators = [
            "podrías describirme", "me gustaría preguntarte", "necesito que me des",
            "¿podrías", "¿has notado", "¿tienes", "¿existe", "¿hay algo",
            "más información", "más detalles", "cuéntame más", "dime si",
            "responde", "pregunta", "información adicional"
        ]
        
        # Verificar si el último mensaje del especialista contenía solicitud de información
        last_specialist_message = recent_specialist_messages[0]
        specialist_asking_for_info = any(indicator in last_specialist_message for indicator in follow_up_indicators)
        
        # Palabras clave que indican que el paciente está respondiendo/proporcionando información
        patient_response_indicators = [
            "es un dolor", "tengo", "siento", "me duele", "principalemnte", "principalmente",
            "no tengo", "sí", "no", "desde hace", "hace", "cuando", "al", "con",
            "irrada", "irradia", "hacia", "en", "también", "además", "pero",
            "vision borrosa", "visión", "trabajo", "pantalla", "nada mas", "nada más"
        ]
        
        message_lower = message.lower()
        patient_providing_info = any(indicator in message_lower for indicator in patient_response_indicators)
        
        # Es follow-up si:
        # 1. El especialista pidió información Y el paciente está respondiendo
        # 2. O si el mensaje es muy corto (típico de respuestas)
        is_short_response = len(message.split()) <= 10
        
        is_follow_up = (specialist_asking_for_info and patient_providing_info) or is_short_response
        
        if is_follow_up:
            logger.info(f"Detectado mensaje de seguimiento - evitando cambio de especialidad")
        
        return is_follow_up
    
    async def switch_specialty(self, conversation_id: str, new_specialty: str) -> Optional[str]:
        """Switch the specialty in a conversation."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            logger.error(f"Conversation {conversation_id} not found")
            return None
        
        try:
            # Switch specialty
            old_specialty = conversation.active_specialty
            conversation.switch_specialty(new_specialty)
            
            # Create a summary of the conversation for context
            context = {
                "conversation_history": [msg.dict() for msg in conversation.messages],
                "previous_specialty": old_specialty,
                "manual_transfer": True  # Indicar que fue un cambio manual
            }
            
            # Generate a transition response using advanced system
            query = f"Este paciente estaba hablando con un especialista en {old_specialty} y ahora quiere hablar contigo. " \
                   f"Por favor, revisa la conversación anterior y preséntate como especialista en {new_specialty}."
            
            agent_message = await self._process_with_advanced_system(
                query=query,
                specialty=new_specialty,
                context=context
            )
            
            # Add the transition message
            system_message = f"Cambiando de especialista de {old_specialty} a {new_specialty} por solicitud del usuario..."
            conversation.add_message(content=system_message, sender="system")
            
            # Add the new specialist's greeting
            conversation.add_message(content=agent_message, sender=new_specialty)
            
            # Save the updated conversation
            self._save_conversation(conversation_id)
            
            return agent_message
            
        except Exception as e:
            logger.error(f"Error switching specialty in conversation {conversation_id}: {e}")
            error_message = "Lo siento, ha ocurrido un error al cambiar de especialista. Por favor, inténtalo de nuevo."
            conversation.add_message(content=error_message, sender="system")
            return error_message 
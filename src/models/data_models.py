from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union, Any
from datetime import datetime


class UserQuery(BaseModel):
    """Model representing a user query to the medical system."""
    query: str = Field(..., description="The medical question or description from the user")
    specialty: Optional[str] = Field(None, description="The specific medical specialty to target, if known")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the query")
    conversation_id: Optional[str] = Field(None, description="ID of the conversation this query belongs to")
    
    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        # Convert any binary data to strings
        for key, value in data.items():
            if isinstance(value, bytes):
                data[key] = value.decode('utf-8', errors='replace')
            elif isinstance(value, dict):
                # Recursively handle dictionaries
                data[key] = self._handle_dict_serialization(value)
            elif isinstance(value, list):
                # Recursively handle lists
                data[key] = self._handle_list_serialization(value)
        return data
    
    def _handle_dict_serialization(self, d):
        """Recursively handle dictionary serialization."""
        result = {}
        for k, v in d.items():
            if isinstance(v, bytes):
                result[k] = v.decode('utf-8', errors='replace')
            elif isinstance(v, dict):
                result[k] = self._handle_dict_serialization(v)
            elif isinstance(v, list):
                result[k] = self._handle_list_serialization(v)
            else:
                result[k] = v
        return result
    
    def _handle_list_serialization(self, lst):
        """Recursively handle list serialization."""
        result = []
        for item in lst:
            if isinstance(item, bytes):
                result.append(item.decode('utf-8', errors='replace'))
            elif isinstance(item, dict):
                result.append(self._handle_dict_serialization(item))
            elif isinstance(item, list):
                result.append(self._handle_list_serialization(item))
            else:
                result.append(item)
        return result


class SpecialtyRecommendation(BaseModel):
    """Model representing the recommendation for which specialty to handle a query."""
    recommended_specialty: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    alternative_specialties: List[str] = []


class AgentResponse(BaseModel):
    """Model representing a response from a specific medical agent."""
    specialty: str
    response: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    sources: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None


class ConsensusResponse(BaseModel):
    """Model representing the final consensus response with contributions from multiple agents."""
    primary_specialty: str
    primary_response: str
    contributing_specialties: List[str] = []
    additional_insights: Dict[str, str] = {}
    created_at: datetime = Field(default_factory=datetime.now)
    patient_recommendations: List[str] = []
    
    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        # Convert any binary data to strings
        for key, value in data.items():
            if isinstance(value, bytes):
                data[key] = value.decode('utf-8', errors='replace')
            elif isinstance(value, dict):
                # Recursively handle dictionaries
                data[key] = self._handle_dict_serialization(value)
            elif isinstance(value, list):
                # Recursively handle lists
                data[key] = self._handle_list_serialization(value)
        return data
    
    def _handle_dict_serialization(self, d):
        """Recursively handle dictionary serialization."""
        result = {}
        for k, v in d.items():
            if isinstance(v, bytes):
                result[k] = v.decode('utf-8', errors='replace')
            elif isinstance(v, dict):
                result[k] = self._handle_dict_serialization(v)
            elif isinstance(v, list):
                result[k] = self._handle_list_serialization(v)
            else:
                result[k] = v
        return result
    
    def _handle_list_serialization(self, lst):
        """Recursively handle list serialization."""
        result = []
        for item in lst:
            if isinstance(item, bytes):
                result.append(item.decode('utf-8', errors='replace'))
            elif isinstance(item, dict):
                result.append(self._handle_dict_serialization(item))
            elif isinstance(item, list):
                result.append(self._handle_list_serialization(item))
            else:
                result.append(item)
        return result


class MessageType(BaseModel):
    """Model representing a message in a conversation."""
    content: str
    sender: str  # 'user', 'system', or a specialty name like 'cardiology'
    timestamp: datetime = Field(default_factory=datetime.now)
    
    def dict(self, **kwargs):
        """Custom dict method to handle datetime serialization."""
        data = super().dict(**kwargs)
        data['timestamp'] = data['timestamp'].isoformat()
        # Ensure string data is not binary
        if isinstance(data['content'], bytes):
            data['content'] = data['content'].decode('utf-8', errors='replace')
        if isinstance(data['sender'], bytes):
            data['sender'] = data['sender'].decode('utf-8', errors='replace')
        return data


class InteractiveConversation(BaseModel):
    """Model representing an interactive conversation with specialists."""
    conversation_id: str
    messages: List[MessageType] = []
    active_specialty: str  # The current specialty the user is talking to
    all_specialties: List[str] = []  # All specialties that have contributed
    context: Dict[str, Any] = {}  # Additional context for the conversation
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def add_message(self, content: str, sender: str) -> None:
        """Add a new message to the conversation."""
        self.messages.append(MessageType(content=content, sender=sender))
        self.updated_at = datetime.now()
        
        # Update specialties if necessary
        if sender not in ['user', 'system'] and sender not in self.all_specialties:
            self.all_specialties.append(sender)
            
    def switch_specialty(self, new_specialty: str) -> None:
        """Switch the active specialty."""
        if new_specialty not in self.all_specialties:
            self.all_specialties.append(new_specialty)
        self.active_specialty = new_specialty
        self.updated_at = datetime.now()
    
    def dict(self, **kwargs):
        """Custom dict method to handle datetime serialization."""
        data = super().dict(**kwargs)
        # Convert datetime to string
        data['created_at'] = data['created_at'].isoformat()
        data['updated_at'] = data['updated_at'].isoformat()
        
        # Ensure conversation_id is string, not bytes
        if isinstance(data['conversation_id'], bytes):
            data['conversation_id'] = data['conversation_id'].decode('utf-8', errors='replace')
        
        # Ensure active_specialty is string, not bytes
        if isinstance(data['active_specialty'], bytes):
            data['active_specialty'] = data['active_specialty'].decode('utf-8', errors='replace')
        
        # Ensure all_specialties are strings, not bytes
        for i, spec in enumerate(data['all_specialties']):
            if isinstance(spec, bytes):
                data['all_specialties'][i] = spec.decode('utf-8', errors='replace')
        
        # Handle any binary data in context
        data['context'] = self._handle_dict_serialization(data['context'])
        
        return data
    
    def _handle_dict_serialization(self, d):
        """Recursively handle dictionary serialization."""
        result = {}
        for k, v in d.items():
            if isinstance(v, bytes):
                result[k] = v.decode('utf-8', errors='replace')
            elif isinstance(v, dict):
                result[k] = self._handle_dict_serialization(v)
            elif isinstance(v, list):
                result[k] = self._handle_list_serialization(v)
            else:
                result[k] = v
        return result
    
    def _handle_list_serialization(self, lst):
        """Recursively handle list serialization."""
        result = []
        for item in lst:
            if isinstance(item, bytes):
                result.append(item.decode('utf-8', errors='replace'))
            elif isinstance(item, dict):
                result.append(self._handle_dict_serialization(item))
            elif isinstance(item, list):
                result.append(self._handle_list_serialization(item))
            else:
                result.append(item)
        return result


class ConversationHistory(BaseModel):
    """Model representing the history of a conversation."""
    conversation_id: str
    queries: List[UserQuery] = []
    responses: List[ConsensusResponse] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def dict(self, **kwargs):
        """Custom dict method to handle datetime serialization."""
        data = super().dict(**kwargs)
        # Convert datetime to string
        data['created_at'] = data['created_at'].isoformat()
        data['updated_at'] = data['updated_at'].isoformat()
        
        # Ensure conversation_id is string
        if isinstance(data['conversation_id'], bytes):
            data['conversation_id'] = data['conversation_id'].decode('utf-8', errors='replace')
            
        return data 
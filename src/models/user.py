import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, username, password=None, user_id=None, created_at=None):
        self.user_id = user_id or str(uuid.uuid4())
        self.username = username
        self.password_hash = generate_password_hash(password) if password else None
        self.created_at = created_at or datetime.utcnow()
    
    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user object to dictionary."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'password_hash': self.password_hash,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create a user object from dictionary data."""
        user = cls(
            username=data.get('username'),
            user_id=data.get('user_id'),
            created_at=data.get('created_at')
        )
        user.password_hash = data.get('password_hash')
        return user 
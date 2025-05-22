import json
import os
import logging
from datetime import datetime
from src.models.user import User

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, 'users.json')
        self._ensure_data_directory()
        self._load_users()
    
    def _ensure_data_directory(self):
        """Ensure that the data directory exists."""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _load_users(self):
        """Load users from the JSON file."""
        self.users = {}
        
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    users_data = json.load(f)
                    
                for user_id, user_data in users_data.items():
                    # Handle datetime conversion
                    if isinstance(user_data.get('created_at'), str):
                        user_data['created_at'] = datetime.fromisoformat(user_data['created_at'])
                    
                    self.users[user_id] = User.from_dict(user_data)
                
                logger.info(f"Loaded {len(self.users)} users from {self.users_file}")
            except Exception as e:
                logger.error(f"Error loading users: {e}")
                self.users = {}
    
    def _save_users(self):
        """Save users to the JSON file."""
        try:
            users_data = {}
            
            for user_id, user in self.users.items():
                user_dict = user.to_dict()
                # Convert datetime to string for JSON serialization
                if isinstance(user_dict.get('created_at'), datetime):
                    user_dict['created_at'] = user_dict['created_at'].isoformat()
                
                users_data[user_id] = user_dict
            
            with open(self.users_file, 'w') as f:
                json.dump(users_data, f, indent=2)
            
            logger.info(f"Saved {len(self.users)} users to {self.users_file}")
        except Exception as e:
            logger.error(f"Error saving users: {e}")
    
    def create_user(self, username, password):
        """Create a new user."""
        # Check if username already exists
        if self.get_user_by_username(username):
            logger.warning(f"Username '{username}' already exists")
            return None
        
        # Create new user
        user = User(username=username, password=password)
        self.users[user.user_id] = user
        self._save_users()
        
        logger.info(f"Created new user: {username}")
        return user
    
    def get_user(self, user_id):
        """Get a user by ID."""
        return self.users.get(user_id)
    
    def get_user_by_username(self, username):
        """Get a user by username."""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    def authenticate(self, username, password):
        """Authenticate a user with username and password."""
        user = self.get_user_by_username(username)
        
        if user and user.check_password(password):
            logger.info(f"User authenticated: {username}")
            return user
        
        logger.warning(f"Authentication failed for user: {username}")
        return None
    
    def update_user(self, user):
        """Update a user."""
        if user.user_id in self.users:
            self.users[user.user_id] = user
            self._save_users()
            logger.info(f"Updated user: {user.username}")
            return True
        
        logger.warning(f"User not found for update: {user.user_id}")
        return False
    
    def delete_user(self, user_id):
        """Delete a user."""
        if user_id in self.users:
            username = self.users[user_id].username
            del self.users[user_id]
            self._save_users()
            logger.info(f"Deleted user: {username}")
            return True
        
        logger.warning(f"User not found for deletion: {user_id}")
        return False 
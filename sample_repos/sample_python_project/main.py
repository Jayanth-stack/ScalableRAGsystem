"""
Sample Python project for testing Code Documentation Assistant.

This module demonstrates various Python constructs including classes,
functions, decorators, and different types of documentation.
"""

import os
import json
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass
class User:
    """Represents a user in the system.
    
    Attributes:
        id: Unique identifier for the user
        name: Full name of the user
        email: Email address
        is_active: Whether the user account is active
    """
    id: int
    name: str
    email: str
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Union[int, str, bool]]:
        """Convert user to dictionary representation.
        
        Returns:
            Dictionary containing user data
        """
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "is_active": self.is_active
        }


class DatabaseInterface(ABC):
    """Abstract interface for database operations."""
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish database connection."""
        pass
    
    @abstractmethod
    def save_user(self, user: User) -> bool:
        """Save user to database."""
        pass
    
    @abstractmethod
    def get_user(self, user_id: int) -> Optional[User]:
        """Retrieve user by ID."""
        pass


class UserManager:
    """Manages user operations and database interactions.
    
    This class provides a high-level interface for user management,
    including creation, retrieval, and validation operations.
    """
    
    def __init__(self, database: DatabaseInterface):
        """Initialize UserManager with database interface.
        
        Args:
            database: Database interface implementation
        """
        self.database = database
        self._users_cache: Dict[int, User] = {}
    
    def create_user(self, name: str, email: str) -> Optional[User]:
        """Create a new user with validation.
        
        Args:
            name: User's full name
            email: User's email address
            
        Returns:
            Created User object if successful, None otherwise
            
        Raises:
            ValueError: If name or email is invalid
        """
        if not self._validate_email(email):
            raise ValueError(f"Invalid email format: {email}")
        
        if not name.strip():
            raise ValueError("Name cannot be empty")
        
        # Generate new user ID (simplified)
        user_id = len(self._users_cache) + 1
        
        user = User(
            id=user_id,
            name=name.strip(),
            email=email.lower(),
            is_active=True
        )
        
        if self.database.save_user(user):
            self._users_cache[user_id] = user
            return user
        
        return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Retrieve user by ID with caching.
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            User object if found, None otherwise
        """
        # Check cache first
        if user_id in self._users_cache:
            return self._users_cache[user_id]
        
        # Fetch from database
        user = self.database.get_user(user_id)
        if user:
            self._users_cache[user_id] = user
        
        return user
    
    def get_active_users(self) -> List[User]:
        """Get all active users.
        
        Returns:
            List of active User objects
        """
        return [user for user in self._users_cache.values() if user.is_active]
    
    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user account.
        
        Args:
            user_id: ID of user to deactivate
            
        Returns:
            True if successful, False otherwise
        """
        user = self.get_user_by_id(user_id)
        if user:
            user.is_active = False
            return self.database.save_user(user)
        return False
    
    @staticmethod
    def _validate_email(email: str) -> bool:
        """Validate email format (simplified).
        
        Args:
            email: Email address to validate
            
        Returns:
            True if email format is valid
        """
        return "@" in email and "." in email.split("@")[1]
    
    def export_users_to_json(self, filepath: str) -> bool:
        """Export all users to JSON file.
        
        Args:
            filepath: Path to output JSON file
            
        Returns:
            True if export successful, False otherwise
        """
        try:
            users_data = [user.to_dict() for user in self._users_cache.values()]
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, indent=2)
            
            return True
        except (IOError, OSError) as e:
            print(f"Error exporting users: {e}")
            return False


def calculate_user_statistics(users: List[User]) -> Dict[str, Union[int, float]]:
    """Calculate statistics for a list of users.
    
    Args:
        users: List of User objects
        
    Returns:
        Dictionary containing user statistics
    """
    if not users:
        return {"total": 0, "active": 0, "inactive": 0, "active_percentage": 0.0}
    
    total_users = len(users)
    active_users = sum(1 for user in users if user.is_active)
    inactive_users = total_users - active_users
    active_percentage = (active_users / total_users) * 100
    
    return {
        "total": total_users,
        "active": active_users,
        "inactive": inactive_users,
        "active_percentage": round(active_percentage, 2)
    }


# Configuration constants
DEFAULT_CONFIG = {
    "max_users": 1000,
    "cache_size": 100,
    "session_timeout": 3600
}

# Example usage
if __name__ == "__main__":
    # This would normally use a real database implementation
    from typing import TYPE_CHECKING
    
    if TYPE_CHECKING:
        # Mock database for demonstration
        class MockDatabase(DatabaseInterface):
            def __init__(self):
                self.users: Dict[int, User] = {}
            
            def connect(self) -> bool:
                return True
            
            def save_user(self, user: User) -> bool:
                self.users[user.id] = user
                return True
            
            def get_user(self, user_id: int) -> Optional[User]:
                return self.users.get(user_id)
        
        # Demo usage
        db = MockDatabase()
        user_manager = UserManager(db)
        
        # Create some users
        user1 = user_manager.create_user("John Doe", "john@example.com")
        user2 = user_manager.create_user("Jane Smith", "jane@example.com")
        
        # Get statistics
        all_users = [user1, user2] if user1 and user2 else []
        stats = calculate_user_statistics(all_users)
        print(f"User statistics: {stats}") 
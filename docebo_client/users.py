"""
Users API module for Docebo
"""

import requests
from typing import Dict, Any, List, Optional
from .auth import DoceboAuth


class UsersAPI:
    """
    API client for Docebo users endpoints
    """
    
    def __init__(
        self,
        base_url: str,
        session: requests.Session,
        auth: DoceboAuth
    ):
        """
        Initialize the Users API
        
        Args:
            base_url (str): Base URL for the API
            session (requests.Session): HTTP session
            auth (DoceboAuth): Authentication handler
        """
        self.base_url = base_url
        self.session = session
        self.auth = auth
    
    def lookup_user(self, search_text: str) -> Dict[str, Any]:
        """
        Look up users by search text
        
        Based on: Lookup User.bru
        
        Args:
            search_text (str): Search text to find users (username, email, etc.)
        
        Returns:
            Dict: Response containing user search results
        """
        if not self.auth.refresh_if_needed():
            raise Exception("Authentication required")
        
        url = f"{self.base_url}/manage/v1/user"
        
        # Build the request body
        data = {
            "search_text": search_text
        }
        
        try:
            response = self.session.get(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to lookup user: {e}")
    
    def get_enrollments(
        self, 
        search_text: str, 
        enrollment_status: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get course enrollments for a user by searching for them first
        
        Args:
            search_text (str): Search text to find the user (username, email, etc.)
            enrollment_status (List[str], optional): Filter by enrollment status 
                (e.g., ["completed", "in_progress", "not_started"])
        
        Returns:
            Dict: Response containing course enrollments for the found user
            
        Raises:
            Exception: If user not found or multiple users found
        """
        # First, look up the user
        user_lookup = self.lookup_user(search_text)
        
        if 'data' not in user_lookup or 'items' not in user_lookup['data']:
            raise Exception(f"No users found for search text: {search_text}")
        
        users = user_lookup['data']['items']
        
        if len(users) == 0:
            raise Exception(f"No users found for search text: {search_text}")
        elif len(users) > 1:
            usernames = [user.get('username', 'Unknown') for user in users]
            raise Exception(f"Multiple users found for search text '{search_text}': {usernames}. Please be more specific.")
        
        # Get the user ID - try different possible field names
        user = users[0]
        user_id = user.get('user_id') or user.get('id_user') or user.get('id')
        
        if not user_id:
            available_keys = list(user.keys()) if user else []
            raise Exception(f"User found but no user ID available. Available keys: {available_keys}")
        
        # Convert to int to ensure proper type
        user_id = int(user_id)
        
        # Import here to avoid circular imports
        from .courses import CoursesAPI
        
        # Create a courses API instance to get enrollments
        courses_api = CoursesAPI(self.base_url, self.session, self.auth)
        
        return courses_api.get_enrollments_by_user_id(user_id, enrollment_status)
    
    def get_enrollments_by_user_id(self, user_id: str, enrollment_status: str = "completed") -> Dict[str, Any]:
        """
        Get course enrollments for a specific user
        
        Based on: Get Enrollments.bru
        
        Args:
            user_id (str): The ID of the user
            enrollment_status (str): Filter by enrollment status (default: "completed")
        
        Returns:
            Dict: Response containing user's course enrollments
        """
        if not self.auth.refresh_if_needed():
            raise Exception("Authentication required")
        
        url = f"{self.base_url}/course/v1/courses/enrollments"
        
        # Build the request body
        data = {
            "user_id": [user_id],
            "enrollment_status": [enrollment_status]
        }
        
        try:
            response = self.session.get(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get enrollments: {e}")
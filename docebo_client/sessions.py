"""
Sessions API module for Docebo
"""

import requests
from typing import Dict, Any
from .auth import DoceboAuth


class SessionsAPI:
    """
    API client for Docebo sessions endpoints
    """
    
    def __init__(
        self,
        base_url: str,
        session: requests.Session,
        auth: DoceboAuth
    ):
        """
        Initialize the Sessions API
        
        Args:
            base_url (str): Base URL for the API
            session (requests.Session): HTTP session
            auth (DoceboAuth): Authentication handler
        """
        self.base_url = base_url
        self.session = session
        self.auth = auth
    
    def get_session_roster(self, session_id: int) -> Dict[str, Any]:
        """
        Get the enrollment roster for a specific session
        
        Based on: Get Session Roster.bru
        
        Args:
            session_id (int): The ID of the session
        
        Returns:
            Dict: Response containing session enrollments
        """
        if not self.auth.refresh_if_needed():
            raise Exception("Authentication required")
        
        url = f"{self.base_url}/course/v1/sessions/{session_id}/enrollments"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get session roster: {e}")
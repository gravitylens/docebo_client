"""
Authentication module for Docebo API
"""

import os
import requests
from typing import Optional
from datetime import datetime, timedelta

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, environment variables should be set manually
    pass


class DoceboAuth:
    """
    Handles OAuth2 authentication for Docebo API
    """
    
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        base_url: Optional[str] = None,
        session: Optional[requests.Session] = None
    ):
        """
        Initialize authentication handler
        
        Args:
            client_id (str, optional): OAuth2 client ID. If not provided, loads from DOCEBO_CLIENT_ID env var
            client_secret (str, optional): OAuth2 client secret. If not provided, loads from DOCEBO_CLIENT_SECRET env var
            username (str, optional): Username for password grant. If not provided, loads from DOCEBO_USERNAME env var
            password (str, optional): Password for password grant. If not provided, loads from DOCEBO_PASSWORD env var
            base_url (str, optional): Base URL for the API. If not provided, loads from DOCEBO_BASE_URL env var
            session (requests.Session, optional): HTTP session to use
        """
        self.client_id = client_id or os.getenv('DOCEBO_CLIENT_ID')
        self.client_secret = client_secret or os.getenv('DOCEBO_CLIENT_SECRET')
        self.username = username or os.getenv('DOCEBO_USERNAME')
        self.password = password or os.getenv('DOCEBO_PASSWORD')
        self.base_url = base_url or os.getenv('DOCEBO_BASE_URL', '')
        self.session = session or requests.Session()
        
        if not self.client_id or not self.client_secret:
            raise ValueError("client_id and client_secret are required. Provide them as parameters or set DOCEBO_CLIENT_ID and DOCEBO_CLIENT_SECRET environment variables.")
        
        self.access_token: Optional[str] = None
        self.token_expires_at: Optional[datetime] = None
    
    def authenticate(self) -> bool:
        """
        Authenticate using OAuth2 password grant
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        if not self.username or not self.password:
            raise ValueError("Username and password are required for authentication")
        
        url = f"{self.base_url}/oauth2/token"
        
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "password",
            "scope": "api",
            "username": self.username,
            "password": self.password
        }
        
        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            
            # Calculate token expiration (default to 1 hour if not provided)
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            # Set authorization header for future requests
            if self.access_token:
                self.session.headers.update({
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                })
                return True
            
        except requests.exceptions.RequestException as e:
            print(f"Authentication failed: {e}")
            
        return False
    
    def is_authenticated(self) -> bool:
        """
        Check if currently authenticated and token is not expired
        
        Returns:
            bool: True if authenticated and token valid, False otherwise
        """
        if not self.access_token:
            return False
        
        if self.token_expires_at and datetime.now() >= self.token_expires_at:
            return False
        
        return True
    
    def get_access_token(self) -> Optional[str]:
        """
        Get the current access token
        
        Returns:
            str: The access token, or None if not authenticated
        """
        if self.is_authenticated():
            return self.access_token
        return None
    
    def refresh_if_needed(self) -> bool:
        """
        Refresh the token if it's expired or about to expire
        
        Returns:
            bool: True if token is valid or successfully refreshed, False otherwise
        """
        if not self.is_authenticated():
            return self.authenticate()
        return True
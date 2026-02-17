"""
Main client class for the Docebo API Library
"""

import os
import requests
from typing import Optional
from .auth import DoceboAuth
from .courses import CoursesAPI
from .sessions import SessionsAPI

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, environment variables should be set manually
    pass


class DoceboClient:
    """
    Main client for interacting with Docebo APIs
    """
    
    def __init__(
        self, 
        base_url: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Initialize the Docebo client
        
        Args:
            base_url (str, optional): The base URL for the Docebo instance. If not provided, loads from DOCEBO_BASE_URL env var
            client_id (str, optional): OAuth2 client ID. If not provided, loads from DOCEBO_CLIENT_ID env var
            client_secret (str, optional): OAuth2 client secret. If not provided, loads from DOCEBO_CLIENT_SECRET env var
            username (str, optional): Username for password grant. If not provided, loads from DOCEBO_USERNAME env var
            password (str, optional): Password for password grant. If not provided, loads from DOCEBO_PASSWORD env var
        """
        self.base_url = (base_url or os.getenv('DOCEBO_BASE_URL', '')).rstrip('/')
        self.session = requests.Session()
        
        # Initialize authentication
        self.auth = DoceboAuth(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            base_url=self.base_url,
            session=self.session
        )
        
        # Initialize API modules
        self.courses = CoursesAPI(self.base_url, self.session, self.auth)
        self.sessions = SessionsAPI(self.base_url, self.session, self.auth)
    
    def authenticate(self) -> bool:
        """
        Authenticate with the Docebo API
        
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        return self.auth.authenticate()
    
    def is_authenticated(self) -> bool:
        """
        Check if the client is currently authenticated
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        return self.auth.is_authenticated()
    
    def get_access_token(self) -> Optional[str]:
        """
        Get the current access token
        
        Returns:
            str: The access token, or None if not authenticated
        """
        return self.auth.get_access_token()
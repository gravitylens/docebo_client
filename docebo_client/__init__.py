"""
Docebo API Python Client Library

A Python library for interacting with the Docebo e-learning platform APIs.
"""

from .client import DoceboClient
from .auth import DoceboAuth
from .courses import CoursesAPI
from .sessions import SessionsAPI
from .users import UsersAPI

__version__ = "1.0.0"
__author__ = "Generated from Bruno API Collection"

__all__ = [
    "DoceboClient",
    "DoceboAuth", 
    "CoursesAPI",
    "SessionsAPI",
    "UsersAPI"
]
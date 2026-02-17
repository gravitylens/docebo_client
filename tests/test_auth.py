#!/usr/bin/env python3
"""
Test script for Docebo API authentication
"""

import sys
import os
from datetime import datetime

# Add the parent directory to Python path so we can import our package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from docebo_client import DoceboClient, DoceboAuth


def test_auth_direct():
    """Test authentication using DoceboAuth directly"""
    print("=" * 60)
    print("Testing DoceboAuth directly...")
    print("=" * 60)
    
    try:
        # Create auth instance (will load from .env)
        auth = DoceboAuth()
        
        print(f"Base URL: {auth.base_url}")
        print(f"Client ID: {auth.client_id}")
        print(f"Username: {auth.username}")
        print("Client Secret: [HIDDEN]")
        print("Password: [HIDDEN]")
        print()
        
        # Test authentication
        print("Attempting to authenticate...")
        success = auth.authenticate()
        
        if success:
            print("✅ Authentication successful!")
            print(f"Access Token: {auth.access_token[:20]}..." if auth.access_token else "No token received")
            print(f"Token expires at: {auth.token_expires_at}")
            
            # Test token validation
            if docebo_auth.is_authenticated():
                print("✅ Token is valid")
            else:
                print("❌ Token is invalid or expired")
                
        else:
            print("❌ Authentication failed!")
            
    except Exception as e:
        print(f"❌ Error during authentication: {e}")
        
    return success


def test_client():
    """Test authentication using DoceboClient"""
    print("\n" + "=" * 60)
    print("Testing DoceboClient...")
    print("=" * 60)
    
    try:
        # Create client instance (will load from .env)
        client = DoceboClient()
        
        print(f"Base URL: {client.base_url}")
        print(f"Client ID: {client.auth.client_id}")
        print(f"Username: {client.auth.username}")
        print("Client Secret: [HIDDEN]")
        print("Password: [HIDDEN]")
        print()
        
        # Test authentication through client
        print("Attempting to authenticate via client...")
        success = client.auth.authenticate()
        
        if success:
            print("✅ Client authentication successful!")
            print(f"Access Token: {client.auth.access_token[:20]}..." if client.auth.access_token else "No token received")
            
            # Test if we can make API calls (this would require actual API endpoints)
            print("✅ Client is ready for API calls")
            
        else:
            print("❌ Client authentication failed!")
            
    except Exception as e:
        print(f"❌ Error during client test: {e}")
        
    return success


def test_environment_variables():
    """Test that environment variables are loaded correctly"""
    print("\n" + "=" * 60)
    print("Testing Environment Variables...")
    print("=" * 60)
    
    required_vars = [
        'DOCEBO_BASE_URL',
        'DOCEBO_CLIENT_ID', 
        'DOCEBO_CLIENT_SECRET',
        'DOCEBO_USERNAME',
        'DOCEBO_PASSWORD'
    ]
    
    all_present = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if 'SECRET' in var or 'PASSWORD' in var:
                print(f"✅ {var}: [HIDDEN]")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")
            all_present = False
            
    return all_present


def main():
    """Run all tests"""
    print("Docebo API Authentication Test")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Test environment variables
    env_success = test_environment_variables()
    
    if not env_success:
        print("\n❌ Environment variables not properly set. Please check your .env file.")
        return False
    
    # Test direct auth
    auth_success = test_auth_direct()
    
    # Test client
    client_success = test_client()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Environment Variables: {'✅ PASS' if env_success else '❌ FAIL'}")
    print(f"Direct Authentication: {'✅ PASS' if auth_success else '❌ FAIL'}")
    print(f"Client Authentication: {'✅ PASS' if client_success else '❌ FAIL'}")
    
    overall_success = env_success and auth_success and client_success
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
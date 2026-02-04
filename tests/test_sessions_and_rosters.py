#!/usr/bin/env python3
"""
Test script that chains get_course_sessions_by_date and get_session_roster
"""

import sys
import os
from datetime import datetime

# Add the parent directory to Python path so we can import our package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from docebo_client import DoceboClient


def test_sessions_and_rosters():
    """Test chaining get_course_sessions_by_date with get_session_roster"""
    print("=" * 70)
    print("Testing get_course_sessions_by_date + get_session_roster chain...")
    print("=" * 70)
    
    course_id = 563
    date_from = "2026-02-03"
    date_to = "2026-02-03"
    
    try:
        # Create client instance (will load from .env)
        client = DoceboClient()
        
        print(f"Connected to: {client.base_url}")
        print(f"Step 1: Getting sessions for course ID: {course_id}")
        print(f"        Date range: {date_from} to {date_to}")
        print()
        
        # Step 1: Get course sessions by date
        sessions_response = client.courses.get_course_sessions_by_date(
            course_id=course_id, 
            date_from=date_from, 
            date_to=date_to
        )
        
        if 'data' in sessions_response and 'sessions' in sessions_response['data']:
            sessions = sessions_response['data']['sessions']
            print(f"Found {len(sessions)} sessions:")
            print()
            
            if len(sessions) == 0:
                print("No sessions found for this date range.")
                return True
            
            # Step 2: For each session, get the roster
            for i, session in enumerate(sessions, 1):
                session_name = session.get('name', 'No name available')
                session_id = session.get('id_session')
                
                print(f"{i:2d}. Session: {session_name}")
                print(f"    ID: {session_id}")
                
                if session_id:
                    try:
                        # Get roster for this session
                        roster_response = client.sessions.get_session_roster(session_id)
                        
                        print(f"    Roster response keys: {list(roster_response.keys())}")
                        
                        # Look for enrollments in the response
                        if 'data' in roster_response and 'items' in roster_response['data']:
                            items = roster_response['data']['items']
                            print(f"    Found {len(items)} enrollments in data.items:")
                            
                            if len(items) == 0:
                                print("      No enrollments found for this session.")
                            else:
                                # Display email from each enrollment
                                for j, item in enumerate(items, 1):
                                    email = item.get('email', 'No email available')
                                    firstname = item.get('firstname', '')
                                    lastname = item.get('lastname', '')
                                    name = f"{firstname} {lastname}".strip() or 'No name'
                                    
                                    print(f"      {j:3d}. {email} ({name})")
                                    
                        elif 'items' in roster_response:
                            items = roster_response['items']
                            print(f"    Found {len(items)} enrollments in items:")
                            
                            for j, item in enumerate(items, 1):
                                email = item.get('email', 'No email available')
                                print(f"      {j:3d}. {email}")
                                
                        elif 'data' in roster_response:
                            print(f"    Unexpected roster structure in 'data': {type(roster_response['data'])}")
                            print(f"    Data content: {roster_response['data']}")
                        else:
                            print(f"    Unexpected roster response structure: {list(roster_response.keys())}")
                            
                    except Exception as roster_error:
                        print(f"    ❌ Error getting roster: {roster_error}")
                        
                else:
                    print("    ❌ No session ID found, cannot get roster")
                    
                print()  # Empty line between sessions
                
        else:
            print("Unexpected sessions response structure.")
            print(f"Response keys: {list(sessions_response.keys())}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_broader_date_sessions_and_rosters():
    """Test with broader date range to find more sessions"""
    print("\n" + "=" * 70)
    print("Testing broader date range (limited to first 3 sessions)...")
    print("=" * 70)
    
    course_id = 563
    date_from = "2026-01-01"
    date_to = "2026-03-31"
    
    try:
        client = DoceboClient()
        
        print(f"Step 1: Getting sessions for course ID: {course_id}")
        print(f"        Date range: {date_from} to {date_to} (showing first 3)")
        print()
        
        # Get sessions in broader date range
        sessions_response = client.courses.get_course_sessions_by_date(
            course_id=course_id, 
            date_from=date_from, 
            date_to=date_to
        )
        
        if 'data' in sessions_response and 'sessions' in sessions_response['data']:
            sessions = sessions_response['data']['sessions']
            print(f"Found {len(sessions)} total sessions, checking first 3:")
            print()
            
            # Limit to first 3 sessions to avoid too much output
            for i, session in enumerate(sessions[:3], 1):
                session_name = session.get('name', 'No name available')
                session_id = session.get('id_session')
                
                print(f"{i}. Session: {session_name}")
                print(f"   ID: {session_id}")
                
                if session_id:
                    try:
                        roster_response = client.sessions.get_session_roster(session_id)
                        
                        if 'data' in roster_response and 'items' in roster_response['data']:
                            items = roster_response['data']['items']
                            print(f"   Enrollments: {len(items)} found")
                            
                            # Show first few emails if any
                            for j, item in enumerate(items[:3], 1):
                                email = item.get('email', 'No email')
                                print(f"     {j}. {email}")
                                
                            if len(items) > 3:
                                print(f"     ... and {len(items) - 3} more")
                        else:
                            print(f"   No items found in roster response")
                            
                    except Exception as roster_error:
                        print(f"   ❌ Error getting roster: {roster_error}")
                else:
                    print("   ❌ No session ID")
                    
                print()
                
        return True
        
    except Exception as e:
        print(f"❌ Error during broader test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("Docebo Sessions and Rosters Chain Test")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Run tests
    test1_success = test_sessions_and_rosters()
    test2_success = test_broader_date_sessions_and_rosters()
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Specific date sessions + rosters: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"Broader date sessions + rosters: {'✅ PASS' if test2_success else '❌ FAIL'}")
    
    overall_success = test1_success and test2_success
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
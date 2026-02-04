#!/usr/bin/env python3
"""
Test script for get_course_sessions_by_date method
"""

import sys
import os
from datetime import datetime

# Add the parent directory to Python path so we can import our package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from docebo_client import DoceboClient


def test_get_course_sessions_by_date():
    """Test get_course_sessions_by_date method with specific parameters"""
    print("=" * 60)
    print("Testing get_course_sessions_by_date...")
    print("=" * 60)
    
    course_id = 563
    date_from = "2026-02-03"
    date_to = "2026-02-03"
    
    try:
        # Create client instance (will load from .env)
        client = DoceboClient()
        
        print(f"Connected to: {client.base_url}")
        print(f"Fetching sessions for course ID: {course_id}")
        print(f"Date range: {date_from} to {date_to}")
        print()
        
        # Get course sessions by date
        response = client.courses.get_course_sessions_by_date(
            course_id=course_id, 
            date_from=date_from, 
            date_to=date_to
        )
        
        print(f"Response keys: {list(response.keys())}")
        print()
        
        # Check response structure and display sessions
        if 'data' in response and 'sessions' in response['data']:
            sessions = response['data']['sessions']
            print(f"Found {len(sessions)} sessions in 'data.sessions' array:")
            print()
            
            if len(sessions) == 0:
                print("No sessions found for this date range.")
            else:
                # Display each session with name and dates
                for i, session in enumerate(sessions, 1):
                    name = session.get('name', 'No name available')
                    print(f"{i:3d}. Session: {name}")
                    
                    # Display dates array
                    dates = session.get('dates', [])
                    if dates:
                        print(f"      Days ({len(dates)} total):")
                        for j, date_info in enumerate(dates, 1):
                            day = date_info.get('day', 'N/A')
                            day_name = date_info.get('name', '')
                            time_begin = date_info.get('time_begin', 'N/A')
                            time_end = date_info.get('time_end', 'N/A')
                            timezone = date_info.get('timezone', 'N/A')
                            
                            print(f"        {j}. Day: {day}")
                            if day_name:
                                print(f"           Name: {day_name}")
                            print(f"           Time: {time_begin} - {time_end} ({timezone})")
                    else:
                        print("      No dates information available")
                    print()
                        
        elif 'sessions' in response:
            sessions = response['sessions']
            print(f"Found {len(sessions)} sessions in 'sessions' array:")
            print()
            
            for i, session in enumerate(sessions, 1):
                name = session.get('name', 'No name available')
                print(f"{i:3d}. Session: {name}")
                
                dates = session.get('dates', [])
                if dates:
                    print(f"      Days:")
                    for date_info in dates:
                        day = date_info.get('day', 'N/A')
                        print(f"        - {day}")
                print()
                
        elif 'data' in response:
            data = response['data']
            print("'data' field structure:")
            print(data)
        else:
            print("Unexpected response structure. Full response:")
            print(response)
            
        # Show pagination info if available
        print()
        print("Additional response info:")
        data_section = response.get('data', {}) if 'data' in response else response
        for key in ['success', 'total_count', 'count', 'has_more_data']:
            if key in data_section:
                print(f"  {key}: {data_section[key]}")
                
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_get_course_sessions_by_date_broader():
    """Test get_course_sessions_by_date method with a broader date range"""
    print("\n" + "=" * 60)
    print("Testing get_course_sessions_by_date with broader range...")
    print("=" * 60)
    
    course_id = 563
    date_from = "2026-01-01"
    date_to = "2026-03-31"
    
    try:
        client = DoceboClient()
        
        print(f"Fetching sessions for course ID: {course_id}")
        print(f"Date range: {date_from} to {date_to}")
        print()
        
        # Get sessions in broader date range
        response = client.courses.get_course_sessions_by_date(
            course_id=course_id, 
            date_from=date_from, 
            date_to=date_to
        )
        
        print(f"Response keys: {list(response.keys())}")
        print()
        
        if 'data' in response and 'sessions' in response['data']:
            sessions = response['data']['sessions']
            print(f"Found {len(sessions)} sessions in broader date range:")
            print()
            
            if len(sessions) == 0:
                print("No sessions found for this date range.")
            else:
                # Display just names and first day for each session
                for i, session in enumerate(sessions, 1):
                    name = session.get('name', 'No name available')
                    dates = session.get('dates', [])
                    first_day = dates[0].get('day', 'N/A') if dates else 'N/A'
                    
                    print(f"{i:3d}. {name}")
                    print(f"      First day: {first_day}")
                    print()
                
        return True
        
    except Exception as e:
        print(f"❌ Error during broader test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("Docebo Course Sessions by Date API Test")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Run tests
    test1_success = test_get_course_sessions_by_date()
    test2_success = test_get_course_sessions_by_date_broader()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Specific date test: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"Broader date range test: {'✅ PASS' if test2_success else '❌ FAIL'}")
    
    overall_success = test1_success and test2_success
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
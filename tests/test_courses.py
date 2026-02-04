#!/usr/bin/env python3
"""
Test script for get_all_courses method
"""

import sys
import os
from datetime import datetime

# Add the parent directory to Python path so we can import our package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from docebo_client import DoceboClient


def test_get_all_courses():
    """Test get_all_courses method and display course information"""
    print("=" * 60)
    print("Testing get_all_courses...")
    print("=" * 60)
    
    try:
        # Create client instance (will load from .env)
        client = DoceboClient()
        
        print(f"Connected to: {client.base_url}")
        print("Fetching courses...")
        print()
        
        # Get first page of courses
        response = client.courses.get_all_courses()
        
        print(f"Response keys: {list(response.keys())}")
        print()
        
        # Check if response has 'items' array
        if 'data' in response and 'items' in response['data']:
            items = response['data']['items']
            print(f"Found {len(items)} courses in 'data.items' array:")
            print()
            
            # Display each course
            for i, course in enumerate(items, 1):
                id_course = course.get('id_course', 'N/A')
                name = course.get('name', 'No name available')
                print(f"{i:3d}. ID: {id_course:<8} | Name: {name}")
                
        elif 'items' in response:
            items = response['items']
            print(f"Found {len(items)} courses in 'items' array:")
            print()
            
            # Display each course
            for i, course in enumerate(items, 1):
                id_course = course.get('id_course', 'N/A')
                name = course.get('name', 'No name available')
                print(f"{i:3d}. ID: {id_course:<8} | Name: {name}")
                
        elif 'data' in response:
            # Alternative structure - some APIs use 'data' as direct list
            data = response['data']
            if isinstance(data, list):
                print(f"Found {len(data)} courses in 'data' array:")
                print()
                
                for i, course in enumerate(data, 1):
                    id_course = course.get('id_course', 'N/A')
                    name = course.get('name', 'No name available')
                    print(f"{i:3d}. ID: {id_course:<8} | Name: {name}")
            else:
                print("'data' field is not a list. Structure:")
                print(data)
                
        elif isinstance(response, list):
            # Direct list response
            print(f"Found {len(response)} courses in direct list:")
            print()
            
            for i, course in enumerate(response, 1):
                id_course = course.get('id_course', 'N/A')
                name = course.get('name', 'No name available')
                print(f"{i:3d}. ID: {id_course:<8} | Name: {name}")
                
        else:
            print("Unexpected response structure. Full response:")
            print(response)
            
        # Show pagination info if available
        print()
        print("Pagination info:")
        for key in ['total_count', 'total_pages', 'current_page', 'page_size', 'has_more_page']:
            if key in response:
                print(f"  {key}: {response[key]}")
                
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False


def test_get_all_courses_paginated():
    """Test get_all_courses with automatic pagination"""
    print("\n" + "=" * 60)
    print("Testing get_all_courses with auto-pagination...")
    print("=" * 60)
    
    try:
        client = DoceboClient()
        
        print("Fetching ALL courses (all pages)...")
        print()
        
        # Get all courses across all pages
        response = client.courses.get_all_courses(get_all_pages=True)
        
        print(f"Response keys: {list(response.keys())}")
        print()
        
        if 'data' in response:
            courses = response['data']
            print(f"Total courses fetched: {len(courses)}")
            print("First 10 courses:")
            print()
            
            for i, course in enumerate(courses[:10], 1):
                id_course = course.get('id_course', 'N/A')
                name = course.get('name', 'No name available')
                print(f"{i:3d}. ID: {id_course:<8} | Name: {name}")
                
            if len(courses) > 10:
                print(f"... and {len(courses) - 10} more courses")
                
        # Show final pagination info
        print()
        print("Final pagination summary:")
        for key in ['total_count', 'total_pages', 'fetched_all_pages']:
            if key in response:
                print(f"  {key}: {response[key]}")
                
        return True
        
    except Exception as e:
        print(f"❌ Error during paginated test: {e}")
        return False


def test_convenience_method():
    """Test the convenience method for getting course data"""
    print("\n" + "=" * 60)
    print("Testing convenience method get_courses...")
    print("=" * 60)
    
    try:
        client = DoceboClient()
        
        print("Using convenience method to get course list...")
        print()
        
        # Use convenience method that returns just the course list
        courses = client.courses.get_courses()
        
        print(f"Received {len(courses)} courses:")
        print()
        
        for i, course in enumerate(courses[:5], 1):  # Show first 5
            id_course = course.get('id_course', 'N/A')
            name = course.get('name', 'No name available')
            print(f"{i:3d}. ID: {id_course:<8} | Name: {name}")
            
        if len(courses) > 5:
            print(f"... and {len(courses) - 5} more courses")
            
        return True
        
    except Exception as e:
        print(f"❌ Error during convenience method test: {e}")
        return False


def main():
    """Run all tests"""
    print("Docebo Courses API Test")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Run tests
    test1_success = test_get_all_courses()
    test2_success = test_get_all_courses_paginated()
    test3_success = test_convenience_method()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Basic get_all_courses: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"Paginated get_all_courses: {'✅ PASS' if test2_success else '❌ FAIL'}")
    print(f"Convenience method: {'✅ PASS' if test3_success else '❌ FAIL'}")
    
    overall_success = test1_success and test2_success and test3_success
    print(f"\nOverall Result: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
    
    return overall_success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
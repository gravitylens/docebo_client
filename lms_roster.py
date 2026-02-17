#!/usr/bin/env python3
"""
LMS Roster - Docebo Session Email Extractor

A command-line tool to extract email addresses from Docebo course sessions
for a specific course and date.

Usage:
    python lms_roster.py <course_id> <date>
    python lms_roster.py 563 2026-02-03

Environment variables required:
    DOCEBO_BASE_URL, DOCEBO_CLIENT_ID, DOCEBO_CLIENT_SECRET, 
    DOCEBO_USERNAME, DOCEBO_PASSWORD
"""

import sys
import argparse
from datetime import datetime
from typing import List
from docebo_client import DoceboClient


def validate_date(date_string: str) -> str:
    """Validate date format (YYYY-MM-DD)"""
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return date_string
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_string}. Use YYYY-MM-DD")


def validate_course_id(course_id_string: str) -> int:
    """Validate course ID is a positive integer"""
    try:
        course_id = int(course_id_string)
        if course_id <= 0:
            raise ValueError("Course ID must be positive")
        return course_id
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid course ID: {course_id_string}. Must be a positive integer")


def get_session_emails(course_id: int, date: str) -> List[str]:
    """
    Get all email addresses from sessions for a specific course and date
    
    Args:
        course_id: The Docebo course ID
        date: Date in YYYY-MM-DD format
        
    Returns:
        List of email addresses
        
    Raises:
        Exception: If API calls fail
    """
    # Initialize client (loads from environment variables)
    client = DoceboClient()
    
    # Get course sessions for the specific date (without get_all_pages for simplicity)
    sessions_response = client.courses.get_course_sessions_by_date(
        course_id=course_id,
        date_from=date,
        date_to=date
    )
    
    # Handle different response structures
    sessions = []
    if isinstance(sessions_response, dict):
        if 'data' in sessions_response and isinstance(sessions_response['data'], dict):
            sessions = sessions_response['data'].get('sessions', [])
        elif 'data' in sessions_response and isinstance(sessions_response['data'], list):
            # Handle case where data is directly a list (from get_all_pages=True)
            sessions = sessions_response['data']
    elif isinstance(sessions_response, list):
        # Handle case where response is directly a list
        sessions = sessions_response
    
    if not sessions:
        return []
    
    all_emails = []
    
    # Get roster for each session
    for session in sessions:
        session_id = session.get('id_session')
        if session_id:
            try:
                roster_response = client.sessions.get_session_roster(session_id)
                roster_items = roster_response.get('data', {}).get('items', [])
                
                # Extract email addresses
                emails = [item.get('email') for item in roster_items if item.get('email')]
                all_emails.extend(emails)
                
            except Exception as e:
                print(f"Warning: Failed to get roster for session {session_id}: {e}", file=sys.stderr)
                continue
    
    # Remove duplicates while preserving order
    unique_emails = list(dict.fromkeys(all_emails))
    return unique_emails


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Extract email addresses from Docebo course sessions",
        epilog="Environment variables required: DOCEBO_BASE_URL, DOCEBO_CLIENT_ID, DOCEBO_CLIENT_SECRET, DOCEBO_USERNAME, DOCEBO_PASSWORD"
    )
    
    parser.add_argument(
        'course_id',
        type=validate_course_id,
        help='Docebo course ID (positive integer)'
    )
    
    parser.add_argument(
        'date',
        type=validate_date,
        help='Date in YYYY-MM-DD format'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output to stderr'
    )
    
    parser.add_argument(
        '--format',
        choices=['list', 'csv', 'json'],
        default='list',
        help='Output format (default: list, one email per line)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.verbose:
            print(f"Getting session emails for course {args.course_id} on {args.date}...", file=sys.stderr)
        
        emails = get_session_emails(args.course_id, args.date)
        
        if args.verbose:
            print(f"Found {len(emails)} unique email addresses", file=sys.stderr)
        
        if not emails:
            if args.verbose:
                print("No email addresses found", file=sys.stderr)
            sys.exit(0)
        
        # Output in requested format
        if args.format == 'list':
            for email in emails:
                print(email)
        elif args.format == 'csv':
            print(','.join(emails))
        elif args.format == 'json':
            import json
            print(json.dumps(emails))
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
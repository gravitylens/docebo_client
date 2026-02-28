#!/usr/bin/env python3
"""
Generate classroom sessions reminder message as markdown text
"""

import os
import sys
from datetime import datetime, timedelta
from docebo_client import DoceboClient
from dotenv import load_dotenv

# Load environment variables - check local .env first, then home directory
if os.path.exists('.env'):
    load_dotenv('.env')
elif os.path.exists(os.path.expanduser('~/.env')):
    load_dotenv(os.path.expanduser('~/.env'))
else:
    load_dotenv()  # Fall back to default behavior

def get_classroom_sessions_for_message():
    """Get classroom sessions data for message generation."""
    
    try:
        # Create Docebo client
        client = DoceboClient(
            base_url=os.getenv('DOCEBO_BASE_URL').strip(),
            client_id=os.getenv('DOCEBO_CLIENT_ID').strip(),
            client_secret=os.getenv('DOCEBO_CLIENT_SECRET').strip(),
            username=os.getenv('DOCEBO_USERNAME').strip(),
            password=os.getenv('DOCEBO_PASSWORD').strip()
        )
        
        courses_data = client.courses.get_courses(get_all_pages=True)
        
        # Filter for classroom courses
        classroom_courses = [course for course in courses_data 
                           if course.get('course_type') == 'classroom']
        
        # Set up date range (today to 7 days from now)
        today = datetime.now()
        date_from = today.strftime('%Y-%m-%d')
        date_to = (today + timedelta(days=7)).strftime('%Y-%m-%d')
        
        upcoming_sessions = []
        
        for course in classroom_courses:
            course_id = course.get('id_course')
            course_name = course.get('name', 'Unknown Course')
            
            try:
                response = client.courses.get_course_sessions_by_date(
                    course_id=course_id,
                    date_from=date_from,
                    date_to=date_to,
                    get_all_pages=True
                )
                
                sessions = []
                if isinstance(response, dict):
                    # Handle paginated response structure
                    if 'sessions' in response:
                        # Direct sessions array (likely paginated result)
                        sessions = response.get('sessions', [])
                    elif 'data' in response:
                        data = response.get('data', {})
                        if isinstance(data, dict):
                            sessions = data.get('sessions', [])
                        elif isinstance(data, list):
                            # Sometimes data is directly a list of sessions
                            sessions = data
                
                for session in sessions:
                    if isinstance(session, dict):
                        session_id = session.get('id_session')
                        start_date = session.get('date_begin', 'Unknown')
                        
                        # Get instructor information
                        instructors_list = []
                        try:
                            if session_id:
                                session_details = client.sessions.get_session_details(session_id)
                                
                                if isinstance(session_details, dict) and 'data' in session_details:
                                    data = session_details['data']
                                    if 'instructors' in data and isinstance(data['instructors'], list):
                                        instructors = data['instructors']
                                        
                                        for instructor in instructors:
                                            if isinstance(instructor, dict):
                                                first_name = instructor.get('firstname', '')
                                                last_name = instructor.get('lastname', '')
                                                full_name = f"{first_name} {last_name}".strip()
                                                if full_name:
                                                    instructors_list.append(full_name)
                        except:
                            pass
                        
                        instructor_display = ", ".join(instructors_list) if instructors_list else "TBD"
                        
                        # Get student count from session roster
                        student_count = 0
                        try:
                            if session_id:
                                roster = client.sessions.get_session_roster(session_id)
                                if isinstance(roster, dict) and 'data' in roster:
                                    data = roster['data']
                                    if isinstance(data, dict) and 'total_count' in data:
                                        student_count = data['total_count']
                        except:
                            pass
                        
                        upcoming_sessions.append({
                            'course_name': course_name,
                            'start_date': start_date,
                            'instructors': instructor_display,
                            'student_count': student_count
                        })
                        
            except:
                continue
        
        # Sort sessions by start date
        upcoming_sessions.sort(key=lambda x: x['start_date'])
        
        return upcoming_sessions
        
    except Exception as e:
        raise Exception(f"Error getting sessions: {e}")

def generate_classroom_reminder_markdown():
    """Generate the classroom sessions reminder message as markdown."""
    
    # Get session data
    sessions = get_classroom_sessions_for_message()
    
    if not sessions:
        return "Good Morning Trainers! No classroom sessions are scheduled for this week.  Woo Hoo!!"
    
    # Build message
    message = "Good Morning Trainers! Just a reminder that we have the following courses starting this week.\n\n"
    
    # Add each session as a formatted list item
    for i, session in enumerate(sessions, 1):
        # Format date to remove time
        start_date_formatted = session['start_date']
        if ' ' in start_date_formatted:
            start_date_formatted = start_date_formatted.split(' ')[0]
        
        course_name = session['course_name']
        instructor = session['instructors']
        student_count = session['student_count']
        
        message += f"{i}. **{course_name}**\n"
        message += f"   • Start Date: {start_date_formatted}\n"
        message += f"   • Instructor: {instructor}\n"
        message += f"   • Students Enrolled: {student_count}\n\n"
    
    # Add closing message
    message += "Good luck with your classes this week!"
    
    return message

if __name__ == "__main__":
    try:
        message = generate_classroom_reminder_markdown()
        print(message)
    except Exception as e:
        print(f"Error generating message: {e}", file=sys.stderr)
        exit(1)
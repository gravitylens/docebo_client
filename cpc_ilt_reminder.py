#!/usr/bin/env python3
"""
Generate CPC ILT sessions reminder message for tomorrow only
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

def get_cpc_ilt_course_ids():
    """Get the list of CPC ILT course IDs from environment variable."""
    cpc_ilt_ids = os.getenv('CPC_ILT_IDS', '')
    if not cpc_ilt_ids:
        raise ValueError("CPC_ILT_IDS environment variable is required")
    
    # Parse comma-separated course IDs
    try:
        course_ids = [int(course_id.strip()) for course_id in cpc_ilt_ids.split(',') if course_id.strip()]
        if not course_ids:
            raise ValueError("No valid course IDs found in CPC_ILT_IDS")
        return course_ids
    except ValueError as e:
        raise ValueError(f"Invalid course IDs in CPC_ILT_IDS: {e}")

def map_gmt_offset_to_region(gmt_offset):
    """Map GMT offset to datacenter region for lab assignment."""
    if not gmt_offset:
        return "US-CENTRAL"  # Default fallback
    
    try:
        # Parse GMT offset (e.g., "GMT -06:00" or "GMT +02:00")
        if 'GMT' in gmt_offset:
            offset_str = gmt_offset.replace('GMT', '').strip()
            # Extract just the hour part (ignore minutes)
            if ':' in offset_str:
                offset_str = offset_str.split(':')[0]
            offset_hours = int(offset_str)
        else:
            return "US-CENTRAL"  # Default if format is unexpected
        
        # Map GMT offset to regions (West to East)
        # GMT-11 through GMT-5 → US-CENTRAL
        if -11 <= offset_hours <= -5:
            return "US-CENTRAL"
        # GMT-4 through GMT-2 → US-EAST-2
        elif -4 <= offset_hours <= -2:
            return "US-EAST-2"
        # GMT-1 through GMT+3 → EMEA
        elif -1 <= offset_hours <= 3:
            return "EMEA"
        # GMT+4 through GMT+12 → APAC-2
        elif 4 <= offset_hours <= 12:
            return "APAC-2"
        else:
            return "US-CENTRAL"  # Default for out-of-range values
            
    except (ValueError, AttributeError):
        return "US-CENTRAL"  # Default fallback on parsing errors

def get_tomorrow_sessions():
    """Get CPC ILT sessions data for tomorrow only."""
    
    try:
        # Create Docebo client
        client = DoceboClient(
            base_url=os.getenv('DOCEBO_BASE_URL').strip(),
            client_id=os.getenv('DOCEBO_CLIENT_ID').strip(),
            client_secret=os.getenv('DOCEBO_CLIENT_SECRET').strip(),
            username=os.getenv('DOCEBO_USERNAME').strip(),
            password=os.getenv('DOCEBO_PASSWORD').strip()
        )
        
        # Get the course IDs we're interested in
        target_course_ids = get_cpc_ilt_course_ids()
        
        # Set up date range (for testing, use 2026-03-03)
        tomorrow = datetime.now() + timedelta(days=1)
        date_tomorrow = tomorrow.strftime('%Y-%m-%d')
        # date_tomorrow = '2026-02-23'  # Testing specific date
        
        tomorrow_sessions = []
        
        for course_id in target_course_ids:
            try:
                # Get sessions for this course tomorrow
                response = client.courses.get_course_sessions_by_date(
                    course_id=course_id,
                    date_from=date_tomorrow,
                    date_to=date_tomorrow
                )
                
                sessions = []
                if isinstance(response, dict):
                    data = response.get('data', {})
                    if isinstance(data, dict):
                        sessions = data.get('sessions', [])
                
                for session in sessions:
                    if isinstance(session, dict):
                        session_id = session.get('id_session')
                        start_date = session.get('date_begin', 'Unknown')
                        
                        # Get instructor information and event details
                        instructors_list = []
                        event_start_time = ''
                        timezone_info = ''
                        gmt_offset = ''
                        region = 'US-CENTRAL'  # Default region
                        course_name = f"Course {course_id}"  # Default fallback
                        try:
                            if session_id:
                                session_details = client.sessions.get_session_details(session_id)
                                
                                if isinstance(session_details, dict) and 'data' in session_details:
                                    data = session_details['data']
                                    
                                    # Extract course name from session details
                                    if 'course' in data and isinstance(data['course'], dict):
                                        course_name = data['course'].get('name', f"Course {course_id}")
                                    
                                    if 'instructors' in data and isinstance(data['instructors'], list):
                                        instructors = data['instructors']
                                        
                                        for instructor in instructors:
                                            if isinstance(instructor, dict):
                                                first_name = instructor.get('firstname', '')
                                                last_name = instructor.get('lastname', '')
                                                full_name = f"{first_name} {last_name}".strip()
                                                if full_name:
                                                    instructors_list.append({
                                                        'first_name': first_name,
                                                        'full_name': full_name
                                                    })
                                
                                # Get session events for proper date/time/timezone
                                events_response = client.sessions.get_session_events(session_id)
                                
                                # Try to access events data with different possible structures
                                events_data = None
                                if isinstance(events_response, dict):
                                    if 'data' in events_response and isinstance(events_response['data'], dict):
                                        if 'items' in events_response['data']:
                                            events_data = events_response['data']['items']
                                        else:
                                            events_data = events_response['data']
                                    elif 'items' in events_response:
                                        events_data = events_response['items']

                                
                                if events_data and isinstance(events_data, list) and events_data:
                                    # Sort events by schedule date
                                    sorted_events = sorted(events_data, key=lambda x: x.get('schedule', {}).get('date', ''))
                                    earliest_event = sorted_events[0] if sorted_events else None
                                    
                                    if earliest_event:
                                        schedule = earliest_event.get('schedule', {})
                                        
                                        # Extract time and timezone info from schedule
                                        event_date = schedule.get('date', '')
                                        event_time = schedule.get('time_begin', '')
                                        timezone_info = schedule.get('timezone', '')
                                        gmt_offset = schedule.get('offset', '')
                                        
                                        # Combine date and time for proper datetime
                                        if event_date and event_time:
                                            event_start_time = f"{event_date} {event_time}"
                                        else:
                                            event_start_time = event_date or event_time
                                        
                                        # Map GMT offset to datacenter region
                                        region = map_gmt_offset_to_region(gmt_offset)
                                    else:
                                        region = "US-CENTRAL"  # Default region
                                            
                                else:
                                    region = "US-CENTRAL"  # Default region when no events
                                
                        except Exception as e:
                            print(f"Error getting session details/events: {e}")
                            pass
                        
                        # Get student count and email list from session roster
                        student_count = 0
                        student_emails = []
                        try:
                            if session_id:
                                roster = client.sessions.get_session_roster(session_id)
                                if isinstance(roster, dict) and 'data' in roster:
                                    data = roster['data']
                                    if isinstance(data, dict) and 'total_count' in data:
                                        student_count = data['total_count']
                                    
                                    # Extract student emails from roster
                                    if 'items' in data and isinstance(data['items'], list):
                                        for item in data['items']:
                                            if isinstance(item, dict):
                                                email = item.get('email', '').strip()
                                                if email and email not in student_emails:
                                                    student_emails.append(email)
                                        

                        except:
                            pass
                        
                        # Run cmbuild command with student emails if we have any
                        if student_emails and region:
                            try:
                                # Create email string for piping
                                email_string = '\n'.join(student_emails)
                                # Execute cmbuild command with emails piped in
                                import subprocess
                                result = subprocess.run(
                                    ['cmbuild', '-course', 'PAM SaaS Lab', '-region', region],
                                    input=email_string,
                                    text=True,
                                    capture_output=True
                                )
                                # Silently continue regardless of command result
                            except Exception:
                                # Silently continue if cmbuild command fails
                                pass
                        
                        tomorrow_sessions.append({
                            'course_id': course_id,
                            'course_name': course_name,
                            'start_date': start_date,
                            'event_start_time': event_start_time,
                            'timezone_info': timezone_info,
                            'gmt_offset': gmt_offset,
                            'region': region,
                            'instructors': instructors_list,
                            'student_count': student_count,
                            'student_emails': student_emails
                        })
                        
            except Exception as e:
                # Log the error but continue with other courses
                print(f"Warning: Error processing course {course_id}: {e}", file=sys.stderr)
                continue
        
        # Sort sessions by start date
        tomorrow_sessions.sort(key=lambda x: x['start_date'])
        
        return tomorrow_sessions, date_tomorrow
        
    except Exception as e:
        raise Exception(f"Error getting sessions: {e}")

def generate_cpc_ilt_reminder_markdown():
    """Generate personalized CPC ILT sessions reminder messages for instructors."""
    
    # Get session data
    sessions, tomorrow_date = get_tomorrow_sessions()
    
    if not sessions:
        return f"No CPC ILT sessions are scheduled for {tomorrow_date}."
    
    # Generate personalized messages for each instructor
    messages = []
    
    for session in sessions:
        instructors = session['instructors']
        student_count = session['student_count']
        course_name = session['course_name']
        event_start_time = session['event_start_time']
        timezone_info = session['timezone_info'] 
        gmt_offset = session['gmt_offset']
        region = session['region']
        
        # Format the start time nicely from event data
        time_info = ""
        if event_start_time and timezone_info:
            try:
                # Parse the event datetime and format just the time
                dt = datetime.fromisoformat(event_start_time.replace(' ', 'T'))
                formatted_time = dt.strftime('%I:%M %p')  # e.g., "09:00 AM"
                time_info = f" at {formatted_time} {timezone_info}"
                if gmt_offset:
                    time_info += f" ({gmt_offset})"
            except:
                time_info = f" ({timezone_info})" if timezone_info else ""
        elif timezone_info:
            time_info = f" ({timezone_info})"
        
        if instructors:
            for instructor in instructors:
                first_name = instructor['first_name']
                
                message = f"Hey {first_name},\n\n"
                message += f"It looks like you have a {course_name} class starting tomorrow{time_info} with {student_count} students. "
                message += f"I'll go ahead and build those labs in the {region} datacenter now and send links to all the students. "
                message += f"\n\nGood luck with your class tomorrow! "
                
                messages.append(message)
        else:
            # Fallback if no instructor info available
            message = f"Hey there,\n\n"
            message += f"It looks like there's {course_name} starting tomorrow{time_info} with {student_count} students. "
            message += f"I'll go ahead and build the students' labs in the {region} datacenter and send them links, but someone probably better figure out who is teaching this, because I don't know. "
            message += f"\n\nGood luck to whomever is teaching this tomorrow!"
            
            messages.append(message)
    
    return '\n\n---\n\n'.join(messages)

if __name__ == "__main__":
    try:
        message = generate_cpc_ilt_reminder_markdown()
        print(message)
    except Exception as e:
        print(f"Error generating message: {e}", file=sys.stderr)
        exit(1)
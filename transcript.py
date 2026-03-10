#!/usr/bin/env python3
"""
Generate a transcript message for a user's completed courses
"""

import os
import sys
from datetime import datetime
from docebo_client import DoceboClient
from dotenv import load_dotenv

# Load environment variables
if os.path.exists('.env'):
    load_dotenv('.env')
elif os.path.exists(os.path.expanduser('~/.env')):
    load_dotenv(os.path.expanduser('~/.env'))
else:
    load_dotenv()

def format_transcript_message(search_text, enrollments):
    """Format the transcript data into a chat-friendly message"""
    
    if not enrollments or 'data' not in enrollments or not enrollments['data']['items']:
        return f"**Transcript for '{search_text}'**\n\nNo completed courses found."
    
    courses = enrollments['data']['items']
    
    # Group courses by type for better organization
    elearning_courses = [c for c in courses if c.get('course_type') == 'elearning']
    classroom_courses = [c for c in courses if c.get('course_type') == 'classroom']
    other_courses = [c for c in courses if c.get('course_type') not in ['elearning', 'classroom']]
    
    # Build the message
    message = f"**Learning Transcript for '{search_text}'**\n\n"
    message += f"**Summary:** {len(courses)} completed courses\n\n"
    
    if elearning_courses:
        message += f"## E-Learning Courses ({len(elearning_courses)})\n\n"
        for i, course in enumerate(elearning_courses, 1):
            course_name = course.get('course_name', 'Unknown Course')
            completion_date = course.get('enrollment_completion_date', 'N/A')
            score = course.get('enrollment_score')
            
            message += f"{i}. **{course_name}**\n"
            if completion_date != 'N/A':
                try:
                    # Parse and format the date
                    date_obj = datetime.strptime(completion_date, '%Y-%m-%d %H:%M:%S')
                    formatted_date = date_obj.strftime('%B %d, %Y')
                    message += f"   Completed: {formatted_date}\n"
                except:
                    message += f"   Completed: {completion_date}\n"
            
            if score and score != 'N/A':
                try:
                    score_num = float(score)
                    if score_num > 0:
                        message += f"   Score: {score_num}%\n"
                except:
                    pass
            
            message += "\n"
    
    if classroom_courses:
        message += f"## Classroom Courses ({len(classroom_courses)})\n\n"
        for i, course in enumerate(classroom_courses, 1):
            course_name = course.get('course_name', 'Unknown Course')
            completion_date = course.get('enrollment_completion_date', 'N/A')
            score = course.get('enrollment_score')
            
            message += f"{i}. **{course_name}**\n"
            if completion_date != 'N/A':
                try:
                    date_obj = datetime.strptime(completion_date, '%Y-%m-%d %H:%M:%S')
                    formatted_date = date_obj.strftime('%B %d, %Y')
                    message += f"   Completed: {formatted_date}\n"
                except:
                    message += f"   Completed: {completion_date}\n"
            
            if score and score != 'N/A':
                try:
                    score_num = float(score)
                    if score_num > 0:
                        message += f"   Score: {score_num}%\n"
                except:
                    pass
            
            message += "\n"
    
    if other_courses:
        message += f"## Other Courses ({len(other_courses)})\n\n"
        for i, course in enumerate(other_courses, 1):
            course_name = course.get('course_name', 'Unknown Course')
            course_type = course.get('course_type', 'Unknown')
            completion_date = course.get('enrollment_completion_date', 'N/A')
            score = course.get('enrollment_score')
            
            message += f"{i}. **{course_name}** ({course_type})\n"
            if completion_date != 'N/A':
                try:
                    date_obj = datetime.strptime(completion_date, '%Y-%m-%d %H:%M:%S')
                    formatted_date = date_obj.strftime('%B %d, %Y')
                    message += f"   Completed: {formatted_date}\n"
                except:
                    message += f"   Completed: {completion_date}\n"
            
            if score and score != 'N/A':
                try:
                    score_num = float(score)
                    if score_num > 0:
                        message += f"   Score: {score_num}%\n"
                except:
                    pass
            
            message += "\n"
    
    message += "---\n"
    message += f"*Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*"
    
    return message

def generate_transcript(search_text):
    """Generate transcript for a user"""
    try:
        # Create Docebo client
        client = DoceboClient()
        
        # Get completed enrollments for the user
        enrollments = client.users.get_enrollments(
            search_text, 
            enrollment_status=["completed"]
        )
        
        # Format as chat message
        message = format_transcript_message(search_text, enrollments)
        
        return message
        
    except Exception as e:
        error_message = f"**Error generating transcript for '{search_text}'**\n\n"
        error_message += f"Details: {str(e)}\n\n"
        error_message += "Please check:\n"
        error_message += "• The search text is correct\n"
        error_message += "• The user exists in the system\n"
        error_message += "• Your API credentials are valid\n\n"
        error_message += f"*Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*"
        
        return error_message

def main():
    """Main function"""
    # Get search text from command line or prompt
    if len(sys.argv) > 1:
        search_text = ' '.join(sys.argv[1:])
    else:
        search_text = input("Enter username or email to generate transcript: ").strip()
    
    if not search_text:
        print("Error: Please provide a search text")
        sys.exit(1)
    
    # Generate the transcript
    transcript_message = generate_transcript(search_text)
    
    # Output the formatted message
    print(transcript_message)

if __name__ == "__main__":
    main()
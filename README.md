# Docebo Client

A Python library for interacting with the Docebo e-learning platform APIs with comprehensive pagination support.

## Features

- **OAuth2 Authentication** with automatic token refresh
- **Complete Course Management** with pagination support
- **Session Management** and roster retrieval
- **Environment Variable Configuration** for secure credential management
- **Type Hints** for better development experience
- **Comprehensive Pagination** - handles large datasets automatically
- **Integration Testing** - real API validation

## Installation

### From source:
```bash
git clone <repository-url>
cd docebo-client
pip install -e .
```

### For development:
```bash
git clone <repository-url>
cd docebo-client
pip install -e ".[dev]"
```

### Build wheel:
```bash
python -m build
```

## Configuration

Create a `.env` file in your project root with your Docebo credentials:

```env
DOCEBO_BASE_URL=https://your-domain.docebosaas.com
DOCEBO_CLIENT_ID=your_client_id
DOCEBO_CLIENT_SECRET=your_client_secret
DOCEBO_USERNAME=your_username
DOCEBO_PASSWORD=your_password
```

## Quick Start

```python
from docebo_client import DoceboClient

# Initialize client (loads from .env automatically)
client = DoceboClient()

# Get all courses with pagination
courses = client.courses.get_all_courses(page=1, page_size=50)
print(f"Found {len(courses['data']['items'])} courses")

# Get ALL courses across all pages automatically
all_courses = client.courses.get_all_courses(get_all_pages=True)
print(f"Total courses: {all_courses['total_count']}")

# Get course sessions for a specific year
sessions = client.courses.get_course_sessions(
    course_id=563, 
    year=2025,
    get_all_pages=True
)

# Get sessions in a date range
date_sessions = client.courses.get_course_sessions_by_date(
    course_id=563,
    date_from="2026-02-03", 
    date_to="2026-02-03"
)

# Get session roster
if date_sessions['data']['sessions']:
    session_id = date_sessions['data']['sessions'][0]['id_session']
    
    # Get session roster
    roster = client.sessions.get_session_roster(session_id)
    emails = [item['email'] for item in roster['data']['items']]
    print(f"Session has {len(emails)} participants")
    
    # Get session details
    details = client.sessions.get_session_details(session_id)
    print(f"Session: {details['data']['name']}")
    
    # Get session events
    events = client.sessions.get_session_events(session_id)
    print(f"Session has {len(events['data']['items'])} events")

# Look up users
user_results = client.users.lookup_user("jason.niles")
print(f"Found {len(user_results['data']['items'])} users")

# Option 1: Get enrollments directly by search (recommended)
enrollments = client.users.get_enrollments("jason.niles")
print(f"User has {len(enrollments['data']['items'])} enrollments")

# Get only completed enrollments
completed = client.users.get_enrollments(
    "jason.niles", 
    enrollment_status=["completed"]
)
print(f"User has {len(completed['data']['items'])} completed courses")

# Option 2: Manual workflow using lookup + courses API
if user_results['data']['items']:
    user_id = user_results['data']['items'][0]['id_user']
    enrollments = client.courses.get_enrollments_by_user_id(user_id)
    print(f"User has {len(enrollments['data']['items'])} enrollments")

# Get LTI objects from Central Repository
lti_objects = client.centralrepo.get_repository_materials(types=['lti'])
print(f"Found {len(lti_objects['data'])} LTI objects")

# Get all training materials from Central Repository 
all_materials = client.centralrepo.get_repository_materials()
print(f"Found {len(all_materials['data'])} total materials")
```

## API Reference

### DoceboClient

Main client class for interacting with Docebo APIs.

**Parameters:**
- `base_url` (str, optional): Docebo instance URL (loads from `DOCEBO_BASE_URL`)
- `client_id` (str, optional): OAuth2 client ID (loads from `DOCEBO_CLIENT_ID`) 
- `client_secret` (str, optional): OAuth2 client secret (loads from `DOCEBO_CLIENT_SECRET`)
- `username` (str, optional): Username (loads from `DOCEBO_USERNAME`)
- `password` (str, optional): Password (loads from `DOCEBO_PASSWORD`)

### CoursesAPI

API methods for course management.

#### `get_all_courses(page=1, page_size=200, get_all_pages=False)`
Get courses with pagination support.

**Parameters:**
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page, max 200 (default: 200)  
- `get_all_pages` (bool): Auto-fetch all pages (default: False)

**Returns:** Dict with courses data and pagination info

#### `get_course_sessions(course_id, year=None, page=1, page_size=200, get_all_pages=False)`
Get classroom sessions for a specific course.

**Parameters:**
- `course_id` (int): Course ID
- `year` (int, optional): Filter by year
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 200)
- `get_all_pages` (bool): Auto-fetch all pages (default: False)

**Returns:** Dict with sessions in `data.sessions` array

#### `get_course_sessions_by_date(course_id, date_from, date_to, page=1, page_size=200, get_all_pages=False)`
Get course sessions within a date range.

**Parameters:**
- `course_id` (int): Course ID  
- `date_from` (str): Start date (YYYY-MM-DD)
- `date_to` (str): End date (YYYY-MM-DD)
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 200)
- `get_all_pages` (bool): Auto-fetch all pages (default: False)

**Returns:** Dict with sessions containing dates arrays

#### Convenience Methods

- `get_courses(**kwargs)` - Returns just the course list without pagination metadata
- `get_all_courses_auto_paginated()` - Simple method to get all courses across all pages

#### `get_enrollments_by_user_id(user_id, enrollment_status=None)`
Get course enrollments for a specific user.

**Parameters:**
- `user_id` (int): User ID
- `enrollment_status` (List[str], optional): Filter by enrollment status (e.g., ["completed", "in_progress", "not_started"])

**Returns:** Dict with user's course enrollments

### SessionsAPI

API methods for session management.

#### `get_session_roster(session_id)`
Get enrollment roster for a specific session.

**Parameters:**
- `session_id` (int): Session ID

**Returns:** Dict with enrollments in `data.items` array, each containing email and user info

#### `get_session_details(session_id)`
Get details for a specific session.

**Parameters:**
- `session_id` (int): Session ID

**Returns:** Dict with session details including name, dates, and configuration

#### `get_session_events(session_id)`
Get the events list for a specific session.

**Parameters:**
- `session_id` (int): Session ID

**Returns:** Dict with session events and scheduling information

### UsersAPI

API methods for user management.

#### `lookup_user(search_text)`
Look up users by search text.

**Parameters:**
- `search_text` (str): Search text to find users (username, email, etc.)

**Returns:** Dict with user search results in `data.items` array

#### `get_enrollments(search_text, enrollment_status=None)`
Get course enrollments for a user by searching for them first.

**Parameters:**
- `search_text` (str): Search text to find the user (username, email, etc.)
- `enrollment_status` (List[str], optional): Filter by enrollment status (e.g. ["completed", "in_progress"])

**Returns:** Dict with user's course enrollments

**Raises:** Exception if user not found or multiple users found

#### `get_enrollments_by_user_id(user_id, enrollment_status="completed")`
Get course enrollments for a specific user.

**Parameters:**
- `user_id` (str): The ID of the user
- `enrollment_status` (str): Filter by enrollment status (default: "completed")

**Returns:** Dict with user's course enrollments in `data.items` array

### CentralRepoAPI

API methods for Central Repository management.

#### `get_repository_materials(folder_id=1, types=None, page=1, page_size=200, get_all_pages=False, include_subfolders=True, sort_attr="created_on", sort_dir="desc")`
Get training materials from the Central Repository.

**Parameters:**
- `folder_id` (int, optional): Folder ID to get materials from (default: 1)  
- `types` (List[str], optional): List of material types to filter (e.g., ['lti', 'scorm']. If None, returns all material types)
- `page` (int, optional): Page number to retrieve (default: 1)
- `page_size` (int, optional): Number of items per page (default: 200, max: 200)
- `get_all_pages` (bool, optional): If True, automatically fetch all pages and return combined results (default: False)
- `include_subfolders` (bool, optional): If True, include materials from descendant folders (default: True)
- `sort_attr` (str, optional): Attribute to sort by (default: "created_on")
- `sort_dir` (str, optional): Sort direction "asc" or "desc" (default: "desc")

**Returns:** Dict with training materials from the central repository

**Examples:**
```python
# Get all LTI objects including subfolders (default behavior)
all_lti = client.central_repo.get_repository_materials(types=['lti'], get_all_pages=True)

# Get only from main folder (no subfolders)  
main_folder_only = client.central_repo.get_repository_materials(types=['lti'], include_subfolders=False)

# Get with custom sorting
sorted_materials = client.central_repo.get_repository_materials(types=['lti'], sort_attr="name", sort_dir="asc")
```

### DoceboAuth

Handles OAuth2 authentication with automatic token refresh.

**Methods:**
- `authenticate()` - Perform OAuth2 authentication
- `is_authenticated()` - Check if token is valid
- `refresh_if_needed()` - Auto-refresh token if needed

## Pagination Support

All `get_` methods support comprehensive pagination:

```python
# Manual pagination
page1 = client.courses.get_all_courses(page=1, page_size=100)
page2 = client.courses.get_all_courses(page=2, page_size=100)

# Automatic pagination (recommended for large datasets)
all_data = client.courses.get_all_courses(get_all_pages=True)
# Returns: {"data": [all_items], "total_count": 1234, "fetched_all_pages": True}

# Convenience method for just the data
course_list = client.courses.get_courses(get_all_pages=True)
# Returns: [course1, course2, course3, ...]
```

## Testing

The package includes comprehensive tests validating real API functionality:

```bash
# Test authentication
python tests/test_auth.py

# Test courses API with pagination
python tests/test_courses.py

# Test session management  
python tests/test_course_sessions_by_date.py

# Test integration workflow
python tests/test_sessions_and_rosters.py
```

## Response Structures

### Courses
```json
{
  "data": {
    "items": [
      {
        "id_course": 563,
        "name": "Course Name",
        "uidCourse": "E-12345",
        "date_last_updated": "2025-01-22 13:27:13"
      }
    ],
    "count": 200,
    "total_count": 1266
  }
}
```

### Sessions 
```json
{
  "data": {
    "sessions": [
      {
        "id_session": 1714,
        "name": "Session Name",
        "date_begin": "2026-02-03 08:00:00",
        "date_end": "2026-02-06 16:00:00",
        "dates": [
          {
            "day": "2026-02-03",
            "name": "Day 1", 
            "time_begin": "09:00:00",
            "time_end": "17:00:00",
            "timezone": "Europe/London"
          }
        ]
      }
    ]
  }
}
```

### Session Roster
```json
{
  "data": {
    "items": [
      {
        "email": "user@example.com",
        "firstname": "John",
        "lastname": "Doe"
      }
    ]
  }
}
```

## Error Handling

```python
try:
    courses = client.courses.get_all_courses()
except Exception as e:
    print(f"API Error: {e}")
```

## License

MIT License
"""
Courses API module for Docebo
"""

import requests
from typing import List, Dict, Any, Optional
from .auth import DoceboAuth


class CoursesAPI:
    """
    API client for Docebo courses endpoints
    """
    
    def __init__(
        self,
        base_url: str,
        session: requests.Session,
        auth: DoceboAuth
    ):
        """
        Initialize the Courses API
        
        Args:
            base_url (str): Base URL for the API
            session (requests.Session): HTTP session
            auth (DoceboAuth): Authentication handler
        """
        self.base_url = base_url
        self.session = session
        self.auth = auth
    
    def get_all_courses(
        self,
        page: int = 1,
        page_size: int = 200,
        get_all_pages: bool = False
    ) -> Dict[str, Any]:
        """
        Get all courses with pagination support
        
        Based on: Returns all courses.bru
        
        Args:
            page (int): Page number to retrieve (default: 1)
            page_size (int): Number of items per page (default: 200, max: 200)
            get_all_pages (bool): If True, automatically fetch all pages and return combined results
        
        Returns:
            Dict: Response containing courses and pagination info
        """
        if not self.auth.refresh_if_needed():
            raise Exception("Authentication required")
        
        url = f"{self.base_url}/learn/v1/courses"
        
        if get_all_pages:
            return self._get_all_paginated_results(url)
        
        params = {
            "page": page,
            "page_size": min(page_size, 200)  # Docebo typically limits to 200
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get courses: {e}")
    
    def get_course_sessions(
        self,
        course_id: int,
        year: Optional[int] = None,
        page: int = 1,
        page_size: int = 200,
        get_all_pages: bool = False
    ) -> Dict[str, Any]:
        """
        Get classroom sessions for a specific course with pagination support
        
        Based on: Get Course.bru
        
        Args:
            course_id (int): The ID of the course
            year (int, optional): Filter by year (defaults to current year)
            page (int): Page number to retrieve (default: 1)
            page_size (int): Number of items per page (default: 200, max: 200)
            get_all_pages (bool): If True, automatically fetch all pages and return combined results
        
        Returns:
            Dict: Response containing course sessions and pagination info
        """
        if not self.auth.refresh_if_needed():
            raise Exception("Authentication required")
        
        url = f"{self.base_url}/learn/v1/courses/{course_id}/classroom/session"
        
        params = {
            "page": page,
            "page_size": min(page_size, 200)
        }
        if year:
            params["year"] = year
        
        if get_all_pages:
            return self._get_all_paginated_results(url, params)
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get course sessions: {e}")
    
    def get_course_sessions_by_date(
        self,
        course_id: int,
        date_from: str,
        date_to: str,
        page: int = 1,
        page_size: int = 200,
        get_all_pages: bool = False
    ) -> Dict[str, Any]:
        """
        Get classroom sessions for a course within a date range with pagination support
        
        Based on: Session per Course.bru
        
        Args:
            course_id (int): The ID of the course
            date_from (str): Start date (YYYY-MM-DD format)
            date_to (str): End date (YYYY-MM-DD format)
            page (int): Page number to retrieve (default: 1)
            page_size (int): Number of items per page (default: 200, max: 200)
            get_all_pages (bool): If True, automatically fetch all pages and return combined results
        
        Returns:
            Dict: Response containing course sessions in date range and pagination info
        """
        if not self.auth.refresh_if_needed():
            raise Exception("Authentication required")
        
        url = f"{self.base_url}/learn/v1/courses/{course_id}/classroom/session"
        
        params = {
            "date_from": date_from,
            "date_to": date_to,
            "page": page,
            "page_size": min(page_size, 200)
        }
        
        if get_all_pages:
            return self._get_all_paginated_results(url, params)
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get course sessions by date: {e}")
    
    def _get_all_paginated_results(
        self, 
        url: str, 
        base_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Helper method to fetch all pages of results
        
        Args:
            url (str): The API endpoint URL
            base_params (dict, optional): Base parameters to include with each request
        
        Returns:
            Dict: Combined response with all data from all pages
        """
        if base_params is None:
            base_params = {}
        
        all_data = []
        page = 1
        page_size = 200
        total_count = None
        total_pages = None
        
        while True:
            params = base_params.copy()
            params.update({
                "page": page,
                "page_size": page_size
            })
            
            try:
                response = self.session.get(url, params=params)
                response.raise_for_status()
                result = response.json()
                
                # Extract data (Docebo returns sessions in nested structure)
                if 'data' in result and 'sessions' in result['data']:
                    all_data.extend(result['data']['sessions'])
                elif 'sessions' in result:
                    all_data.extend(result['sessions'])
                elif 'data' in result and 'items' in result['data']:
                    all_data.extend(result['data']['items'])
                elif 'items' in result:
                    all_data.extend(result['items'])
                elif 'data' in result and isinstance(result['data'], list):
                    all_data.extend(result['data'])
                elif isinstance(result, list):
                    all_data.extend(result)
                else:
                    # If structure is different, add the whole result
                    all_data.append(result)
                
                # Extract pagination info (check both nested and direct structure)
                data_section = result.get('data', {}) if 'data' in result else result
                if 'total_count' in data_section:
                    total_count = data_section['total_count']
                if 'total_page_count' in data_section:
                    total_pages = data_section['total_page_count']
                elif 'total_pages' in data_section:
                    total_pages = data_section['total_pages']
                elif 'has_more_data' in data_section:
                    # Docebo uses has_more_data instead of has_more_page
                    if not data_section['has_more_data']:
                        break
                
                # Check if we have all pages
                if total_pages and page >= total_pages:
                    break
                elif total_count and len(all_data) >= total_count:
                    break
                elif 'data' in result and 'sessions' in result['data'] and len(result['data']['sessions']) < page_size:
                    # If we got fewer results than requested, we're likely at the end
                    break
                elif 'sessions' in result and len(result['sessions']) < page_size:
                    break
                elif 'data' in result and 'items' in result['data'] and len(result['data']['items']) < page_size:
                    # If we got fewer results than requested, we're likely at the end
                    break
                elif 'items' in result and len(result['items']) < page_size:
                    break
                
                page += 1
                
                # Safety check to prevent infinite loops
                if page > 1000:  # Arbitrary large number
                    break
                    
            except requests.exceptions.RequestException as e:
                raise Exception(f"Failed to fetch page {page}: {e}")
        
        # Return the combined result in a structure similar to single page response
        return {
            "data": all_data,
            "total_count": total_count or len(all_data),
            "total_pages": total_pages or page,
            "current_page": "all",
            "page_size": len(all_data),
            "fetched_all_pages": True
        }
    
    def get_courses(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Convenience method to get just the course data (not pagination metadata)
        
        Args:
            **kwargs: Arguments passed to get_all_courses
        
        Returns:
            List: List of course objects
        """
        result = self.get_all_courses(**kwargs)
        if 'data' in result and 'sessions' in result['data']:
            return result['data']['sessions']
        elif 'sessions' in result:
            return result['sessions']
        elif 'data' in result and 'items' in result['data']:
            return result['data']['items']
        elif 'items' in result:
            return result['items']
        elif 'data' in result and isinstance(result['data'], list):
            return result['data']
        elif isinstance(result, list):
            return result
        else:
            return [result]
    
    def get_all_courses_auto_paginated(self) -> List[Dict[str, Any]]:
        """
        Convenience method to get ALL courses across all pages
        
        Returns:
            List: List of all course objects
        """
        return self.get_courses(get_all_pages=True)
    
    def get_enrollments_by_user_id(
        self,
        user_id: int,
        enrollment_status: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get course enrollments for a specific user
        
        Based on: Get Enrollments.bru
        
        Args:
            user_id (int): The ID of the user
            enrollment_status (List[str], optional): Filter by enrollment status 
                (e.g., ["completed", "in_progress", "not_started"])
        
        Returns:
            Dict: Response containing course enrollments for the user
        """
        if not self.auth.refresh_if_needed():
            raise Exception("Authentication required")
        
        url = f"{self.base_url}/course/v1/courses/enrollments"
        
        # Build the request body
        data = {
            "user_id": [str(user_id)]  # API expects array of strings
        }
        
        if enrollment_status:
            data["enrollment_status"] = enrollment_status
        
        try:
            response = self.session.get(url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get enrollments: {e}")
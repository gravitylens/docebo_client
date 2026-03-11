"""
Central Repository API module for Docebo
"""

import requests
from typing import Dict, Any, Optional
from .auth import DoceboAuth


class CentralRepoAPI:
    """
    API client for Docebo Central Repository endpoints
    """
    
    def __init__(
        self,
        base_url: str,
        session: requests.Session,
        auth: DoceboAuth
    ):
        """
        Initialize the Central Repository API
        
        Args:
            base_url (str): Base URL for the API
            session (requests.Session): HTTP session
            auth (DoceboAuth): Authentication handler
        """
        self.base_url = base_url
        self.session = session
        self.auth = auth
    
    def get_repository_materials(
        self, 
        folder_id: int = 1, 
        types: list = None,
        page: int = 1,
        page_size: int = 200,
        get_all_pages: bool = False,
        include_subfolders: bool = True,
        sort_attr: str = "created_on",
        sort_dir: str = "desc"
    ) -> Dict[str, Any]:
        """
        Get training materials from the Central Repository
        
        Based on: Get Central Repository.bru and web interface behavior
        
        Args:
            folder_id (int): Folder ID to get materials from (default: 1)
            types (list, optional): List of material types to filter (e.g., ['lti', 'scorm'])
                                  If None, returns all material types
            page (int): Page number to retrieve (default: 1)
            page_size (int): Number of items per page (default: 200, max: 200)
            get_all_pages (bool): If True, automatically fetch all pages and return combined results
            include_subfolders (bool): If True, include materials from descendant folders (default: True)
            sort_attr (str): Attribute to sort by (default: "created_on")
            sort_dir (str): Sort direction "asc" or "desc" (default: "desc")
        
        Returns:
            Dict: Response containing training materials from the central repository
        """
        if not self.auth.refresh_if_needed():
            raise Exception("Authentication required")
        
        url = f"{self.base_url}/tmrepo/v1/folders/{folder_id}/materials"
        
        # Build base parameters to match web interface
        base_params = {
            "sort_attr": sort_attr,
            "sort_dir": sort_dir
        }
        
        # Add folder filtering (critical - includes subfolders!)
        if include_subfolders:
            base_params["folder_filter_type"] = "with_descendants"
        
        # Add material type filters
        if types:
            for i, material_type in enumerate(types):
                base_params[f"type[{i}]"] = material_type
        
        if get_all_pages:
            return self._get_all_paginated_results(url, base_params)
        
        # Add pagination parameters
        params = base_params.copy()
        params.update({
            "page": page,
            "page_size": min(page_size, 200)  # Docebo typically limits to 200
        })
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get repository materials: {e}")
    
    def _get_all_paginated_results(
        self, 
        url: str, 
        base_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Helper method to fetch all pages of results for central repository
        
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
        debug_info = []
        
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
                
                # Debug info for this page
                page_debug = {
                    "page": page,
                    "requested_size": page_size,
                    "url": url,
                    "params": params
                }
                
                # Extract data from central repository response structure
                if 'data' in result and isinstance(result['data'], dict) and 'items' in result['data']:
                    # Central repo returns {data: {items: [...], ...}}
                    page_items = result['data']['items']
                    all_data.extend(page_items)
                    
                    # Update debugging info
                    page_debug.update({
                        "items_received": len(page_items),
                        "has_more_data": result['data'].get('has_more_data'),
                        "api_total_count": result['data'].get('total_count'),
                        "api_total_pages": result['data'].get('total_page_count'),
                        "current_page": result['data'].get('current_page')
                    })
                    
                    debug_info.append(page_debug)
                    
                    # Update totals from API
                    if 'total_count' in result['data']:
                        total_count = result['data']['total_count']
                    if 'total_page_count' in result['data']:
                        total_pages = result['data']['total_page_count']
                    
                    # Check termination conditions
                    has_more = result['data'].get('has_more_data', False)
                    
                    # Stop if API says no more data
                    if not has_more:
                        break
                    
                    # Stop if we got fewer items than requested (end of data)
                    if len(page_items) < page_size:
                        break
                        
                    # Stop if we've hit the total page count
                    if total_pages and page >= total_pages:
                        break
                        
                else:
                    # Handle unexpected response structure
                    page_debug["error"] = f"Unexpected response structure: {list(result.keys())}"
                    debug_info.append(page_debug)
                    break
                
                page += 1
                
                # Safety check to prevent infinite loops
                if page > 100:  # Reasonable upper limit
                    page_debug["error"] = "Hit safety limit of 100 pages"
                    debug_info.append(page_debug)
                    break
                    
            except requests.exceptions.RequestException as e:
                page_debug["error"] = str(e)
                debug_info.append(page_debug)
                raise Exception(f"Failed to fetch page {page}: {e}")
        
        # Return the combined result with debug info
        return {
            "data": all_data,
            "total_count": total_count or len(all_data),
            "total_pages": total_pages or page,
            "current_page": "all", 
            "page_size": len(all_data),
            "fetched_all_pages": True,
            "debug_info": debug_info
        }
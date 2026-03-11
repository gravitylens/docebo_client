#!/usr/bin/env python3
"""
LTI Objects Report Script

This script generates a markdown table report of all LTI objects in the central repository,
showing the name and number of courses attached to each object.
"""

import os
import sys
from docebo_client.client import DoceboClient

def format_lti_objects_table(lti_objects):
    """Format LTI objects data as a markdown table"""
    
    if not lti_objects.get('data'):
        return "No LTI objects found."
    
    objects = lti_objects['data']
    if isinstance(objects, dict) and 'items' in objects:
        objects = objects['items']
    
    if not objects:
        return "No LTI objects found."
    
    # Create markdown table
    table = ["| Name | Courses |\n", "|------|--------|\n"]
    
    for obj in objects:
        name = obj.get('name', 'Unknown')
        # Get course count from assigned_courses_counts.total
        courses_info = obj.get('assigned_courses_counts', {})
        courses = courses_info.get('total', 0) if courses_info else 0
        
        # Clean up name for markdown (escape pipes)
        name = str(name).replace('|', '\\|')
        table.append(f"| {name} | {courses} |\n")
    
    return ''.join(table)

def main():
    try:
        # Create Docebo client
        client = DoceboClient()
        
        print("Fetching LTI objects from central repository...")
        
        # Get LTI objects with pagination
        lti_objects = client.centralrepo.get_repository_materials(types=['lti'], get_all_pages=True)
        
        # Format as markdown table
        table = format_lti_objects_table(lti_objects)
        
        print("\n# LTI Objects Report\n")
        print(table)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
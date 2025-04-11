from typing import List
import pandas as pd
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from openai import OpenAI

load_dotenv()

def enhance_task_description(title, description, system_prompt):
    """
    Use OpenAI to enhance the task description.
    
    Args:
        title (str): Task title
        description (str): Original task description
        
    Returns:
        str: Enhanced task description
    """
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    prompt = f"""
    Make a detailed description for the following Email campaign
    
    Task Title: {title}
    Original Description: {description}
    
    Provide an enhanced description according to your system prompt.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error enhancing description: {str(e)}")
        return description  # Return original description if enhancement fails

def import_to_clickup(tasks_file_csv, list_id, system_prompt=""):
    """
    Import tasks from a CSV file into ClickUp.
    
    Args:
        tasks_file_csv (str): Path to the CSV file containing tasks
        list_id (str): ClickUp list ID where the task should be created (defaults to your list)
        
    The CSV file should have the following columns:
    - name: Task name
    - description: Task description
    """
    try:
        # Read the CSV file
        df = pd.read_csv(tasks_file_csv)
        
        # ClickUp API endpoint
        base_url = "https://api.clickup.com/api/v2"
        headers = {
            "Authorization": os.getenv('CLICKUP_API_KEY'),
            "Content-Type": "application/json"
        }
        
        # Process each task
        for _, row in df.iterrows():
            # Enhance the description using OpenAI
            enhanced_description = enhance_task_description(
                row['name'],
                row.get('description', 'No description'),
                system_prompt
            )
            
            # Prepare task data
            task_data = {
                "name": row['name'],
                "description": enhanced_description,
                "due_date": int(datetime.today().timestamp() * 1000),
            }
            
            # Create task
            response = requests.post(
                f"{base_url}/list/{list_id}/task",
                headers=headers,
                json=task_data
            )
            
            # Check for errors
            if response.status_code != 200:
                print(f"Error creating task '{row['name']}': {response.text}")
            else:
                print(f"Successfully created task: {row['name']}")
                print(f"Enhanced description: {enhanced_description[:100]}...")  # Print first 100 chars of enhanced description
                
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def get_clickup_lists() -> List[dict]:
    """
    Fetch all lists from your ClickUp workspace and return their details.
    """
    api_key = os.getenv('CLICKUP_API_KEY')
    if not api_key:
        print("Error: CLICKUP_API_KEY not found in environment variables")
        return
        
    base_url = "https://api.clickup.com/api/v2"
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json"
    }

    try:
        # First get the user's teams
        teams_response = requests.get(f"{base_url}/team", headers=headers)
        if teams_response.status_code != 200:
            print(f"Error fetching teams: {teams_response.text}")
            return
            
        teams = teams_response.json()['teams']
        if not teams:
            print("No teams found for this user")
            return
            
        # Use the first team (most users have only one team)
        team_id = teams[0]['id']
        
        # Fetch all spaces for the team
        spaces_response = requests.get(f"{base_url}/team/{team_id}/space", headers=headers)
        if spaces_response.status_code != 200:
            print(f"Error fetching spaces: {spaces_response.text}")
            return
            
        results = []
        spaces = spaces_response.json()['spaces']
        for space in spaces:
            # Fetch all folders in the space
            folders_response = requests.get(f"{base_url}/space/{space['id']}/folder", headers=headers)
            if folders_response.status_code != 200:
                print(f"Error fetching folders for space {space['name']}: {folders_response.text}")
                continue

            folders = folders_response.json()['folders']
            for folder in folders:
                # Fetch all lists in the folder
                lists_response = requests.get(f"{base_url}/folder/{folder['id']}/list", headers=headers)
                if lists_response.status_code != 200:
                    print(f"Error fetching lists for folder {folder['name']}: {lists_response.text}")
                    continue

                lists = lists_response.json()['lists']
                for list_item in lists:
                    results.append({
                        "Name": list_item['name'],
                        "ID": list_item['id'],
                        "Folder": folder['name'],
                        "Space": space['name']
                    })
                    
        return results
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Please check your internet connection and API key permissions")
        return []

# if __name__ == '__main__':
    # Uncomment the line below to see your list details
    # get_clickup_lists()
    
    # Uncomment these lines to import tasks
    # clickup_import_tasks = 'clickup_tasks.csv'
    # import_to_clickup(clickup_import_tasks)
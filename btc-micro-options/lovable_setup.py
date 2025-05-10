import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

LOVABLE_API_URL = "https://api.lovable.dev"
PROJECT_ID = "ada2784e-9a2c-48b3-8c9b-c216960cebfe"

def setup_lovable_integration():
    """Set up Lovable integration with GitHub"""
    api_key = os.getenv('LOVABLE_API_KEY')
    if not api_key:
        print("Error: LOVABLE_API_KEY not found in environment variables")
        return False

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    # Configure GitHub integration
    github_config = {
        'repository': 'willialso/micro-options-pulse-btc5',
        'branch': 'main',
        'auto_deploy': True,
        'build_on_push': True,
        'webhook_enabled': True
    }

    try:
        # Set up GitHub integration
        response = requests.post(
            f'{LOVABLE_API_URL}/projects/{PROJECT_ID}/github',
            headers=headers,
            json=github_config
        )
        response.raise_for_status()
        print("Successfully connected to GitHub repository")

        # Trigger initial build
        build_response = requests.post(
            f'{LOVABLE_API_URL}/projects/{PROJECT_ID}/build',
            headers=headers,
            json={
                'trigger': 'manual',
                'repository': 'willialso/micro-options-pulse-btc5'
            }
        )
        build_response.raise_for_status()
        print("Initial build triggered successfully")

        return True

    except requests.exceptions.RequestException as e:
        print(f"Error setting up Lovable integration: {e}")
        return False

if __name__ == '__main__':
    setup_lovable_integration() 
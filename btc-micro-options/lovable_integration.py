import requests
import os
from functools import wraps
from flask import request, jsonify, session, redirect, url_for

# Lovable configuration
LOVABLE_API_URL = "https://api.lovable.dev"
LOVABLE_PROJECT_ID = "ada2784e-9a2c-48b3-8c9b-c216960cebfe"

def lovable_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'lovable_token' not in session:
            return redirect(url_for('lovable_login'))
        return f(*args, **kwargs)
    return decorated_function

def lovable_login():
    """Handle Lovable OAuth login with GitHub"""
    auth_url = f"{LOVABLE_API_URL}/oauth/authorize"
    client_id = os.getenv('LOVABLE_CLIENT_ID')
    redirect_uri = os.getenv('LOVABLE_REDIRECT_URI')
    
    # Add GitHub as the provider
    return redirect(f"{auth_url}?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&provider=github")

def lovable_callback():
    """Handle Lovable OAuth callback"""
    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'No code provided'}), 400
    
    token_url = f"{LOVABLE_API_URL}/oauth/token"
    data = {
        'client_id': os.getenv('LOVABLE_CLIENT_ID'),
        'client_secret': os.getenv('LOVABLE_CLIENT_SECRET'),
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': os.getenv('LOVABLE_REDIRECT_URI'),
        'provider': 'github'  # Specify GitHub as the provider
    }
    
    response = requests.post(token_url, json=data)
    if response.status_code == 200:
        session['lovable_token'] = response.json()['access_token']
        return redirect(url_for('index'))
    else:
        return jsonify({'error': 'Failed to get access token'}), 400

def lovable_logout():
    """Handle Lovable logout"""
    session.pop('lovable_token', None)
    return redirect(url_for('index'))

def get_lovable_headers():
    """Get headers for Lovable API requests"""
    return {
        'Authorization': f"Bearer {session.get('lovable_token')}",
        'Content-Type': 'application/json'
    }

def sync_with_lovable(data):
    """Sync data with Lovable"""
    sync_url = f"{LOVABLE_API_URL}/projects/{LOVABLE_PROJECT_ID}/sync"
    headers = get_lovable_headers()
    
    try:
        response = requests.post(sync_url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error syncing with Lovable: {e}")
        return None 
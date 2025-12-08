import subprocess
import json
import os
from simple_salesforce import Salesforce

def authenticate():
    """
    This will open a new tab and allow you to authenticate with Okta.
    SF credentials are then stored as a token in your home directory inside a ".sf" folder.

    You must have sf cli installed using brew install sf
    """
    result = subprocess.run([
        'sf', 'org', 'login', 'web',
        '-r', 'https://elastic.my.salesforce.com',
        '-d',
        '-a', 'elastic'
    ], capture_output=True, text=True)

    if result.returncode == 0:
        print("Login successful!")
        print(result.stdout)
    else:
        print("Login failed!")
        print(result.stderr)
        raise Exception("Authentication failed")

def get_token():
    """Get the access token from the sf CLI"""
    result = subprocess.run(
        ['sf', 'org', 'display', '--json', '-o', 'elastic'],
        capture_output=True,
        text=True,
        env={**os.environ, 'NO_COLOR': '1'}
    )

    if result.returncode != 0:
        return None, None

    try:
        org_info = json.loads(result.stdout)
        access_token = org_info['result']['accessToken']
        instance_url = org_info['result']['instanceUrl']
        return access_token, instance_url
    except (json.JSONDecodeError, KeyError):
        return None, None

def validate_token(access_token, instance_url):
    """Check if the token is valid by attempting to connect"""
    try:
        sf = Salesforce(instance_url=instance_url, session_id=access_token)
        # Try a simple query to verify the connection works
        sf.query("SELECT Id FROM User LIMIT 1")
        return True
    except Exception:
        return False

def get_salesforce_connection():
    """
    Get an authenticated Salesforce connection.
    Only authenticates if no valid token exists.
    
    Returns:
        Salesforce: An authenticated Salesforce connection object
    """
    # Try to get existing token
    access_token, instance_url = get_token()
    
    # If token exists, validate it
    if access_token and instance_url:
        if validate_token(access_token, instance_url):
            print("Using existing valid token.")
            return Salesforce(instance_url=instance_url, session_id=access_token)
        else:
            print("Existing token is invalid. Re-authenticating...")
    else:
        print("No existing token found. Authenticating...")
    
    # Authenticate and get new token
    authenticate()
    access_token, instance_url = get_token()
    
    if access_token and instance_url:
        print("Connected!")
        return Salesforce(instance_url=instance_url, session_id=access_token)
    else:
        raise Exception("Failed to retrieve token after authentication")

if __name__ == "__main__":
    # Test the connection
    sf = get_salesforce_connection()
    print(sf)

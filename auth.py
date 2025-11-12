"""
Strava OAuth 2.0 Authentication Module
Handles authorization flow and token management.
"""

import os
import requests
from typing import Dict, Optional


# OAuth Configuration
AUTH_URL = "https://www.strava.com/oauth/authorize"
TOKEN_URL = "https://www.strava.com/oauth/token"
REDIRECT_URI = "http://localhost"


def get_authorization_url(client_id: str) -> str:
    """
    Generate the OAuth authorization URL for the user to visit.

    Args:
        client_id: Strava application client ID

    Returns:
        Authorization URL string
    """
    params = {
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": "activity:read_all,read"
    }

    param_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return f"{AUTH_URL}?{param_string}"


def exchange_code_for_token(client_id: str, client_secret: str, code: str) -> Dict:
    """
    Exchange authorization code for access and refresh tokens.

    Args:
        client_id: Strava application client ID
        client_secret: Strava application client secret
        code: Authorization code from OAuth callback

    Returns:
        Dictionary containing access_token, refresh_token, and expires_at

    Raises:
        requests.RequestException: If the API request fails
    """
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code"
    }

    response = requests.post(TOKEN_URL, data=data)
    response.raise_for_status()

    return response.json()


def refresh_access_token(client_id: str, client_secret: str, refresh_token: str) -> Dict:
    """
    Refresh an expired access token using the refresh token.

    Args:
        client_id: Strava application client ID
        client_secret: Strava application client secret
        refresh_token: Refresh token from previous authentication

    Returns:
        Dictionary containing new access_token, refresh_token, and expires_at

    Raises:
        requests.RequestException: If the API request fails
    """
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }

    response = requests.post(TOKEN_URL, data=data)
    response.raise_for_status()

    return response.json()


def save_tokens(tokens: Dict, env_file: str = ".env") -> None:
    """
    Save tokens to .env file.

    Args:
        tokens: Dictionary containing access_token, refresh_token, and expires_at
        env_file: Path to .env file
    """
    # Read existing .env content
    env_content = {}
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_content[key] = value

    # Update tokens
    env_content['STRAVA_ACCESS_TOKEN'] = tokens.get('access_token', '')
    env_content['STRAVA_REFRESH_TOKEN'] = tokens.get('refresh_token', '')
    env_content['STRAVA_TOKEN_EXPIRES_AT'] = str(tokens.get('expires_at', ''))

    # Write back to file
    with open(env_file, 'w') as f:
        for key, value in env_content.items():
            f.write(f"{key}={value}\n")


def load_tokens(env_file: str = ".env") -> Optional[Dict]:
    """
    Load tokens from .env file.

    Args:
        env_file: Path to .env file

    Returns:
        Dictionary containing access_token, refresh_token, and expires_at, or None if not found
    """
    if not os.path.exists(env_file):
        return None

    tokens = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                if key == 'STRAVA_ACCESS_TOKEN':
                    tokens['access_token'] = value
                elif key == 'STRAVA_REFRESH_TOKEN':
                    tokens['refresh_token'] = value
                elif key == 'STRAVA_TOKEN_EXPIRES_AT':
                    tokens['expires_at'] = int(value) if value else 0

    if 'access_token' in tokens and 'refresh_token' in tokens:
        return tokens

    return None


def load_credentials(env_file: str = ".env") -> Optional[Dict]:
    """
    Load client credentials from .env file.

    Args:
        env_file: Path to .env file

    Returns:
        Dictionary containing client_id and client_secret, or None if not found
    """
    if not os.path.exists(env_file):
        return None

    credentials = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                if key == 'STRAVA_CLIENT_ID':
                    credentials['client_id'] = value
                elif key == 'STRAVA_CLIENT_SECRET':
                    credentials['client_secret'] = value

    if 'client_id' in credentials and 'client_secret' in credentials:
        return credentials

    return None

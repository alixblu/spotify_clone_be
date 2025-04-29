import requests
from django.conf import settings
import os
import sys
from django.core.cache import cache
sys.path.append('/home/alixblu/project/Spotify/backend')  # Add project path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')


SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

import base64

def fetch_new_token():
    """Fetch a new Spotify API access token."""
    auth_url = SPOTIFY_TOKEN_URL
    data = {"grant_type": "client_credentials"}
    
    # Correctly encode credentials for Spotify authentication
    client_credentials = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
    encoded_credentials = base64.b64encode(client_credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(auth_url, data=data, headers=headers)
    
    if response.status_code == 200:
        token_info = response.json()
        return token_info.get("access_token")
    else:
        raise Exception(f"Failed to fetch access token: {response.json()}")

def get_spotify_access_token():
    token = cache.get("spotify_access_token")
    if not token:
        token = fetch_new_token()  # Function to get a new token
        cache.set("spotify_access_token", token, timeout=3600)
    return token



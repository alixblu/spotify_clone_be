import requests
from django.conf import settings
import os
import sys

sys.path.append('/home/alixblu/project/Spotify/backend')  # Add project path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

def get_spotify_access_token():
    """Fetch the Spotify API access token."""
    response = requests.post(
        SPOTIFY_TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=(settings.SPOTIFY_CLIENT_ID, settings.SPOTIFY_CLIENT_SECRET)
    )
    token_info = response.json()
    if "access_token" in token_info:
        return token_info["access_token"]
    else:
        raise Exception("Failed to fetch access token")

def get_most_played_albums():
    """Fetch most-played albums from Spotify."""
    access_token = get_spotify_access_token()
    url = "https://api.spotify.com/v1/browse/new-releases"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.json()  # Return raw API data

def get_playlists():
    """Fetch user's playlists from Spotify."""
    access_token = get_spotify_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.spotify.com/v1/me/playlists", headers=headers)
    return response.json()
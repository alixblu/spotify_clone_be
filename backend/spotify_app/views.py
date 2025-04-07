# Create your views here.
##########
from django.shortcuts import render
from django.http import JsonResponse
import requests
from django.conf import settings
from django.shortcuts import redirect
from datetime import datetime, timedelta
from pymongo import MongoClient
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from django.views.decorators.csrf import csrf_exempt

import json
from django.http import JsonResponse

@csrf_exempt
def index(request):
    return JsonResponse({"message": "Welcome to Spotify Clone!"})

import requests
from django.http import JsonResponse

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
CLIENT_ID = settings.SPOTIFY_CLIENT_ID
CLIENT_SECRET = settings.SPOTIFY_CLIENT_SECRET

def get_spotify_token():
    # Request for Spotify Access Token using Client Credentials Flow
    response = requests.post(
        SPOTIFY_TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=(CLIENT_ID, CLIENT_SECRET)
    )
    token_info = response.json()
    if "access_token" in token_info:
        return token_info["access_token"]
    else:
        raise Exception(f"Failed to fetch access token: {token_info.get('error', 'Unknown error')}")

def get_playlists():
    access_token = get_spotify_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get("https://api.spotify.com/v1/me/playlists", headers=headers)
    return response.json()

client = MongoClient(settings.DATABASE_URL)
db = client.spotify

@csrf_exempt
def custom_login(request):
    if request.method == "POST":
        body = json.loads(request.body)
        email = body.get("email")
        password = body.get("password")

        user = db.users.find_one({"email": email})

        if user:
            if user["password"] == password:
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"success": False, "error": "Invalid credentials"})
        else:
            return JsonResponse({"success": False, "error": "User not found"})
    return JsonResponse({"error": "Invalid request method"}, status=405)

@csrf_exempt
def custom_register(request):
    if request.method == "POST":
        body = json.loads(request.body)
        email = body.get("email")
        password = body.get("password")

        # Check if the user already exists
        user = db.users.find_one({"email": email})
        if user:
            return JsonResponse({"success": False, "error": "User already exists"})
        
        # Add new user to database
        db.users.insert_one({"email": email, "password": password, "created_at": datetime.now()})
        return JsonResponse({"success": True})
    return JsonResponse({"error": "Invalid request method"}, status=405)
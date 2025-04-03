#from django.shortcuts import render

# Create your views here.
##########
from django.shortcuts import render
from django.http import JsonResponse

def index(request):
    return JsonResponse({"message": "Welcome to Spotify Clone!"})

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def search_songs(query):
    sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
        client_id='<your_client_id>',
        client_secret='<your_client_secret>'
    ))
    results = sp.search(q=query, type='track', limit=10)
    return results['tracks']['items']
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import get_spotify_access_token  

SPOTIFY_SEARCH_URL = "https://api.spotify.com/v1/search"

def search_edm_artists(request):
    """Search for EDM artists using the Spotify API."""
    access_token = get_spotify_access_token()
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"q": "genre:edm", "type": "artist", "limit": 10}  # Adjust limit as needed

    response = requests.get(SPOTIFY_SEARCH_URL, headers=headers, params=params)

    if response.status_code != 200:
        return {"error": f"Spotify API returned {response.status_code}"}

    artists_data = response.json()["artists"]["items"]

    # Format artist data
    artists = [
        {
            "artist_id": artist["id"],
            "name": artist["name"],
            "genre": "EDM",
            "CoverImage": artist["images"][0]["url"] if artist["images"] else None,
            "label": "Nghệ sĩ",
        }
        for artist in artists_data
    ]
    
    return JsonResponse(artists, safe=False)

@csrf_exempt
def fetch_artist_top_tracks(request, artist_id):
    access_token = get_spotify_access_token()
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"market": "VN"}  # Replace with your preferred market (e.g., US, VN)

    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return JsonResponse({"error": f"Spotify API returned {response.status_code}"}, status=response.status_code)

    tracks_data = response.json()["tracks"]
    formatted_tracks = [
        {
            "SongID": track["id"],
            "Title": track["name"],
            "Duration": track["duration_ms"] // 1000,  # Convert ms to seconds
            "AudioFile": track["preview_url"],  # Spotify's preview audio file
            "cover_image": track["album"]["images"][0]["url"] if track["album"]["images"] else None,
        }
        for track in tracks_data
    ]

    return JsonResponse(formatted_tracks, safe=False)

@csrf_exempt
# its works, dont touch it
def fetch_new_releases(request):
    access_token = get_spotify_access_token()  # Ensure this function works correctly
    new_releases_url = "https://api.spotify.com/v1/browse/new-releases"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(new_releases_url, headers=headers)

    # Check for invalid response
    if response.status_code != 200:
        return JsonResponse({"error": f"Spotify API returned {response.status_code}"}, status=response.status_code)

    new_releases_data = response.json()

    # Debug: Print the response to see the structure
    print(new_releases_data)

    # Extract albums from the response
    try:
        albums = new_releases_data["albums"]["items"]
        formatted_albums = [
            {
                "AlbumID": album["id"],
                "Title": album["name"],
                "Artist": ", ".join(artist["name"] for artist in album["artists"]),
                "CoverImage": album["images"][0]["url"] if album["images"] else None,
                "ReleaseDate": album["release_date"],
                "TotalTracks": album["total_tracks"],

            }
            for album in albums
        ]
        return JsonResponse(formatted_albums, safe=False)
    except KeyError as e:
        return JsonResponse({"error": f"Failed to fetch new releases: {str(e)}"}, status=500)
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
        return JsonResponse({"error": f"Spotify API returned {response.status_code}"}, status=response.status_code)

    artists_data = response.json()["artists"]["items"]

    # Format artist data
    artists = [
        {
            "_id": artist["id"],  # Matches "id" attribute
            "artist_name": artist["name"],  # Matches "artist_name" attribute
            "profile_img": artist["images"][0]["url"] if artist["images"] else None,  # Matches "profile_img" attribute
            "biography": None,  # Assuming Spotify API doesn't provide artist biography
            "label": "Artist",  # Matches "label" attribute with default value
            "isfromDB": False,  # Assuming fetched artists are from Spotify API
            "isHidden": False,  # Assuming artists are not hidden by default
        }
        for artist in artists_data
    ]
    
    return JsonResponse(artists, safe=False)




# @csrf_exempt
# def fetch_artist_top_tracks(request, artist_id):
#     access_token = get_spotify_access_token()
#     url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks"
#     headers = {"Authorization": f"Bearer {access_token}"}
#     params = {"market": "VN"}  # Replace with your preferred market (e.g., US, VN)

#     response = requests.get(url, headers=headers, params=params)
#     if response.status_code != 200:
#         return JsonResponse({"error": f"Spotify API returned {response.status_code}"}, status=response.status_code)

#     tracks_data = response.json()["tracks"]
#     formatted_tracks = [
#         {
#             "SongID": track["id"],
#             "Title": track["name"],
#             "Duration": track["duration_ms"] // 1000,  # Convert ms to seconds
#             "AudioFile": track["preview_url"],  # Spotify's preview audio file
#             "cover_image": track["album"]["images"][0]["url"] if track["album"]["images"] else None,
#         }
#         for track in tracks_data
#     ]

#     return JsonResponse(formatted_tracks, safe=False)
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
            "_id": track["id"],  # Matches "id" attribute
            "album_id": track["album"]["id"],  # Matches "album_id" attribute from songs table
            "title": track["name"],  # Matches "title" attribute
            "duration": track["duration_ms"] // 1000,  # Convert ms to seconds, matches "duration" attribute
            "audio_file": track["preview_url"],  # Spotify's preview audio file, matches "audio_file"
            "img": track["album"]["images"][0]["url"] if track["album"]["images"] else None,  # Matches "img"
            "isfromDB": False,  # Assuming tracks fetched are from Spotify API
            "uploaded_by": None,  # As tracks from Spotify aren’t user-uploaded
            "created_at": None,  # Spotify tracks don’t have a creation timestamp
            "isHidden": False,  # Assuming tracks are not hidden by default
        }
        for track in tracks_data
    ]

    return JsonResponse(formatted_tracks, safe=False)



@csrf_exempt
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
                "_id": album["id"],  # Matches "id" attribute
                "album_name": album["name"],  # Matches "album_name" attribute
                "artist_id": album["artists"][0]["id"],  # Fetch the first artist ID (assuming one artist per album)
                "artist_name": ", ".join(artist["name"] for artist in album["artists"]),  # Matches "artist_name" attribute
                "cover_img": album["images"][0]["url"] if album["images"] else None,  # Matches "cover_img" attribute
                "release_date": album["release_date"],  # Matches "release_date" attribute
                "total_tracks": album["total_tracks"],  # Matches "total_tracks" attribute
                "isfromDB": False,  # Assuming new releases are not from the DB
                "isHidden": False,  # Assuming new releases are not hidden
            }
            for album in albums
        ]
        return JsonResponse(formatted_albums, safe=False)
    except KeyError as e:
        return JsonResponse({"error": f"Failed to fetch new releases: {str(e)}"}, status=500)
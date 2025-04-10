import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import get_spotify_access_token  # Ensure this function is defined correctly
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
                "AlbumID": album["id"],
                "Title": album["name"],
                "Artist": ", ".join(artist["name"] for artist in album["artists"]),
                "CoverImage": album["images"][0]["url"] if album["images"] else None,
                "ReleaseDate": album["release_date"],
                "TotalTracks": album["total_tracks"],
                "SpotifyURL": album["external_urls"]["spotify"],
            }
            for album in albums
        ]
        return JsonResponse(formatted_albums, safe=False)
    except KeyError as e:
        return JsonResponse({"error": f"Failed to fetch new releases: {str(e)}"}, status=500)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Album
from .serializers import AlbumSerializer
from bson import ObjectId

@api_view(['POST'])
def create_album(request):
    """ Create a new album """
    album_data = {
        'artist_id': request.data.get('artist_id'),
        'album_name': request.data.get('album_name'),
        'artist_name': request.data.get('artist_name'),
        'cover_img': request.data.get('cover_img', None),
        'release_date': request.data.get('release_date'),
        'total_tracks': request.data.get('total_tracks'),
        'isfromDB': request.data.get('isfromDB', True),
        'isHidden': request.data.get('isHidden', False),
    }
    
    serializer = AlbumSerializer(data=album_data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Album created successfully!", "data": serializer.data}, status=201)
    
    return Response(serializer.errors, status=400)

@api_view(['GET'])
def list_albums(request):
    """ Retrieve all albums """
    albums = Album.objects.all()
    serializer = AlbumSerializer(albums, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def get_album(request, album_id):
    """ Retrieve a specific album by ID """
    try:
        album = Album.objects.get(_id=ObjectId(album_id))
        serializer = AlbumSerializer(album)
        return Response(serializer.data)
    except Album.DoesNotExist:
        return Response({"error": "Album not found"}, status=404)

@api_view(['PUT'])
def update_album(request, album_id):
    """ Update album details """
    try:
        album = Album.objects.get(_id=ObjectId(album_id))
        serializer = AlbumSerializer(album, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Album updated!", "data": serializer.data})
        return Response(serializer.errors, status=400)
    except Album.DoesNotExist:
        return Response({"error": "Album not found"}, status=404)

@api_view(['DELETE'])
def delete_album(request, album_id):
    """ Delete an album """
    try:
        album = Album.objects.get(_id=ObjectId(album_id))
        album.delete()
        return Response({"message": "Album deleted successfully!"})
    except Album.DoesNotExist:
        return Response({"error": "Album not found"}, status=404)
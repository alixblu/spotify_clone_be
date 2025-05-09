from rest_framework import serializers
from music_library.models import ArtistPerform

class ArtistPerformSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArtistPerform
        fields = '__all__'

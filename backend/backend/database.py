from pymongo import MongoClient
from django.conf import settings

client = MongoClient(settings.DATABASE_URL)
db = client.spotify
print(settings.DATABASE_URL)  # Test if database URL is accessible
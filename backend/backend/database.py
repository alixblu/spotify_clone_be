from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017', serverSelectionTimeoutMS=5000)
try:
    client.admin.command('ping')
    print("MongoDB is reachable")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv('MONGODB_URI')
if not uri:
    raise ValueError("MONGODB_URI environment variable not found")

# Create a MongoClient
client = MongoClient(uri, server_api=ServerApi('1'))

# Ping to verify connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. Successfully connected to MongoDB!")
except Exception as e:
    print("Connection failed:", e)

# Select your database
db = client['user']
users_collection = db['user']
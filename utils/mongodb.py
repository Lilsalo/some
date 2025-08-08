from pymongo import MongoClient
from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("DB_NAME")

if not MONGODB_URI or not DB_NAME:
    raise ValueError("MONGODB_URI and DB_NAME must be set in the environment variables.")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

def get_collection(name: str):
    """Return a MongoDB collection by name."""
    return db[name]

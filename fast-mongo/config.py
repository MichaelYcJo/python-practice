import os
from pathlib import Path
from pymongo.mongo_client import MongoClient
from dotenv import load_dotenv

current_file_path = Path(__file__).resolve()
BASE_DIR = current_file_path.parent.parent.parent

load_dotenv(os.path.join(BASE_DIR, ".env"))

DATABASE_URL = os.environ.get("DATABASE_URL")

# Create a new client and connect to the server
client = MongoClient(DATABASE_URL)

db = client.todo_db
collection = db("todo_data")

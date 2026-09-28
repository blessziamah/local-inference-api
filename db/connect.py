import os
from pymongo import MongoClient


def get_db():
    database_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    client = MongoClient(database_uri)

    database_name = os.getenv("MONGODB_DB_NAME", "local_inference_api")
    database = client[database_name]

    return database

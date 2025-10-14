from pymongo import MongoClient


def get_db():
    database_uri = "mongodb://localhost:27017/"
    client = MongoClient(database_uri)

    database = client["BLACKSTAR_AI"]

    return database
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE = os.getenv("DATABASE")

client = MongoClient(MONGO_URI, maxPoolSize=50, minPoolSize=5)


def connect(collection_name: str) -> tuple[Collection, MongoClient]:
    try:
        db: Database = client[DATABASE]
        collection: Collection = db[collection_name]
        return collection, client
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise
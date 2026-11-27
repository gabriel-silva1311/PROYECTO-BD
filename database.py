import os
import certifi
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
ca = certifi.where()

def dbConnection():
    db = None
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=ca)
        db = client[os.getenv("DB_NAME", "heladeria")]
    except Exception:
        print("Error de conexion con la bdd")
    return db
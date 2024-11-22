from pymongo import MongoClient
import os

os.getenv('')

def upload_to_databases(data_list):
    # MongoDB 업로드
    client = MongoClient("mongodb://localhost:27017/")
    db = client["my_database"]
    collection = db["stores"]
    collection.insert_many(data_list)
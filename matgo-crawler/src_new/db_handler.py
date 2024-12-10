from pymongo import MongoClient
import os



def upload_to_db(store_list, db_name):
    """
    DB에 Store에 대한 상세 JSON 데이터 삽입

    param:
        
    
    """
    if db_name == False:
        raise ValueError()
    # MongoDB 업로드
    client = MongoClient("mongodb://localhost:27017/")
    db = client["my_database"]
    collection = db["stores"]
    collection.insert_many(data_list)


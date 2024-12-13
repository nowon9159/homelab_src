# 데이터 저장 로직
from pymongo import MongoClient
import os

## DB
mongo_ip = "127.0.0.1"
mongo_port = 40441
mongo_username = os.getenv("MONGO_DB_USERNAME")
mongo_pw = os.getenv("MONGO_DB_PW")
mongo_client_url = f"mongodb+srv://{mongo_username}:{mongo_pw}@cluster0.qehwj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"


def conn_mongodb(collection_name, detail_info_list):
    client = MongoClient(mongo_client_url, tls=True, tlsAllowInvalidCertificates=True)
    db = client.matgo
    try:
        collection = db[collection_name]
        collection.insert_many(detail_info_list)
        print(f"\n데이터가 '{collection_name}' 컬렉션에 성공적으로 삽입되었습니다.", "\n", detail_info_list, "\n")
    except Exception as e:
        print(f"MongoDB의 '{collection_name}' 컬렉션에 데이터 삽입 중 오류 발생:", e)

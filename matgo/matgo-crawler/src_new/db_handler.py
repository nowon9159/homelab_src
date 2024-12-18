from pymongo import MongoClient
from config import MONGO_DB_CLIENT_URL

mongo_client_url = MONGO_DB_CLIENT_URL
client = MongoClient(mongo_client_url, tls=True, tlsAllowInvalidCertificates=True)

def conn_mongodb(collection_name, detail_info_list):
    db = client.matgo
    try:
        collection = db[collection_name]
        collection.insert_many(detail_info_list)
        print(f"\n데이터가 '{collection_name}' 컬렉션에 성공적으로 삽입되었습니다.", "\n", detail_info_list, "\n")
    except Exception as e:
        print(f"MongoDB의 '{collection_name}' 컬렉션에 데이터 삽입 중 오류 발생:", e)

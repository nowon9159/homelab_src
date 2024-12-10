from dotenv import load_dotenv
import os

load_dotenv()

# Crawler
KEYWORD = "양천향교역 김치찌개"

# DB
# MONGO_CLIENT_URI = "mongodb://localhost:27017" # 192.168.0.100
MONGO_CLIENT_URI = os.getenv("MONGO_CLIENT_URI")
MONGO_COLL_STORE_INFO = "store_information"
MONGO_COLL_IMG_META = "img_metadata"

# AI
TEXT_QUERY_FILE = "./matgo-crawler/src/food_categories.txt"

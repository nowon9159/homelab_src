from crawler import Crawler
from ai_analyser import process_images
from db_handler import save_to_mongo
from config import MONGO_URI

def main():
    # 크롤러 초기화
    crawler = Crawler()
    
    # 크롤링 작업 수행
    store_data = crawler.run_crawling("서울 맛집")
    
    # 이미지 처리
    for store in store_data:
        store['filtered_images'] = process_images(store['image_urls'])
    
    # MongoDB에 저장
    save_to_mongo(MONGO_URI, "store_information", store_data)

if __name__ == "__main__":
    main()
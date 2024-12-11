# 크롤러 시작점
from store_info.spider import MySpider
from store_info.settings import Settings

def main():
    settings = Settings()
    spider = MySpider(settings)
    spider.start()

if __name__ == "__main__":
    main()
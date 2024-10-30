# 로직 정리
# 1. 드라이버 설정
# 2. 키워드 기반 네이버 map URL 접속
# 3. 현재 페이지에 있는 모든 가게 데이터에 대한 상세 정보 가져오기
#     3.1 가게 클릭
#     3.2 가게 정보 메타데이터에 리스트에 담기 
#         3.2.1 가져와야하는 메타데이터 {
#             "store_id": ,
#             "store_name": ,
#             "location": ,
#             "open_info": ,
#             "review_count": ,
#             "store_id": ,
#             "store_id": ,
#         }
# 4. 현재 페이지 모두 수행했다면 다음 페이지도 수행 (리스트 길이 100 일때 중지)
# 5. 메타데이터 리스트 안의 오브젝트 MongoDB에 하나하나 담기
# f-1. filter 적용하려면 이와 같은 url 사용 "https://pcmap.place.naver.com/restaurant/list?query=%EB%8F%88%EC%B9%B4%EC%B8%A0&x=127.161762930&y=35.849829071&entry=bmp&rank={"요즘뜨는"}&hours={"24시간%20영업"}"
# f-2. 

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup

from selenium.webdriver.support.ui import WebDriverWait
# expected_conditions (EC): Selenium에서 제공하는 여러 가지 조건을 정의한 모듈
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains

from urllib.parse import urlparse, urlunparse # url query 정리
import json

# ENV

KEYWORD = "한식"
#SEARCH_URL = f"https://pcmap.place.naver.com/restaurant/list?query={KEYWORD}"
SEARCH_URL = f"https://map.naver.com/p/search/%EA%B9%80%EC%B9%98/place/31894752?c=15.00,0,0,0,dh&placePath=%2Fphoto%3Fentry%253Dbmp"
IMAGE_LIST = []


# Driver
options = webdriver.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')   # 차단 방지 user-agent 설정
options.add_argument("--start-maximized")   # 화면 크게
options.add_argument("disable-gpu")

options.add_experimental_option("detach", True) # 자동종료 방지(드라이버 유지)


driver = webdriver.Chrome(options=options)

driver.get(url=SEARCH_URL)

# 화면 스크롤
def scroll_list() :
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app-root"]/div')))

    scroll_container = driver.find_element(By.CSS_SELECTOR, ".Ryr1F")
    # execute_script = js 실행.
    last_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)
    # 스크롤
    while True:
            # 요소 내에서 아래로 3000px 스크롤
            driver.execute_script("arguments[0].scrollTop += 3000;", scroll_container)
            # 페이지 로드를 기다림
            time.sleep(0.5)  # 동적 콘텐츠 로드 시간에 따라 조절
            # 스크롤 높이 계산
            new_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)
            # 스크롤이 더 이상 늘어나지 않으면 루프 종료
            if new_height == last_height:
                break
            last_height = new_height

def move_nextpage():
    return "asd"

def switch_left():
    # Iframe 왼쪽 포커스
    driver.switch_to.parent_frame()
    iframe = driver.find_element(By.XPATH,'//*[@id="searchIframe"]')
    driver.switch_to.frame(iframe)

def switch_right():
    # Iframe 오른쪽 포커스
    driver.switch_to.parent_frame()
    iframe = driver.find_element(By.XPATH,'//*[@id="entryIframe"]')
    driver.switch_to.frame(iframe)

# bs4 parsing
def parsing_page():

    # 검색 결과 창을 html로 추출
    results_html = driver.page_source

    # parsing to bs4
    soup = BeautifulSoup(results_html, 'html.parser')
    
    return soup


def crwl_data(ele):
    result_items = ele.find_all('li', class_='rTjJo')
    for index, item in enumerate(result_items, start=1):
            restaurant_name = item.find('span', class_="TYaxT") # 상호명
            # 영업 여부
            try :
                isOpen = item.find('span', class_="MqNOY").get_text()
            except :
                isOpen = None
            # 별점 
            try :
                rating_value = item.find('span', class_="orXYY").get_text().replace("별점","").strip()
            except :
                rating_value = None
            # 리뷰
            reviews_ele = item.find('div', class_="MVx6e")
            for item in reviews_ele:
                if len(item['class']) == 1: #fix 방문자 / 블로그 리뷰 분리 조건문 추가 필요
                    print(item.get_text().replace("리뷰","").strip())
                    reviews_value = item.get_text().replace("리뷰","").strip()
            
            print(index, ".", restaurant_name.get_text(), "\n 영업여부 :", isOpen, "\n 별점 :", rating_value, "\n 리뷰 수 : "+reviews_value)

def crawling_start():
    scroll_list()
    
    parsing_html = parsing_page()

    crwl_data(ele=parsing_html)

    # 드라이버 종료
    driver.quit()

crawling_start()
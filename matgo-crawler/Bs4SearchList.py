from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
# expected_conditions (EC): Selenium에서 제공하는 여러 가지 조건을 정의한 모듈
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import sys
import time

# 상수 (전주역 테스트용 좌표)
KEYWORD = "돈카츠"
# URL = f"https://map.naver.com/restaurant/list?query={KEYWORD}&x=126.97828200000112&y=37.56846119999963&clientX=126.97825&clientY=37.566551"
COORD_X = "127.161762930"
COORD_Y = "35.849829071"
URL = f"https://pcmap.place.naver.com/restaurant/list?query={KEYWORD}&x={COORD_X}&y={COORD_Y}"
WAIT_TIMEOUT = 10 ## 대기 시간(초)
# 파라미터로 데이터 입력 받기
# index 0: file path
# KEYWORD = sys.argv[1:]
# COORD_X = sys.argc[2:]
# COORD_Y = sys.argc[3:]
# 옵션 설정
options = Options()
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3') # 차단 방지 user-agent 설정
options.add_argument("--start-maximized") # 화면 크게
options.add_experimental_option("detach", True) # 자동종료 방지

# run webdriver
driver = webdriver.Chrome(options=options)
driver.get(url = URL)

# 화면 스크롤
def scroll_list() :
    wait = WebDriverWait(driver, WAIT_TIMEOUT)
    wait.until(EC.presence_of_element_located(By.XPATH, '//*[@id="app-root"]/div'))

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

    parsing_page()

# bs4 parsing
def parsing_page():
    # 검색 결과 창을 html로 추출
    results_html = driver.page_source
    # parsing to bs4
    soup = BeautifulSoup(results_html, 'html.parser')
    crwl_data(soup)


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

# test
scroll_list()
# 드라이버 종료
driver.quit()
### 기존 place -> map에 iframe으로 붙은 형태
### place 서치 시 pcmap으로 리다이렉트 되며 정보 조회됨
### 검색명에 따라 좌측 iframe의 DOM 구조가 바뀜 (list page or detail page )

# 기대 json data에 따른 로직 변경 필요
## 1. 현재는 json data를 한개만 담아서 전역변수인 img_list에 복수의 값을 담는데, 이미지 url 하나 당 ObjectId 하나가 되어야 함
## 1.1 1번을 만족하려면 현재 select_tab_img() 로직을 조금 수정해서 current_img 전역 변수에 하나씩 담고 하나씩 변경하는 식으로 오브젝트 여러개를 만들어 pymongo의 insert_many()를 이용해 리스트 안에 있는 여러 개의 object를 insert 해야할 듯

# lib
## selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC # expected_conditions (EC): Selenium에서 제공하는 여러 가지 조건을 정의한 모듈
from selenium.webdriver import ActionChains
from urllib.parse import urlparse, urlunparse # url query 정리
import re
import json

## mongodb
from pymongo import MongoClient
from bson import json_util
## mysql
import mysql.connector
from mysql.connector import Error

# 상수
## 크롤링
WAIT_TIMEOUT = 15 ## 대기 시간(초)
KEYWORD = "맥도날드 명동" ## 테스트코드 맥도날드 명동점
URL = f"https://map.naver.com/restaurant/list?query={KEYWORD}" # https://pcmap.place.naver.com/place/list?query <-- 해당 url도 가능

## DB
mongo_ip = "127.0.0.1"
mongo_port = 40441
mysql_ip = "127.0.0.1"
mysql_port = 40120
mysql_admin = "test"
mysql_pw = "1q2w3e4r!"
mysql_db_name = "matgo"

# 드라이버 실행 및 옵션 정의
options = webdriver.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')   # 차단 방지 user-agent 설정
options.add_argument("--start-maximized")   # 화면 크게
options.add_experimental_option("detach", True) # 자동종료 방지(드라이버 유지)
options.add_argument("headless")
driver = webdriver.Chrome(options=options)

# pymongo client 생성
client = MongoClient(mongo_ip, mongo_port) # minikube service mongodb --url

# 페이지 스크롤
def page_scroll(class_name):
    scroll_container = driver.find_element(By.CSS_SELECTOR, f".{class_name}")
    last_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container) # execute_script = js 실행.

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

# iframe 엘리먼트 지정
def focus_iframe(type):
    driver.switch_to.parent_frame()
    if type == 'list':
        iframe = driver.find_element(By.XPATH,'//*[@id="searchIframe"]')
    elif type == 'detail':
        wait = WebDriverWait(driver, WAIT_TIMEOUT)
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="entryIframe"]')))
        
        iframe = driver.find_element(By.XPATH,'//*[@id="entryIframe"]')
    driver.switch_to.frame(iframe)

# img_list의 모든 URL에 대해 dict 리스트 구성
def detail_info():
    focus_iframe('detail')

    # 현재 URL 가져오기 및 처리
    current_url = driver.current_url
    parsed_url = urlparse(current_url)
    cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))

    # store_id 추출
    url_path = urlparse(cleaned_url).path
    url_path_match = re.search(r'place/(\d+)', url_path)
    store_id = url_path_match.group(1) if url_path_match else None

    # 페이지 소스 가져와 BeautifulSoup로 파싱
    result_page = driver.page_source
    soup = BeautifulSoup(result_page, 'html.parser')
    
    # 가게 상세 정보 추출
    detail_ele = soup.find('div', class_='PIbes')
    detail_addr = detail_ele.find('div', class_='vV_z_').get_text() if detail_ele else None
    current_status = detail_ele.find('em').get_text() if detail_ele else None
    time_ele = soup.find('time', {'aria-hidden': 'true'}).get_text() if detail_ele else None
    strt_time, end_time = (time_ele, None) if current_status == '영업 종료' else (None, time_ele)
    
    # 이미지 리스트 수집
    tab_list = driver.find_elements(By.CSS_SELECTOR, '.veBoZ')
    for tab in tab_list:
        if tab.text == '사진':
            tab.click()
            WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.CLASS_NAME, 'wzrbN')))
            img_elems = driver.find_elements(By.CLASS_NAME, 'wzrbN')
            img_list = [img.find_element(By.XPATH, './/a/img').get_attribute('src') for img in img_elems]
            break

    # img_list의 URL마다 개별 dict 구성
    detail_info_list = []
    for img_url in img_list:
        detail_info = {
            'img_url': img_url,
            'detail_addr': detail_addr,
            'store_id': store_id,
            'current_status': current_status,
            'strt_time': strt_time,
            'end_time': end_time,
            'naver_url': cleaned_url,
            'img_thumbs_url': img_list[0]  # 첫 번째 이미지 썸네일로 설정
        }
        detail_info_list.append(detail_info)
    
    print("Detail info list 구성 완료:", detail_info_list)
    return detail_info_list

# MongoDB에 데이터 삽입 함수
def conn_mongodb(detail_info_list):
    db = client.matgo  # 'matgo'라는 MongoDB 데이터베이스 선택
    try:
        db.metadata.insert_many(detail_info_list)  # 리스트를 insert_many로 삽입
        print("\n", "데이터가 MongoDB에 성공적으로 삽입되었습니다.", detail_info_list, "\n")
    except Exception as e:
        print("MongoDB에 데이터 삽입 중 오류 발생:", e)

def conn_mysql():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=mysql_ip,
            port=mysql_port,
            user=mysql_admin,
            passwd=mysql_pw,
            database=mysql_db_name
        )
        print("MySQL 데이터베이스에 연결됨.")
    except Error as e:
        print(f"오류 발생: '{e}'")
    return connection

def insert_mysql(connection, detail_info_list):
    cursor = connection.cursor()
    insert_query = """
    INSERT INTO your_table_name (img_url, detail_addr, store_id, current_status, strt_time, end_time, naver_url, img_thumbs_url)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """ # 예시 쿼리, 변경 필요
    try:
        for detail_info in detail_info_list:
            cursor.execute(insert_query, (
                detail_info['img_url'],
                detail_info['detail_addr'],
                detail_info['store_id'],
                detail_info['current_status'],
                detail_info['strt_time'],
                detail_info['end_time'],
                detail_info['naver_url'],
                detail_info['img_thumbs_url']
            )) # 예시 쿼리, 변경 필요
        connection.commit()  # 변경 사항 커밋
        print("데이터가 MySQL에 성공적으로 삽입되었습니다.")
    except Error as e:
        print(f"MySQL에 데이터 삽입 중 오류 발생: '{e}'")
    finally:
        cursor.close()

# 크롤링 시작 함수
def crwl_data():
    driver.get(url=URL)
    WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.XPATH, '//*[@id="section_content"]/div')))
    try:
        driver.find_element(By.XPATH, '//*[@id="searchIframe"]')
        focus_iframe('list')
        page_scroll("Ryr1F")
        search_restaurant = driver.find_element(By.XPATH, f'//*[contains(text(),"{KEYWORD}")]')
        select_restaurant = search_restaurant.find_element(By.XPATH, '../../../div/div/span')
        
        driver.switch_to.parent_frame()
        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".SEARCH_MARKER > div")))
        focus_iframe('list')

        actions = ActionChains(driver)
        actions.click(select_restaurant).perform()
        
    except Exception as e:
        print("목록에서 가게 검색에 실패했습니다:", e)

    # 상세 정보 크롤링 및 DB에 저장
    detail_info_list = detail_info()
    conn_mongodb(detail_info_list)


    # mysql에 저장할 때는 detail_info_list 수정 필요
    mysql_connection = conn_mysql()
    insert_mysql(mysql_connection, detail_info_list)

    if mysql_connection:
        mysql_connection.close()  # MySQL 연결 종료

# test
crwl_data()
driver.quit()
### 기존 place -> map에 iframe으로 붙은 형태
### place 서치 시 pcmap으로 리다이렉트 되며 정보 조회됨
### 검색명에 따라 좌측 iframe의 DOM 구조가 바뀜 (list page or detail page )

# TODO List (241111)
## OpenAI 이용한 이미지 분석
### 1. OpenAI API를 이용하면 이미지 분석이 가능할 것이다. 해당 SDK를 이용해 이미지 분석 프롬프트를 날려 이미지 분석을 할것.
## 이미지 url 크롤링 과정 변경
### 1. 현재는 한 페이지의 url만 긁어 오는데 이미지 분석 과정을 앞에 두고 url의 이미지 분석이 완료되어 음식 사진이라고 판별된 url만 dict에 추가
### 2. dict에 추가되고 특정 갯수 x 를 넘지 않는 경우 이미지 불러오기 및 url 추가 과정 반복
## 조건문으로 각 DB insert
### 1. mysql인 경우 특정 로직, mongodb인 경우 특정 로직으로 나누어 변수 생성 및 dict 생성
## 리뷰 추가 사항
### 1. mongodb는 int형, mysql은 str형
### 2. 리뷰 검색해서 1번째 리뷰 긁어오기, mysql 적재, 추후 mongodb collection으로 옮기기
## 모듈화
### 1. mysql 적재, mongodb 적재 로직 나눠서 모듈화

# lib
## selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC # expected_conditions (EC): Selenium에서 제공하는 여러 가지 조건을 정의한 모듈
from selenium.webdriver import ActionChains
from fake_useragent import UserAgent
## mongodb
from pymongo import MongoClient
from bson import json_util
## mysql
import mysql.connector
from mysql.connector import Error
## common
from urllib.parse import urlparse, urlunparse # url query 정리
import time
import re
import json
import random
import os
from dotenv import load_dotenv

# .env 파일 불러오기
load_dotenv()

# 상수
## 크롤링
WAIT_TIMEOUT = random.uniform(10, 11) ## 대기 시간(초)
KEYWORD = "맥도날드 명동" ## 테스트코드 맥도날드 명동점
URL = f"https://map.naver.com/restaurant/list?query={KEYWORD}" # https://pcmap.place.naver.com/place/list?query <-- 해당 url도 가능

## DB
mongo_ip = "127.0.0.1"
mongo_port = 40441
mongo_username = os.getenv("MONGO_DB_USERNAME")
mongo_pw = os.getenv("MONGO_DB_PW")
mongo_client_url = f"mongodb+srv://{mongo_username}:{mongo_pw}@cluster0.qehwj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
mysql_ip = "127.0.0.1"
mysql_port = 40120
mysql_admin = "test"
mysql_pw = "1q2w3e4r!"
mysql_db_name = "matgo"

# 드라이버 실행 및 옵션 정의
ua = UserAgent(platforms="pc", browsers="chrome")
user_agents = ua.random
options = webdriver.ChromeOptions()
options.add_argument(f'--user-agent={user_agents}')
options.add_argument("--start-maximized")   # 화면 크게
options.add_experimental_option("detach", True) # 자동종료 방지(드라이버 유지)
#options.add_argument("--headless=chrome")
driver = webdriver.Chrome(options=options)


# pymongo client 생성
#client = MongoClient(mongo_ip, mongo_port) # minikube service mongodb --url
client = MongoClient(mongo_client_url, tls=True, tlsAllowInvalidCertificates=True)

# 페이지 스크롤
def page_scroll(class_name):
    scroll_container = driver.find_element(By.CSS_SELECTOR, f".{class_name}")
    last_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container) # execute_script = js 실행.

    while True:
            # 요소 내에서 아래로 3000px 스크롤
            driver.execute_script("arguments[0].scrollTop += 3000;", scroll_container)
            # 페이지 로드를 기다림
            time.sleep(random.uniform(1, 2))
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

# 위도 경도 좌표 구하는 탭 추가 후 값 return
def get_lat_lon(input_address):
    lat_lon_url = "https://gps.aply.biz/"
    #driver.execute_script(f'window.open({lat_lon_url});')
    driver.execute_script("window.open('');")
    time.sleep(1)

    driver.switch_to.window(driver.window_handles[-1])  #새로 연 탭으로 이동
    driver.get(url=lat_lon_url)

    address = driver.find_element(By.XPATH, '//*[@id="gtco-header2"]/div/div[3]/div[2]/div[1]/input')

    address.send_keys(input_address)

    driver.find_element(By.XPATH, '//*[@id="btnGetGpsByAddress"]').click()

    wait = WebDriverWait(driver, 5)

    lat = driver.find_element(By.XPATH, '//*[@id="gtco-header2"]/div/div[3]/div[1]/div[1]/input')
    lon = driver.find_element(By.XPATH, '//*[@id="gtco-header2"]/div/div[3]/div[1]/div[2]/input')

    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="askModal"]/div/div/div[2]'))) # 모달 생성 대기

    time.sleep(3)

    lat_value = lat.get_attribute("value")
    lon_value = lon.get_attribute("value")

    time.sleep(1)
    
    driver.close()
    return lat_value, lon_value

# img_list의 모든 URL에 대해 dict 리스트 구성
def detail_info():
    focus_iframe('detail')
    time.sleep(random.uniform(2, 3))

    # 현재 URL 가져오기 및 처리
    current_url = driver.current_url
    parsed_url = urlparse(current_url)
    cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))

    # 페이지 소스 가져와 BeautifulSoup로 파싱
    result_page = driver.page_source
    soup = BeautifulSoup(result_page, 'html.parser')
    
    detail_ele = soup.find('div', class_='PIbes')
    subject_ele = soup.find('div', class_='zD5Nm undefined')

    # 가게 상세 정보 추출
    # common
    url_path = urlparse(cleaned_url).path
    url_path_match = re.search(r'place/(\d+)', url_path)
    store_id = url_path_match.group(1) if url_path_match else None
    # mongo
    detail_addr = detail_ele.find('span', class_='LDgIH').get_text() if detail_ele else None
    current_status = detail_ele.find('em').get_text() if detail_ele else None
    time_ele = soup.find('time', {'aria-hidden': 'true'}).get_text() if detail_ele else None
    strt_time, end_time = (time_ele, None) if current_status == '영업 종료' else (None, time_ele)
    # mysql
    store_nm = subject_ele.find('span', class_='GHAhO').get_text() if subject_ele else None
    address = detail_ele.find('span', class_='LDgIH').get_text() if detail_ele else None
    tel_no = detail_ele.find('span', class_='xlx7Q').get_text() if detail_ele else None
    star_rate = (subject_ele.find('span', class_='PXMot LXIwF').get_text() if subject_ele.find('span', class_='PXMot LXIwF') else "Node")
    category = subject_ele.find('span', class_='lnJFt').get_text() if subject_ele else None
    lat_lon_list = get_lat_lon(input_address=address)
    latitude = lat_lon_list[0]
    longitude = lat_lon_list[1]
    tags = "test"
    driver.switch_to.window(driver.window_handles[0])

    # review_cn 연산
    visitor_review_txt = subject_ele.find('a', attrs={"href": f"/restaurant/{store_id}/review/visitor"}).get_text() if subject_ele else None
    blog_review_txt = subject_ele.find('a', attrs={"href": f"/restaurant/{store_id}/review/ugc"}).get_text() if subject_ele else None
    visitor_review_cn = re.search(r'\b\d{1,3}(?:,\d{3})*\b', visitor_review_txt).group()
    blog_review_cn = re.search(r'\b\d{1,3}(?:,\d{3})*\b', blog_review_txt).group()
    review_cn = int(visitor_review_cn.replace(',', '')) + int(blog_review_cn.replace(',', ''))

    # 이미지 리스트 수집
    tab_list = driver.find_elements(By.CSS_SELECTOR, '.veBoZ')
    for tab in tab_list:
        if tab.text == '사진':
            tab.click()
            WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.CLASS_NAME, 'wzrbN')))
            time.sleep(random.uniform(2, 3))
            img_elems = driver.find_elements(By.CLASS_NAME, 'wzrbN')
            img_list = [img.find_element(By.XPATH, './/a/img').get_attribute('src') for img in img_elems]
            time.sleep(0.5)
            break

    # img_list의 URL마다 개별 dict 구성
    mongo_detail_info_list = []
    mysql_detail_info_list = []

    mongo_detail_info = {}
    mysql_detail_info = {}
    
    for img_url in img_list:
        mongo_detail_info = {
            'img_url': img_url,
            'detail_addr': detail_addr,
            'store_id': store_id,
            'current_status': current_status,
            'strt_time': strt_time,
            'end_time': end_time,
            'naver_url': cleaned_url,
            'img_thumbs_url': img_list[0]  # 첫 번째 이미지 썸네일로 설정
        }
        time.sleep(0.2)
        mongo_detail_info_list.append(mongo_detail_info)
    
    mysql_detail_info = {
        'img_url': img_list,
        'store_id': store_id,
        'store_nm': store_nm,
        'tel_no': tel_no,
        'review_cn': review_cn,
        'star_rate': star_rate,
        'latitude': latitude,
        'longitude': longitude,
        'tags': tags,
        'category': category
    }

    print("Detail info list 구성 완료:", mongo_detail_info_list)
    print("Detail info list 구성 완료:", mysql_detail_info)
    return mongo_detail_info_list, mysql_detail_info_list

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
        print(f"MySQL 데이터베이스 연결 오류 발생: '{e}'")
    return connection

def insert_mysql(connection, detail_info_list):
    cursor = connection.cursor()
    insert_query = """
    INSERT INTO store_information (store_id, store_nm, address, tel_no, review_cn, star_rate, latitude, longitude, image_url, tags, category) VALUES (%d, %s, %s, %s, %d, %d, %d, %d, %s, %s, %s)
    """
    try:
        for detail_info in detail_info_list:
            cursor.execute(insert_query, (
                detail_info['store_id'],
                detail_info['store_nm'],
                detail_info['address'],
                detail_info['tel_no'],
                detail_info['review_cn'],
                detail_info['star_rate'],
                detail_info['latitude'],
                detail_info['longitude'],
                detail_info['image_url'],
                detail_info['tags'],
                detail_info['category']
            )) 
        connection.commit()  # 변경 사항 커밋
        print("데이터가 MySQL에 성공적으로 삽입되었습니다.")
    except Error as e:
        print(f"MySQL에 데이터 삽입 중 오류 발생: \n '{e}'")
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

    # 상세 정보 크롤링 및 mongo DB에 저장
    mongo_detail_info_list = detail_info()[0]
    mysql_detail_info_list = detail_info()[1]
    conn_mongodb(mongo_detail_info_list)

    # 상세 정보 크롤링 및 mysql DB에 저장
    mysql_connection = conn_mysql()
    insert_mysql(mysql_connection, mysql_detail_info_list)

    if mysql_connection:
        mysql_connection.close()  # MySQL 연결 종료

# test
crwl_data()
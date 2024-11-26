from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
import config
import random
from fake_useragent import UserAgent
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
import re

class Crawler:
    def __init__(self, driver_path):
        self.driver = webdriver.Chrome(driver_path)  # 크롬 드라이버 초기화

    def scroll_to_bottom(self, class_name):
        """페이지 끝까지 스크롤"""
        scroll_container = self.driver.find_element(By.CSS_SELECTOR, f".{class_name}")
        last_height = self.driver.execute_script("return arguments[0].scrollHeight", scroll_container) # execute_script = js 실행.

        while True:
            # 요소 내에서 아래로 3000px 스크롤
            self.driver.execute_script("arguments[0].scrollTop += 3000;", scroll_container)
            # 페이지 로드를 기다림
            time.sleep(random.uniform(1, 2))
            # 스크롤 높이 계산
            new_height = self.driver.execute_script("return arguments[0].scrollHeight", scroll_container)

            # 스크롤이 더 이상 늘어나지 않으면 루프 종료
            if new_height == last_height:
                break
            last_height = new_height
    
    def focus_iframe(self, type):
        """iframe 엘리먼트 지정"""
        self.driver.switch_to.parent_frame()
        if type == 'list':
            iframe = self.driver.find_element(By.XPATH,'//*[@id="searchIframe"]')
        elif type == 'detail':
            wait = WebDriverWait(self.driver, random.uniform(10, 11))
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="entryIframe"]')))
            iframe = self.driver.find_element(By.XPATH,'//*[@id="entryIframe"]')
        self.driver.switch_to.frame(iframe)

    def extract_json_data(self):
        """가게 상세 정보를 추출"""
        # 각 가게 정보 추출
        tab_list = self.driver.find_elements(By.CLASS_NAME, 'veBoZ') # 전체 탭 리스트
        current_url = self.driver.current_url # 키워드 기반 현재 url
        parsed_url = urlparse(current_url) # 파싱 url
        cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', '')) # 정리된 url

        page = self.driver.page_source
        soup = BeautifulSoup(page, 'html.parser')

        detail_ele = soup.find('div', class_='PIbes')
        subject_ele = soup.find('div', class_='zD5Nm undefined')

        url_path = urlparse(cleaned_url).path
        url_path_match = re.search(r'place/(\d+)', url_path)
        store_id = url_path_match.group(1) if url_path_match else None

        current_status = detail_ele.find('em').get_text() if detail_ele else None
        time_ele = soup.find('time', {'aria-hidden': 'true'}).get_text() if detail_ele else None
        strt_time, end_time = (time_ele, None) if current_status == '영업 종료' else (None, time_ele)
        store_nm = subject_ele.find('span', class_='GHAhO').get_text() if subject_ele else None
        address = detail_ele.find('span', class_='LDgIH').get_text() if detail_ele else None
        tel_no = detail_ele.find('span', class_='xlx7Q').get_text() if detail_ele else None
        star_rate = (subject_ele.find('span', class_='PXMot LXIwF').get_text() if subject_ele.find('span', class_='PXMot LXIwF') else "Node")
        category = subject_ele.find('span', class_='lnJFt').get_text() if subject_ele else None
        lat_lon_list = self.get_lat_lon(input_address=address)
        latitude = lat_lon_list[0]
        longitude = lat_lon_list[1]

        visitor_review_txt = subject_ele.find('a', attrs={"href": f"/restaurant/{store_id}/review/visitor"}).get_text() if subject_ele else None
        blog_review_txt = subject_ele.find('a', attrs={"href": f"/restaurant/{store_id}/review/ugc"}).get_text() if subject_ele else None
        visitor_review_cn = re.search(r'\b\d{1,3}(?:,\d{3})*\b', visitor_review_txt).group()
        blog_review_cn = re.search(r'\b\d{1,3}(?:,\d{3})*\b', blog_review_txt).group()
        review_cn = int(visitor_review_cn.replace(',', '')) + int(blog_review_cn.replace(',', ''))


        # store_information = {
        #     "store_id": "1398748369",
        #     "store_nm": "김둘레순대국 양천향교점",
        #     "address": "서울 강서구 강서로 433",
        #     "tel_no": "02-868-9515",
        #     "review_cnt": 18732,
        #     "star_rate": "4.9",
        #     "open_info": {
        #         "status": "영업 중",
        #         "strt_time": None,
        #         "end_time": "22:00에 영업 종료"
        #     },
        #     "location": {
        #         "type": "Point",
        #         "coordinates" [경도, 위도]
        #         },
        #     "category": "solo,cupl,lunch,dinner",
        #     "img_url": "main_image_url",
        #     "naver_url": "https://naver.me/F2vnL4TS",
        #     "simple_review": "리뷰 내용"
        # }
        return store_information

    def get_lat_lon(self, input_address):
        lat_lon_url = "https://gps.aply.biz/"
        self.driver.execute_script("window.open('');")
        time.sleep(random.uniform(1, 2))

        wait = WebDriverWait(self.driver, 5)

        self.driver.switch_to.window(self.driver.window_handles[-1])  #새로 연 탭으로 이동
        self.driver.get(url=lat_lon_url)

        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="gtco-header2"]/div/div[3]/div[2]/div[1]/input'))) # address input box 생성 대기
        address_box = self.driver.find_element(By.XPATH, '//*[@id="gtco-header2"]/div/div[3]/div[2]/div[1]/input')# 주소 인풋박스 div 찾기
        address_box.send_keys(input_address)

        self.driver.find_element(By.XPATH, '//*[@id="btnGetGpsByAddress"]').click()

        lat = self.driver.find_element(By.XPATH, '/html/body/div[3]/header/div/div[3]/div[1]/div[1]/input')
        lon = self.driver.find_element(By.XPATH, '/html/body/div[3]/header/div/div[3]/div[1]/div[2]/input')

        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="askModal"]/div/div/div[2]'))) # 모달 생성 대기

        time.sleep(random.uniform(3, 4))

        lat_value = lat.get_attribute("value")
        lon_value = lon.get_attribute("value")

        time.sleep(random.uniform(1, 2))
        
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

        return lat_value, lon_value

    def run_crawling(self, keyword):
        """전체 크롤링 작업 실행"""
        self.driver.get("https://map.naver.com")
        search_box = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "search-input"))
        )
        search_box.send_keys(keyword)
        search_box.submit()

        self.scroll_to_bottom()
        
        store_elements = self.driver.find_elements(By.CLASS_NAME, "store-class")
        stores = []
        for store_element in store_elements[:10]:  # 10개 가게만 처리
            store_element.click()
            self.navigate_to_iframe()
            stores.append(self.extract_store_data(store_element))
            self.driver.switch_to.default_content()
        
        self.driver.quit()
        return stores
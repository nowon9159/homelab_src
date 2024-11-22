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
        self.driver.switch_to.parent_frame()
        if type == 'list':
            iframe = self.driver.find_element(By.XPATH,'//*[@id="searchIframe"]')
        elif type == 'detail':
            wait = WebDriverWait(self.driver, random.uniform(10, 11))
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="entryIframe"]')))
            iframe = self.driver.find_element(By.XPATH,'//*[@id="entryIframe"]')
        self.driver.switch_to.frame(iframe)

    def extract_store_data(self, store_element):
        """가게 상세 정보를 추출"""
        store_data = {
            "name": store_element.find_element(By.CLASS_NAME, "store-name").text,
            "address": store_element.find_element(By.CLASS_NAME, "store-address").text,
            "image_urls": [],  # 추후 추가
        }
        return store_data

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
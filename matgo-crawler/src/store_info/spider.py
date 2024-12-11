# 크롤링 주요 로직 파일
## 클래스 인스턴스 자신을 참조하는 매개변수 self 활용

## selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
## module
from parser import parse_page
from storage import insert_data
## common
from common.utils import Utils
from common.constants import WAIT_TIMEOUT_ONE, WAIT_TIMEOUT_TWO, WAIT_TIMEOUT_TEN, WAIT_TIMEOUT_ELE

class MySpider :
    # 인스턴스 생성 시 호출. setting값 저장
    def __init__(self, settings):
        self.settings = settings
        self.driver = None

    # 상세 정보 크롤링
    def detail_info(self):
        Utils.focus_iframe(self.driver, 'detail')
        tab_list = self.driver.find_elements(By.CLASS_NAME, 'veBoZ')
        
        store_info = parse_page(self.driver, self.settings, tab_list)
        store_info_list = []
        store_info_list.append(store_info)
        print("Detail info list 구성 완료:", store_info_list)
        return store_info_list

    # 검색 리스트 추출
    def crwl_list(self, list):
        for index, store in enumerate(list, start=1):
            self.driver.switch_to.parent_frame()

            Utils.custom_wait(self.driver, (By.CSS_SELECTOR, ".SEARCH_MARKER > div"), WAIT_TIMEOUT_TEN, WAIT_TIMEOUT_ELE)
            
            Utils.focus_iframe(self.driver, 'list')

            self.actions.click(store).perform()
            store_info_list = self.detail_info()

            ## insert to mongoDB
            insert_data("store_information", store_info_list)

            # 가게 5개로 임시 제한
            if index == 5:
                break

    # 옵션 및 드라이버 정의
    def start_driver(self):        
        options = webdriver.ChromeOptions()
        options.add_argument(f'--user-agent={self.settings.USER_AGENT}')

        self.driver = webdriver.Chrome(options=options)
        self.actions = ActionChains(self.driver)  # 액션 체인 초기화

    # 크롤링 시작
    def start_crwl(self):
        self.start_driver()  # 드라이버 시작
        self.driver.get(url=f"{self.settings.BASE_URL}?query={self.settings.KEYWORD}")  # 크롤링할 URL 로드
        
        # 이후 크롤링 로직 추가...
        try:
            self.driver.find_element(By.XPATH, '//*[@id="searchIframe"]')
            Utils.focus_iframe(self.driver, 'list')
            Utils.page_scroll(self.driver, "Ryr1F")

            store_list = self.driver.find_elements(By.CLASS_NAME, 'TYaxT')
            self.crwl_list(store_list)

        except Exception as e:
            print("크롤링 작업이 실패했습니다:", e)
            self.close_crwl()

    # 크롤링 종료
    def close_crwl(self):
        if self.driver:
            self.driver.quit()  # 드라이버 종료
### 기존 place -> map에 iframe으로 붙은 형태
### place 서치 시 pcmap으로 리다이렉트 되며 정보 조회됨
### 검색명에 따라 좌측 iframe의 DOM 구조가 바뀜 (list page or detail page )

### (!!!로직 개선 필요!!!) 
#1 naver map에서 place iframe 타겟 후 서칭
#2 리스트 형식으로 검색될 경우 식당 리스트 추출 
#2-1 상세페이지로 바로 리다이렉트될 경우 상세 정보 크롤링
#3 키워드 필터링 후 click을 통해 상세페이지 iframe으로 이동
#4 상세 정보 크롤링

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

# 상수
WAIT_TIMEOUT = 10 ## 대기 시간(초)
KEYWORD = "맥도날드 명동" ## 테스트코드 맥도날드 명동점
URL = f"https://map.naver.com/restaurant/list?query={KEYWORD}" # https://pcmap.place.naver.com/place/list?query <-- 해당 url도 가능

# 드라이버 실행 및 옵션 정의
options = webdriver.ChromeOptions()
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')   # 차단 방지 user-agent 설정
options.add_argument("--start-maximized")   # 화면 크게
options.add_experimental_option("detach", True) # 자동종료 방지(드라이버 유지)
driver = webdriver.Chrome(options=options)

driver.get(url=URL)

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

# 이미지
img_list = []
def select_tab_img():
    tab_list = driver.find_elements(By.CSS_SELECTOR, '.veBoZ')
    # 사진 탭 진입
    for tab in tab_list:
         if tab.text == '사진':
              tab.click()
              
    wait = WebDriverWait(driver, WAIT_TIMEOUT)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'wzrbN')))
    img_elems = driver.find_elements(By.CLASS_NAME, 'wzrbN')
    for img in img_elems:
        img_src = img.find_element(By.XPATH,'.//a/img').get_attribute('src')
        img_list.append(img_src)

# 상세 정보
def detail_info():
    focus_iframe('detail')
    # 현재 URL 가져오기 (리스트와 같이 나옴) <-- 이해 필요
    current_url = driver.current_url
    parsed_url = urlparse(current_url)
    # 쿼리 문자열 제거
    cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
    
    # parsing to bs4 
    result_page = driver.page_source
    soup = BeautifulSoup(result_page, 'html.parser')
    # wait = WebDriverWait(driver, WAIT_TIMEOUT)
    # wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'PIbes'))) <- 안 잡힘
    detail_ele = soup.find('div', class_='PIbes')   #fix redirect 시 사진 넘어가기 전 상세정보 필요
    
    detail_addr = detail_ele.find('div', class_='vV_z_').getText()  # 상세 주소
    current_status = detail_ele.find('em').get_text()  # 영업 여부
    time_ele = soup.find('time', {'aria-hidden': 'true'}).get_text()   # 영업 시간
    strt_time = None
    end_time = None
    if current_status == '영업 중':
        end_time = time_ele
    elif current_status == '영업 종료':
        strt_time = time_ele
    # img url list
    select_tab_img()

    detail_info = {
         'detail_addr' : detail_addr,
         'current_status' : current_status,
         'strt_time' : strt_time,
         'end_time' : end_time,
         'naver_url' : cleaned_url,
         'img_url' : img_list
    }
    json_detail_info = json.dumps(detail_info, ensure_ascii=False);
    print("dic", json_detail_info)
    return json_detail_info
    # print("상세주소 :"+detail_addr, "\n영업 여부:", current_status, "\n오픈 시간:",strt_time, "\n마감 시간:",end_time, "\n네이버 URL:", cleaned_url, "\n이미지 URL:", img_list)

### 크롤링 시작 함수
def crwl_data():
    wait = WebDriverWait(driver, WAIT_TIMEOUT)
    wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="section_content"]/div')))
    try:
            driver.find_element(By.XPATH, '//*[@id="searchIframe"]')
            focus_iframe('list')
            page_scroll("Ryr1F")
            # try:
            # 키워드 포함 여부 체크 
            search_restaurant = driver.find_element(By.XPATH, f'//*[contains(text(),"{KEYWORD}")]')
            select_restaurant = search_restaurant.find_element(By.XPATH, '../../../div/div/span')
            # 스크롤 이동
            # actions.move_to_element(select_restaurant).perform()
            # 클릭 가능할 때까지 대기
            # wait.until(EC.visibility_of_element_located(select_restaurant))
            # WebDriverWait(driver, 10).until(
            #     lambda d: d.execute_script('return document.readyState') == 'complete'
            # )
            time.sleep(2) #fix 뒤의 지도가 로딩되어야 클릭이벤트가 작동하는 것으로 파악됨. 지도렌더링 기다릴 방법 찾을 것
            actions = ActionChains(driver)
            actions.click(select_restaurant).perform()
            # select_restaurant.click();
    except:
        print("FAIL TO SEARCH LIST")
    ## 최종 정보 크롤링
    detail_info()

# test
crwl_data()
# 드라이버 종료
driver.quit()
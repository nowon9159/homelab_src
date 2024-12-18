from constants import WAIT_TIMEOUT_ONE, WAIT_TIMEOUT_TWO, WAIT_TIMEOUT_THREE, WAIT_TIMEOUT_FOUR, WAIT_TIMEOUT_TEN, WAIT_TIMEOUT_ELE

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC # expected_conditions (EC): Selenium에서 제공하는 여러 가지 조건을 정의한 모듈

import random
import time

# iframe 전환
def focus_iframe(driver, type):
    driver.switch_to.parent_frame()
    if type == 'list':
        iframe = driver.find_element(By.XPATH,'//*[@id="searchIframe"]')
    elif type == 'detail':
        custom_wait(driver, (By.XPATH, '//*[@id="entryIframe"]'),WAIT_TIMEOUT_TEN, WAIT_TIMEOUT_ELE)
        iframe = driver.find_element(By.XPATH,'//*[@id="entryIframe"]')

    driver.switch_to.frame(iframe)

# 랜덤 대기 시간 생성
def random_time(min, max):
    return random.uniform(min, max)

# 대기 시간 설정
def custom_wait(driver, path, min, max):
    return WebDriverWait(driver, random_time(min, max)).until(EC.presence_of_element_located(path));

# page scroll
def page_scroll(driver, class_name):
    scroll_container = driver.find_element(By.CSS_SELECTOR, f".{class_name}")
    last_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container) # execute_script = js 실행.

    while True:
        # 요소 내에서 아래로 3000px 스크롤
        driver.execute_script("arguments[0].scrollTop += 3000;", scroll_container)
        # 페이지 로드를 기다림
        time.sleep(random_time(WAIT_TIMEOUT_ONE, WAIT_TIMEOUT_TWO))
        # 스크롤 높이 계산
        new_height = driver.execute_script("return arguments[0].scrollHeight", scroll_container)

        # 스크롤이 더 이상 늘어나지 않으면 루프 종료
        if new_height == last_height:
            break
        last_height = new_height

# 인기 점수 계산
def calc_famous_cnt(star, review):
    famous_cnt = (float(star) * 0.01) + (float(review) * 0.0002)
    return famous_cnt

# 주소 기반 좌표값 추출
def get_lat_lon(driver, settings, input_address):
    driver.execute_script("window.open('');")
    time.sleep(1)
    driver.switch_to.window(driver.window_handles[-1])  #새로 연 탭으로 이동

    lat_lon_url = {settings.COORD_URL}
    driver.get(url=lat_lon_url)

    # get address input box
    custom_wait(driver, (By.XPATH, '//*[@id="gtco-header2"]/div/div[3]/div[2]/div[1]/input'), WAIT_TIMEOUT_TEN, WAIT_TIMEOUT_ELE)
    address_box = driver.find_element(By.XPATH, '//*[@id="gtco-header2"]/div/div[3]/div[2]/div[1]/input')
    address_box.send_keys(input_address)
    driver.find_element(By.XPATH, '//*[@id="btnGetGpsByAddress"]').click()

    lat = driver.find_element(By.XPATH, '/html/body/div[3]/header/div/div[3]/div[1]/div[1]/input')
    lon = driver.find_element(By.XPATH, '/html/body/div[3]/header/div/div[3]/div[1]/div[2]/input')

    # wait created modal
    custom_wait(driver, (By.XPATH, '//*[@id="askModal"]/div/div/div[2]'), WAIT_TIMEOUT_TEN, WAIT_TIMEOUT_ELE)
    time.sleep(random_time(WAIT_TIMEOUT_THREE, WAIT_TIMEOUT_FOUR))

    lat_value = lat.get_attribute("value")
    lon_value = lon.get_attribute("value")
    
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    return [lon_value, lat_value]
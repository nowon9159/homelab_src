# 데이터 파싱 로직

from bs4 import BeautifulSoup
from urllib.parse import urlparse, urlunparse # url query 정리
import re
from selenium.webdriver.common.by import By

from common.utils import *
from common.constants import WAIT_TIMEOUT_THREE, WAIT_TIMEOUT_FOUR, WAIT_TIMEOUT_TEN, WAIT_TIMEOUT_ELE

def simple_review():
    ## 인기순? 리뷰[0] 가져오는 로직 추가 필요
    return None

def main_image():
    ## 대표 이미지 가져오는 로직 추가 필요
    return None

def category_list():
    ## 카테고리 가져오는 로직 추가 필요
    return None

# review_cnt 연산
def review_count(store_id, ele):
    visitor_review_txt = ele.find('a', attrs={"href": f"/restaurant/{store_id}/review/visitor"}).get_text() if ele else None
    blog_review_txt = ele.find('a', attrs={"href": f"/restaurant/{store_id}/review/ugc"}).get_text() if ele else None
    visitor_review_cn = re.search(r'\b\d{1,3}(?:,\d{3})*\b', visitor_review_txt).group()
    blog_review_cn = re.search(r'\b\d{1,3}(?:,\d{3})*\b', blog_review_txt).group()
    return int(visitor_review_cn.replace(',', '')) + int(blog_review_cn.replace(',', ''))

# 현재 URL 가져오기 및 처리
def get_clean_url(driver):
    current_url = driver.current_url
    parsed_url = urlparse(current_url)
    cleaned_url = urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
    return cleaned_url

# 페이지 파싱
def parse_page(driver, settings, tab_list):
    result_page = driver.page_source
    soup = BeautifulSoup(result_page, 'html.parser')

    ## common
    cleaned_url = get_clean_url(driver)
    detail_ele = soup.find('div', class_='PIbes')
    subject_ele = soup.find('div', class_='zD5Nm undefined')
    url_path = urlparse(cleaned_url).path
    url_path_match = re.search(r'place/(\d+)', url_path)

    ## 가게 상세 정보 추출
    store_id = url_path_match.group(1) if url_path_match else None
    current_status = detail_ele.find('em').get_text() if detail_ele else None
    time_ele = soup.find('time', {'aria-hidden': 'true'}).get_text() if detail_ele else None
    strt_time, end_time = (time_ele, None) if current_status == '영업 종료' else (None, time_ele)
    store_nm = subject_ele.find('span', class_='GHAhO').get_text() if subject_ele else None
    address = detail_ele.find('span', class_='LDgIH').get_text() if detail_ele else None
    tel_no = detail_ele.find('span', class_='xlx7Q').get_text() if detail_ele else None
    star_rate = (subject_ele.find('span', class_='PXMot LXIwF').get_text() if subject_ele.find('span', class_='PXMot LXIwF') else "Node")
    star_rate = float(re.search(r"\d+\.\d+", star_rate).group())
    coord_list = get_lat_lon(driver, settings, input_address=address)
    review_cnt = review_count(store_id, subject_ele)
    
    focus_iframe(driver, "detail")
    custom_wait(driver, ((By.CLASS_NAME, 'CB8aP')), WAIT_TIMEOUT_THREE, WAIT_TIMEOUT_FOUR)
    for tab in tab_list:
        if tab.text == '리뷰':
            simple_review()
        if tab.text == '사진':
            main_image()
            category_list() # <--? inser_metadata.py 기반이라 여기 아닐수도?
            
    store_information = {
        'store_id': store_id,
        'store_nm': store_nm,
        'address': address,
        'tel_no': tel_no,
        'review_cnt': review_cnt,
        'star_rate': star_rate,
        'open_info': {
            'status': current_status,
            'start_time': strt_time,
            'end_time': end_time 
        },
        'location': {
            'type': 'Point',
            'coordinates': coord_list
        },
        # 'category': category_list,
        # 'image_url': main_img,
        'naver_url': cleaned_url,
        # 'simple_review': review_list[0],
        'famous_cnt': calc_famous_cnt(star=star_rate, review=review_cnt)
    }
    return store_information
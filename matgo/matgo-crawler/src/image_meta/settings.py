# 설정 파일
from fake_useragent import UserAgent
USER_AGENT = UserAgent(platforms="pc", browsers="chrome")


class Settings:
    def __init__(self):
        self.BASE_URL = f"https://map.naver.com/restaurant/list"
        self.COORD_URL = "https://gps.aply.biz/"
        self.USER_AGENT = USER_AGENT
        self.KEYWORD = "양천향교역 김치찌개" #test

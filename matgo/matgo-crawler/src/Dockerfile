# 베이스 이미지 선택
FROM python:3.9-slim

# 작업 디렉토리 생성
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 크롤링 프로그램 소스 코드 복사
COPY . .

RUN chmod +x src/chromedriver-linux64/chromedriver

# 실행 명령어 설정
CMD ["python", "insert_metadata.py"]

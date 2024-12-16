git -C /root/matgo/src/crawler/crawler pull origin main

docker build -t crawler:latest /root/matgo/src/crawler/crawler/.

docker compose up -d crawler
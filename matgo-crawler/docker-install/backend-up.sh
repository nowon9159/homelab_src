git -C /root/matgo/src/back pull origin main

docker build -t matgo-back:latest /root/matgo/src/back/matgo-back/.

docker compose up -d backend
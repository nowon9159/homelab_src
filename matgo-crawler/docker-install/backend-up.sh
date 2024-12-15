git -C /root/matgo/src/back origin pull origin master

docker build -t matgo-back:latest /root/matgo/src/back/matgo-back/sr``

docker compose up -d backend
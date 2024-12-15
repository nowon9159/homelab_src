git -C /root/matgo/src/front/matgo-front pull origin master

docker build -t matgo-front:latest /root/matgo/src/front/matgo-front/.

docker compose up -d frontend
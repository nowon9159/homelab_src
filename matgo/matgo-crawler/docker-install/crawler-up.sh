#git -C /root/matgo/git_src/crawler/crawler pull origin main

cp -r /home/clouflake/ai_model /root/matgo/src
docker build -t crawler:latest /root/matgo/src/.

docker compose up -d crawler
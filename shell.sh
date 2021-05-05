docker build -t door:v2 .
docker run -p 127.0.0.1:28800:80/tcp -p 20183:20183/tcp -v /etc/localtime:/etc/localtime:ro -v /data/door_server_alpine/code:/code --restart=always -d door:v2

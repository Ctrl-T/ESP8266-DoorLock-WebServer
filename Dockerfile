FROM python:3.8-alpine
WORKDIR /code
COPY requirements.txt /init/
RUN cd /init/ && sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/g' /etc/apk/repositories && apk add --no-cache nginx && pip3 install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com && rm -rf /etc/nginx/sites-enabled/default && mkdir /run/nginx/
COPY default.conf /etc/nginx/conf.d/default.conf
EXPOSE 20183 80
ENV FLASK_APP app.py
CMD nginx && flask run -h 0.0.0.0 -p 5000 

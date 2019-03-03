FROM python:alpine
COPY . /app
WORKDIR /app
RUN apk add python3-dev
RUN apk add libevent-dev
RUN apk add	mysql-client
RUN apk add mariadb-dev
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
EXPOSE 5000
CMD python ./app.py
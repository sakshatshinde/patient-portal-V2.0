FROM python:alpine3.7
COPY . /app
WORKDIR /app
RUN apk add mariadb mariadb-client 
#RUN apk add libmysqlclient-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 5000
CMD python ./app.py
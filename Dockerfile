FROM python:alpine
COPY . /app
WORKDIR /app
RUN apk update
RUN apk upgrade
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
EXPOSE 5000
CMD python ./app.py
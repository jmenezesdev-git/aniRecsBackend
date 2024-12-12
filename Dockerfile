FROM python:3.12
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000
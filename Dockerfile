FROM python:3

COPY server /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD gunicorn --bind 0.0.0.0:8000 wsgi
EXPOSE 8000
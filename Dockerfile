FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD uvicorn main:app --port=8000 --host=0.0.0.0


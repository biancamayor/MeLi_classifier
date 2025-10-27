# 1. Imagem Base
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scraper.py .

ENTRYPOINT ["python", "scraper.py"]

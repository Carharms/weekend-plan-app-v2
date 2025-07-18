# Dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    default-mysql-client \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN tar -czf weekend-app.tar.gz app.py templates static requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
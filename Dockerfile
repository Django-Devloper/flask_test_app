FROM python:3.11 AS builder

WORKDIR /install

COPY requirements.txt .

RUN pip install --no-cache-dir  --prefix=/install -r requirements.txt 
RUN pip install --no-cache-dir  --prefix=/install gunicorn
WORKDIR /app
FROM python:3.11-slim
COPY --from=builder /install /usr/local
COPY . .


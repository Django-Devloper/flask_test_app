FROM python:3.11 AS builder

WORKDIR /install

COPY requirements.txt .

RUN pip install --no-cache-dir  --prefix=/install -r requirements.txt 
RUN pip install --no-cache-dir  --prefix=/install gunicorn

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /install /usr/local

COPY . .

EXPOSE 5000

CMD ["gunicorn","-w","2","-b","0.0.0.0:5000","app:app"]


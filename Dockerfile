FROM python:3.7-alpine

WORKDIR /app

COPY requirements.txt .

RUN apk add --no-cache git \
    && pip install -r requirements.txt \
    && apk del git \
    && rm -rf /root/.cache

COPY ./pb/ pb/

CMD ["python", "-m", "pb"]

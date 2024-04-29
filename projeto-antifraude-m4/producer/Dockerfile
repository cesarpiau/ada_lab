FROM python:3.12-alpine3.19

WORKDIR /app

RUN apk add curl && pip install --upgrade pip && pip3 install pika minio
COPY ["transacoes.json", "producer.py", "./"]
ENTRYPOINT [ "python3", "producer.py" ]
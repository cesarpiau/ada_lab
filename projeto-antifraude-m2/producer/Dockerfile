FROM python:3.11.9-alpine3.19

WORKDIR /app

RUN apk add curl && pip install --upgrade pip && pip3 install pika
COPY ["transacoes.json", "producer.py", "./"]
ENTRYPOINT [ "python3", "producer.py" ]
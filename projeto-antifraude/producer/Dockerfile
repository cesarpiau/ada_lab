FROM ubuntu:22.04

WORKDIR /app

RUN apt-get update && apt-get install -y curl python3 python3-pip 
RUN pip3 install pika
COPY ["transacoes.json", "producer.py", "./"]
ENTRYPOINT [ "python3", "producer.py" ]
#COPY . .
#ENTRYPOINT [ "sleep", "infinity" ]

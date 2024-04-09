FROM ubuntu:22.04

WORKDIR /app

RUN apt-get update && apt-get install -y curl python3 python3-pip 
RUN pip3 install minio pika redis requests uuid
COPY ["consumer-antifraude.py", "./"]
ENTRYPOINT [ "python3", "consumer-antifraude.py" ]
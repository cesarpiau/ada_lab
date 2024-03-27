# syntax=docker/dockerfile:1

FROM debian:latest
WORKDIR /app
RUN apt-get update && apt-get install python3 -y
COPY main.py .

ENTRYPOINT [ "python3", "main.py" ]
#!/bin/bash

# RabbitMQ
docker container run --rm -d -p 15672:15672 -p 5672:5672 rabbitmq:3-management

# Redis
docker run --rm -d --name redis-stack -p 6379:6379 -p 8001:8001 redis/redis-stack:latest

# MinIO
docker run --rm -d -p 9000:9000 -p 9001:9001 --name minio1 -e "MINIO_ROOT_USER=guest" -e "MINIO_ROOT_PASSWORD=guestguest" -v ~/.minio/data:/data quay.io/minio/minio server /data --console-address ":9001"

# Python Packages
pip3 install minio pika redis requests uuid

# MinIO Client [Opcional]
# mkdir ~/.minio
# Invoke-WebRequest https://dl.min.io/client/mc/release/windows-amd64/mc.exe -OutFile '~/.minio/mc.exe'
# ~\.minio\mc.exe alias set local http://127.0.0.1:9000 guest guestguest


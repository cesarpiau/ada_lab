# Stage 1: Build
FROM python:3.11.9-alpine3.19

WORKDIR /app
RUN pip install --upgrade pip && pip install --no-cache-dir minio requests flask

COPY ["main.py", "./"]
EXPOSE 5000
ENV FLASK_APP=main.py
CMD ["flask", "run", "--host", "0.0.0.0"]
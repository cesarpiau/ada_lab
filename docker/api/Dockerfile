FROM alpine:latest

WORKDIR /app
# COPY ./requirements.txt /app
RUN apk add --no-cache curl python3 py3-pip py3-flask py3-redis
COPY . .
EXPOSE 5000
ENV FLASK_APP=main.py
CMD ["flask", "run", "--host", "0.0.0.0"]
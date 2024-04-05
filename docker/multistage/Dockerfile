# --- STAGE 1 ---
FROM python:3.9
WORKDIR /app
COPY . /app

# --- STAGE 1 ---
FROM python:3.9-alpine
WORKDIR /app
COPY --from=0 . /app
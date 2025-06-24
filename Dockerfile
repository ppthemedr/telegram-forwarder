FROM python:3.11-alpine

# Systeemafhankelijkheden
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    build-base \
    python3-dev

# Werkmap
WORKDIR /app

# Requirements installeren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code kopiëren
COPY . .

# Maak de sessions map aan voor persistent storage
RUN mkdir -p sessions
VOLUME ["/app/sessions"]

# Start de app
CMD ["python", "telegram_forwarder/forwarder.py"]

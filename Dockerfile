FROM python:3.11-alpine

# INSTALL SYSTEM DEPENDENCIES
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    build-base \
    python3-dev

# WERKMAP INSTELLEN
WORKDIR /app

# DEPENDENCIES INSTALLEREN
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# CODE KOPIËREN
COPY . .

# APP STARTEN
CMD ["python", "-m", "telegram_forwarder"]

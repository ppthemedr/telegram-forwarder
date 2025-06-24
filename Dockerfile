FROM python:3.11-alpine

# system deps voor cryptography / telethon
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev build-base python3-dev

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY forwarder.py .

CMD ["python", "forwarder.py"]

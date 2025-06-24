FROM python:3.11-alpine
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev build-base python3-dev

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# kopieer de volledige repo-inhoud
COPY . .

CMD ["python", "telegram_forwarder/forwarder.py"]


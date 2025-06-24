WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

RUN mkdir -p sessions
VOLUME ["/app/sessions"]

CMD ["python", "telegram_forwarder/forwarder.py"]

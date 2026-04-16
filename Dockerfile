FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /storage

ENV FLASK_APP=wsgi.py

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 80

CMD ["./entrypoint.sh"]

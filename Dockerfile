FROM python:3.11-slim

LABEL org.opencontainers.image.platform="linux/amd64"

WORKDIR /app

RUN pip install --no-cache-dir gunicorn[gevent]

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV ENV=production

EXPOSE 5000

CMD ["gunicorn", "-w", "2", "-k", "gevent", "-b", "0.0.0.0:5000", "main:app"]
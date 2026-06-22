FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m appuser && \
    mkdir -p /app/staticfiles /app/media && \
    chown -R appuser:appuser /app
USER appuser

RUN python manage.py collectstatic --noinput --skip-checks

EXPOSE 8000

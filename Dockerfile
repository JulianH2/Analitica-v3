FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    unixodbc-dev \
    g++ \
    curl \
    gnupg2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8050

CMD ["gunicorn", "--workers=4", "--threads=2", "--bind", "0.0.0.0:8050", "app:server"]
FROM python:3.10-slim

# نصب ابزارهای مورد نیاز سیستمی
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    python3-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# آپدیت pip و نصب پیش‌نیازها با اولویت نسخه‌های آماده
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]

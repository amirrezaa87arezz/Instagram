FROM python:3.10-slim

# نصب ابزارهای مورد نیاز سیستم برای کامپایل پکیج‌ها و پردازش ویدیو
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    python3-dev \
    && apt-get clean

WORKDIR /app

# آپدیت خودِ pip برای جلوگیری از ارورهای نصب
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]

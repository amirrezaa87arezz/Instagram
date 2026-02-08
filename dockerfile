FROM python:3.10-slim

# نصب ابزارهای مورد نیاز برای پردازش ویدیو
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

WORKDIR /app

COPY . .

# نصب کتابخانه‌های پایتون
RUN pip install --no-cache-dir -r requirements.txt

# اجرای ربات
CMD ["python", "main.py"]

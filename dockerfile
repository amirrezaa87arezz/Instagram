FROM python:3.10-slim

# نصب ffmpeg برای پردازش ویدیو
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir pyTelegramBotAPI yt-dlp

CMD ["python", "main.py"]

FROM python:3.10-slim

# نصب ffmpeg و کتابخانه‌های مورد نیاز
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libjpeg-dev \
    zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
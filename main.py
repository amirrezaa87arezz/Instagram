import telebot
import os
from yt_dlp import YoutubeDL
import threading

# توکن شما
TOKEN = "8576338411:AAGRw-zAM2U5CaBsn53fUTWGl1ju_UW3n4I"
bot = telebot.TeleBot(TOKEN)

# تنظیمات دانلود
YDL_OPTIONS = {
    'format': 'best[ext=mp4]/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'quiet': True,
    'no_warnings': True,
}

def download_and_send(message):
    url = message.text
    status_msg = bot.reply_to(message, "⏳ در حال دانلود از اینستاگرام...")
    
    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')
        
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            with open(file_path, 'rb') as video:
                bot.send_video(message.chat.id, video, caption="✅ بفرمایید!")
            
            os.remove(file_path) # حذف فایل بعد از ارسال
            bot.delete_message(message.chat.id, status_msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"❌ خطا در دانلود! مطمئن شوید پیج عمومی است.", message.chat.id, status_msg.message_id)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! لینک اینستاگرام بفرست تا برات دانلود کنم. 🔥")

@bot.message_handler(func=lambda m: "instagram.com" in m.text)
def handle_insta(message):
    # اجرای دانلود در یک ترد جداگانه برای جلوگیری از هنگ کردن ربات
    threading.Thread(target=download_and_send, args=(message,)).start()

print("Bot is running...")
bot.infinity_polling()

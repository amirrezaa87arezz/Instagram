import telebot
from telebot import types
import os
import time
import json
import threading
from yt_dlp import YoutubeDL
from instagrapi import Client

# --- تنظیمات توکن تلگرام ---
TOKEN = "8576338411:AAGRw-zAM2U5CaBsn53fUTWGl1ju_UW3n4I"
bot = telebot.TeleBot(TOKEN)
cl = Client()

# --- تنظیم پروکسی ارسالی شما ---
# فرمت: http://IP:PORT
PROXY_URL = "http://209.135.168.41:80"

def insta_login():
    try:
        print(f"Dragon is connecting via Proxy: {PROXY_URL} 🐲")
        # تنظیم پروکسی در کتابخانه
        cl.set_proxy(PROXY_URL)
        
        # سشن‌آیدی اختصاصی شما
        sid = "72867675539%3AACcKqkPmesZgdm%3A27%3AAYh8Md6lF1xwQD0eTS-5plrnrAOgIcDSDjRR3RwqzQ"
        
        # ورود مستقیم با سشن
        cl.login_by_sessionid(sid)
        
        print("Success! Dragon is online and bypassed the block. ✅")
    except Exception as e:
        print(f"❌ Login Failed with Proxy: {e}")
        print("Tip: If it failed, the proxy might be offline. Try another one.")

def download_and_send(url, chat_id, caption):
    # تنظیمات دانلود ویدیو
    opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': f'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True
    }
    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
            with open(path, 'rb') as v:
                bot.send_video(chat_id, v, caption=caption)
            os.remove(path)
    except Exception as e:
        bot.send_message(chat_id, f"❌ Download Error: {e}")

def watch_directs():
    while True:
        try:
            # بررسی دایرکت‌ها هر ۶۰ ثانیه برای جلوگیری از بلاک مجدد
            threads = cl.direct_threads(amount=5)
            for thread in threads:
                # بررسی آخرین پیام در هر ترد
                messages = cl.direct_messages(thread.id, amount=1)
                if messages:
                    msg = messages[0]
                    # اگر پیام حاوی لینک اینستاگرام بود و ما نفرستاده بودیم
                    if msg.text and "instagram.com" in msg.text and msg.user_id != cl.user_id:
                        # اگر لایک نشده بود یعنی جدید است
                        if not msg.reactions:
                            print(f"New link from direct! 📥")
                            # ارسال به تلگرام (در اینجا به صورت پیش‌فرض به چت‌باکس ربات می‌رود)
                            # برای شخصی‌سازی، باید یوزرنیم را در دیتابیس چک کنید
                            threading.Thread(target=download_and_send, args=(msg.text, 584311059, f"📥 دریافت شد از اینستاگرام")).start()
                            # لایک کردن برای علامت‌گذاری
                            cl.direct_message_react(thread.id, msg.id, '❤️')
            time.sleep(60)
        except Exception as e:
            print(f"Watch Error: {e}")
            time.sleep(120)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🐲 دراگون با پروکسی اختصاصی فعال شد!\nلینک ریلز بفرست تا دانلود کنم.")

@bot.message_handler(func=lambda m: "instagram.com" in m.text)
def handle_tg_link(message):
    threading.Thread(target=download_and_send, args=(message.text, message.chat.id, "بفرمایید! 🐲")).start()

if __name__ == "__main__":
    insta_login()
    threading.Thread(target=watch_directs, daemon=True).start()
    # استفاده از skip_pending برای جلوگیری از ارور Conflict
    bot.infinity_polling(skip_pending=True)
    

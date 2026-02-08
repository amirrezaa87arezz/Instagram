import telebot
import os
import time
import json
import threading
from yt_dlp import YoutubeDL
from instagrapi import Client

# --- تنظیمات اصلی ---
TOKEN = "8576338411:AAGRw-zAM2U5CaBsn53fUTWGl1ju_UW3n4I"
INSTA_USER = "dragonn.dl"
INSTA_PASS = "#dragon#$123321"

bot = telebot.TeleBot(TOKEN)
cl = Client()
DB_FILE = "users.json"

# بارگذاری دیتابیس کاربران
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        try:
            user_map = json.load(f)
        except:
            user_map = {}
else:
    user_map = {}

def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(user_map, f)

# لاگین به اینستاگرام
def insta_login():
    try:
        session_path = "session.json"
        if os.path.exists(session_path):
            cl.load_settings(session_path)
        cl.login(INSTA_USER, INSTA_PASS)
        cl.dump_settings(session_path)
        print("Dragon connected to Instagram! ✅")
    except Exception as e:
        print(f"Insta Error: {e}")

# تابع دانلود و ارسال
def download_and_send(url, chat_id, caption="بفرمایید! 🐲"):
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': f'downloads/{int(time.time())}_%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            with open(file_path, 'rb') as video:
                bot.send_video(chat_id, video, caption=caption)
            os.remove(file_path)
    except Exception as e:
        bot.send_message(chat_id, "❌ خطا در دانلود! مطمئن شوید پیج عمومی است.")

# چک کردن دایرکت‌ها
def watch_directs():
    while True:
        try:
            threads = cl.get_threads()
            for thread in threads:
                sender = thread.users[0].username.lower()
                if sender in user_map:
                    msgs = cl.get_messages(thread.id, amount=1)
                    if msgs:
                        m = msgs[0]
                        if m.text and "instagram.com" in m.text and not m.is_sent_by_viewer:
                            target_id = user_map[sender]
                            threading.Thread(target=download_and_send, args=(m.text, target_id, f"🚀 از دایرکت @{sender}")).start()
                            cl.message_like(m.id)
            time.sleep(45)
        except:
            time.sleep(60)

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "🐲 دراگون دانلودر فعال است!\nلینک بفرست یا با `/connect username` وصل شو.")

@bot.message_handler(commands=['connect'])
def connect(message):
    parts = message.text.split()
    if len(parts) == 2:
        uname = parts[1].replace('@', '').lower()
        user_map[uname] = message.chat.id
        save_db()
        bot.reply_to(message, f"✅ اکانت @{uname} متصل شد!")
    else:
        bot.reply_to(message, "مثال: `/connect dragon_user`")

@bot.message_handler(func=lambda m: "instagram.com" in m.text)
def direct_link(message):
    threading.Thread(target=download_and_send, args=(message.text, message.chat.id)).start()

if __name__ == "__main__":
    insta_login()
    threading.Thread(target=watch_directs, daemon=True).start()
    bot.infinity_polling()

import telebot
from telebot import types
import os
import time
import json
import threading
from yt_dlp import YoutubeDL
from instagrapi import Client

# --- تنظیمات ---
TOKEN = "8576338411:AAGRw-zAM2U5CaBsn53fUTWGl1ju_UW3n4I"
bot = telebot.TeleBot(TOKEN)
cl = Client()
DB_FILE = "users_data.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try: return json.load(f)
            except: return {"users": {}, "stats": {}}
    return {"users": {}, "stats": {}}

db = load_db()

def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

# متد لاگین کاملاً تغییر یافته برای حذف ارور set_cookies
def insta_login():
    try:
        print("Dragon is trying a new technique... 🐲")
        
        # سشن‌آیدی شما
        sid = "72867675539%3AACcKqkPmesZgdm%3A27%3AAYh8Md6lF1xwQD0eTS-5plrnrAOgIcDSDjRR3RwqzQ"
        
        # لاگین مستقیم با کوکی سشن
        cl.login_by_sessionid(sid)
        
        print("Success! Dragon is online. ✅")
    except Exception as e:
        print(f"❌ Login Failed: {e}")

def download_and_send(url, chat_id, caption):
    opts = {'format': 'best[ext=mp4]/best', 'outtmpl': f'downloads/%(id)s.%(ext)s', 'quiet': True}
    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
            with open(path, 'rb') as v:
                bot.send_video(chat_id, v, caption=caption)
            os.remove(path)
            uid = str(chat_id)
            db["stats"][uid] = db["stats"].get(uid, 0) + 1
            save_db()
    except Exception as e:
        bot.send_message(chat_id, f"❌ Download Error: {e}")

def watch_directs():
    while True:
        try:
            # استفاده از متد صحیح برای گرفتن دایرکت‌ها
            threads = cl.direct_threads()
            for thread in threads:
                sender_uname = thread.users[0].username.lower()
                if sender_uname in db["users"]:
                    # چک کردن آخرین پیام
                    msg = thread.messages[0]
                    # اگر لینک اینستاگرام بود و ما نفرستاده بودیم
                    if msg.text and "instagram.com" in msg.text and msg.user_id != cl.user_id:
                        # چک کردن اینکه لایک نشده باشد (نشان‌دهنده پیام جدید)
                        if not msg.reactions:
                            target_id = db["users"][sender_uname]
                            threading.Thread(target=download_and_send, args=(msg.text, target_id, f"📥 دریافت شد از @{sender_uname}")).start()
                            # لایک کردن برای علامت‌گذاری به عنوان "خوانده شده"
                            cl.direct_message_react(thread.id, msg.id, '❤️')
            time.sleep(40)
        except Exception as e:
            print(f"Watch Error: {e}")
            time.sleep(60)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🔗 متصل کردن اکانت"), types.KeyboardButton("📊 آمار"))
    bot.send_message(message.chat.id, "🐲 دراگون فعال شد!", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🔗 متصل کردن اکانت")
def ask_conn(message):
    msg = bot.send_message(message.chat.id, "یوزرنیم اینستاگرامت رو بفرست:")
    bot.register_next_step_handler(msg, do_connect)

def do_connect(message):
    uname = message.text.lower().strip()
    db["users"][uname] = message.chat.id
    save_db()
    bot.send_message(message.chat.id, f"✅ @{uname} متصل شد.")

@bot.message_handler(func=lambda m: "instagram.com" in m.text)
def handle_link(message):
    threading.Thread(target=download_and_send, args=(message.text, message.chat.id, "بفرمایید! 🐲")).start()

if __name__ == "__main__":
    insta_login()
    threading.Thread(target=watch_directs, daemon=True).start()
    bot.infinity_polling(skip_pending=True)

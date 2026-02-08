import telebot
from telebot import types
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

# متد لاگین اصلاح شده برای حل ارور set_cookies
def insta_login():
    try:
        print("Dragon is waking up... 🐲")
        
        # سشن‌آیدی اختصاصی شما
        my_session_id = "72867675539%3AACcKqkPmesZgdm%3A27%3AAYh8Md6lF1xwQD0eTS-5plrnrAOgIcDSDjRR3RwqzQ"
        
        # تنظیمات مستقیم سشن
        settings = {
            "authorization_data": {
                "sessionid": my_session_id
            }
        }
        cl.set_settings(settings)
        
        # تست ورود
        cl.get_timeline_feed() 
        print("Connected to Instagram successfully! ✅")
        
    except Exception as e:
        print(f"⚠️ Login Error: {e}")
        try:
            cl.login(INSTA_USER, INSTA_PASS)
            print("Login with pass successful! ✅")
        except Exception as e2:
            print(f"❌ Critical Failure: {e2}")

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
        bot.send_message(chat_id, f"❌ خطا: {e}")

def watch_directs():
    while True:
        try:
            # متد اصلاح شده برای گرفتن دایرکت‌ها
            threads = cl.direct_threads()
            for thread in threads:
                sender_uname = thread.users[0].username.lower()
                if sender_uname in db["users"]:
                    # گرفتن آخرین پیام دایرکت
                    msg = cl.direct_messages(thread.id, amount=1)[0]
                    if msg.text and "instagram.com" in msg.text and not msg.is_sent_by_viewer:
                        # چک کردن لایک برای جلوگیری از تکرار
                        target_id = db["users"][sender_uname]
                        threading.Thread(target=download_and_send, args=(msg.text, target_id, f"📥 از دایرکت @{sender_uname}")).start()
                        # لایک کردن پیام برای اینکه دوباره دانلود نشود
                        cl.direct_message_react(thread.id, msg.id, '❤️')
            time.sleep(40)
        except:
            time.sleep(60)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🔗 متصل کردن اکانت اینستاگرام"), types.KeyboardButton("📊 آمار من"))
    bot.send_message(message.chat.id, "🐲 دراگون آماده است!", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🔗 متصل کردن اکانت اینستاگرام")
def ask_conn(message):
    msg = bot.send_message(message.chat.id, "یوزرنیم اینستاگرامت رو (بدون @) بفرست:")
    bot.register_next_step_handler(msg, do_connect)

def do_connect(message):
    uname = message.text.lower().strip()
    db["users"][uname] = message.chat.id
    save_db()
    bot.send_message(message.chat.id, f"✅ اکانت @{uname} متصل شد.")

@bot.message_handler(func=lambda m: "instagram.com" in m.text)
def handle_link(message):
    threading.Thread(target=download_and_send, args=(message.text, message.chat.id, "بفرمایید! 🐲")).start()

if __name__ == "__main__":
    insta_login()
    threading.Thread(target=watch_directs, daemon=True).start()
    bot.infinity_polling(skip_pending=True) # اضافه کردن skip_pending برای حل ارور Conflict

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

# بارگذاری دیتابیس (یوزرنیم‌ها و آمار)
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

# لاگین به اینستاگرام
def insta_login():
    try:
        print("Dragon is waking up... 🐲")
        cl.login(INSTA_USER, INSTA_PASS)
        print("Connected to Instagram! ✅")
    except Exception as e:
        print(f"Insta Login Error: {e}")

# منوی اصلی
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🔗 متصل کردن اکانت اینستاگرام"))
    markup.add(types.KeyboardButton("📊 آمار من"), types.KeyboardButton("❓ راهنما"))
    return markup

# دانلود و ارسال
def download_and_send(url, chat_id, caption):
    opts = {'format': 'best[ext=mp4]/best', 'outtmpl': f'downloads/{int(time.time())}_%(id)s.%(ext)s', 'quiet': True}
    try:
        if not os.path.exists('downloads'): os.makedirs('downloads')
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
            with open(path, 'rb') as v:
                bot.send_video(chat_id, v, caption=caption)
            os.remove(path)
            
            # بروزرسانی آمار
            uid = str(chat_id)
            db["stats"][uid] = db["stats"].get(uid, 0) + 1
            save_db()
    except:
        bot.send_message(chat_id, "❌ خطا در دانلود! (احتمالا پیج خصوصی است یا لینک منقضی شده)")

# مانیتورینگ دایرکت (نسخه اصلاح شده)
def watch_directs():
    while True:
        try:
            threads = cl.get_threads()
            for thread in threads:
                sender_uname = thread.users[0].username.lower()
                if sender_uname in db["users"]:
                    messages = cl.get_messages(thread.id, amount=2)
                    for m in messages:
                        # اگر پیام حاوی لینک است، توسط ما فرستاده نشده و لایک نشده (جدید است)
                        if m.text and "instagram.com" in m.text and not m.is_sent_by_viewer:
                            if not m.reactions:
                                target_id = db["users"][sender_uname]
                                threading.Thread(target=download_and_send, args=(m.text, target_id, f"📥 دریافت شد از دایرکت @{sender_uname}")).start()
                                cl.message_like(m.id)
            time.sleep(30)
        except:
            time.sleep(60)

# هندلرهای تلگرام
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🐲 به پنل مدیریت **دراگون دانلودر** خوش آمدی!\n\nلینک پست رو بفرست یا از منو استفاده کن:", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "📊 آمار من")
def show_stats(message):
    count = db["stats"].get(str(message.chat.id), 0)
    bot.reply_to(message, f"📊 **آمار فعالیت شما:**\n\n✅ تعداد دانلود موفق: {count} ویدیو\n🐲 سطح شما: {'اژدهای تازه‌کار' if count < 10 else 'اژدهای آتشین'}")

@bot.message_handler(func=lambda m: m.text == "🔗 متصل کردن اکانت اینستاگرام")
def ask_conn(message):
    msg = bot.send_message(message.chat.id, "لطفاً یوزرنیم اینستاگرام خود را (بدون @) بفرستید:")
    bot.register_next_step_handler(msg, do_connect)

def do_connect(message):
    uname = message.text.lower().strip()
    db["users"][uname] = message.chat.id
    save_db()
    bot.send_message(message.chat.id, f"✅ اکانت @{uname} متصل شد!\nحالا در دایرکت به پیج ما پست بفرست.")

@bot.message_handler(func=lambda m: m.text == "❓ راهنما")
def help_msg(message):
    bot.send_message(message.chat.id, "1️⃣ لینک ریلز یا پست رو اینجا کپی کن.\n2️⃣ یا اکانتت رو متصل کن و توی اینستاگرام برای پیج ما دایرکت کن.\n3️⃣ ربات خودکار ویدیو رو برات اینجا می‌فرسته!")

@bot.message_handler(func=lambda m: "instagram.com" in m.text)
def handle_link(message):
    threading.Thread(target=download_and_send, args=(message.text, message.chat.id, "بفرمایید! 🐲")).start()

if __name__ == "__main__":
    insta_login()
    threading.Thread(target=watch_directs, daemon=True).start()
    bot.infinity_polling()

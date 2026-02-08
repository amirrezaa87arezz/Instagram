import telebot
from telebot import types
import os, time, json, threading
from yt_dlp import YoutubeDL
from instagrapi import Client

# --- تنظیمات اصلی ---
TOKEN = "8576338411:AAGRw-zAM2U5CaBsn53fUTWGl1ju_UW3n4I"
bot = telebot.TeleBot(TOKEN)
cl = Client()
DB_FILE = "users_data.json"

# --- مدیریت دیتابیس آمار ---
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

# --- تابع دانلود هوشمند ---
def download_and_send(url, chat_id):
    opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }
    try:
        proc_msg = bot.send_message(chat_id, "⏳ در حال پردازش لینک...")
        
        if not os.path.exists('downloads'): os.makedirs('downloads')
        with YoutubeDL(opts) as ydl:
            ydl.cache.remove()
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
            with open(path, 'rb') as v:
                bot.send_video(chat_id, v, caption="بفرمایید! 🐲\n@dragonn_dl")
            os.remove(path)
            bot.delete_message(chat_id, proc_msg.message_id)
            
            # ثبت آمار دانلود
            uid = str(chat_id)
            db["stats"][uid] = db["stats"].get(uid, 0) + 1
            save_db()
            
    except Exception as e:
        bot.send_message(chat_id, f"❌ خطا در دانلود: {str(e)[:50]}...")

# --- مدیریت اینستاگرام ---
def insta_login():
    try:
        sid = "72867675539%3AACcKqkPmesZgdm%3A27%3AAYh8Md6lF1xwQD0eTS-5plrnrAOgIcDSDjRR3RwqzQ"
        cl.login_by_sessionid(sid)
        print("Instagram Login Success! ✅")
        return True
    except:
        print("Instagram Login Failed! ⚠️")
        return False

# --- دکمه‌ها و دستورات تلگرام ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("🔗 اتصال اکانت اینستاگرام"))
    markup.add(types.KeyboardButton("📊 آمار من"))
    bot.send_message(message.chat.id, "🐲 به دراگون خوش آمدی!\nلینک ریلز بفرست یا از منو استفاده کن:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📊 آمار من")
def show_stats(message):
    count = db["stats"].get(str(message.chat.id), 0)
    bot.reply_to(message, f"📊 تعداد ویدیوهای دانلود شده توسط شما: {count}")

@bot.message_handler(func=lambda m: m.text == "🔗 اتصال اکانت اینستاگرام")
def ask_conn(message):
    msg = bot.send_message(message.chat.id, "لطفاً یوزرنیم اینستاگرام خود را (بدون @) بفرستید:")
    bot.register_next_step_handler(msg, do_connect)

def do_connect(message):
    uname = message.text.lower().strip()
    db["users"][uname] = message.chat.id
    save_db()
    bot.send_message(message.chat.id, f"✅ اکانت @{uname} با موفقیت ثبت شد.")

@bot.message_handler(func=lambda m: "instagram.com" in m.text)
def handle_link(message):
    threading.Thread(target=download_and_send, args=(message.text, message.chat.id)).start()

if __name__ == "__main__":
    insta_login()
    bot.infinity_polling(skip_pending=True)
    

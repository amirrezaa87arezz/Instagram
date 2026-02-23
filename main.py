import telebot
from telebot import types
import os, json, threading, time, random, pickle
from yt_dlp import YoutubeDL
from instagrapi import Client
import logging
from datetime import datetime

# --- تنظیمات اصلی ---
TOKEN = "8576338411:AAGRw-zAM2U5CaBsn53fUTWGl1ju_UW3n4I"
bot = telebot.TeleBot(TOKEN)
DB_FILE = "users_data.json"
SESSION_FILE = "instagram_session.pkl"

# --- تنظیمات حرفه‌ای ---
class InstagramManager:
    def __init__(self):
        self.cl = Client()
        self.session_id = "72867675539%3AACcKqkPmesZgdm%3A27%3AAYh8Md6lF1xwQD0eTS-5plrnrAOgIcDSDjRR3RwqzQ"
        self.user_agents = [
            "Instagram 269.0.0.18.85 Android",
            "Instagram 270.0.0.20.85 Android",
            "Instagram 271.0.0.30.85 iPhone",
        ]
        self.last_request = 0
        self.setup_client()
    
    def setup_client(self):
        """تنظیمات اولیه"""
        self.cl.set_user_agent(random.choice(self.user_agents))
        self.cl.delay_range = [3, 8]
    
    def login(self):
        """لاگین با Session ID"""
        try:
            # تلاش برای بارگذاری Session قبلی
            if os.path.exists(SESSION_FILE):
                try:
                    with open(SESSION_FILE, 'rb') as f:
                        settings = pickle.load(f)
                        self.cl.set_settings(settings)
                    print("✅ Session قبلی loaded")
                    return True
                except:
                    pass
            
            # لاگین جدید
            self.cl.login_by_sessionid(self.session_id)
            
            # ذخیره Session
            with open(SESSION_FILE, 'wb') as f:
                pickle.dump(self.cl.get_settings(), f)
            
            print("✅ لاگین جدید موفق بود")
            return True
            
        except Exception as e:
            print(f"❌ خطا در لاگین: {e}")
            return False

# --- دیتابیس ---
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            try: return json.load(f)
            except: return {"users": {}, "stats": {}}
    return {"users": {}, "stats": {}}

db = load_db()
instagram = InstagramManager()

def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

# --- تابع دانلود ---
def download_and_send(url, chat_id):
    opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'user_agent': random.choice(instagram.user_agents),
    }
    
    try:
        proc_msg = bot.send_message(chat_id, "⏳ در حال دانلود...")
        
        if not os.path.exists('downloads'): 
            os.makedirs('downloads')
        
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if os.path.exists(filename):
                with open(filename, 'rb') as f:
                    bot.send_video(chat_id, f, caption="🐲 @dragonn_dl")
                os.remove(filename)
                bot.delete_message(chat_id, proc_msg.message_id)
                
                # ثبت آمار
                db["stats"][str(chat_id)] = db["stats"].get(str(chat_id), 0) + 1
                save_db()
            else:
                # اگه فایل با اسم دیگه ذخیره شده
                for file in os.listdir('downloads'):
                    if file.endswith(('.mp4', '.mkv', '.webm')):
                        with open(f'downloads/{file}', 'rb') as f:
                            bot.send_video(chat_id, f, caption="🐲 @dragonn_dl")
                        os.remove(f'downloads/{file}')
                        break
                
    except Exception as e:
        bot.send_message(chat_id, f"❌ خطا: {str(e)[:100]}")

# --- هندلرهای تلگرام ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📥 دانلود"),
        types.KeyboardButton("📊 آمار"),
        types.KeyboardButton("🔄 وضعیت")
    )
    
    bot.send_message(
        message.chat.id,
        "🐲 **ربات دانلود اینستاگرام**\n\n"
        "لینک پست یا ریلز بفرستید تا دانلود کنم ⬇️",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "📊 آمار")
def stats(message):
    count = db["stats"].get(str(message.chat.id), 0)
    bot.reply_to(message, f"📊 تعداد دانلود: {count}")

@bot.message_handler(func=lambda m: m.text == "🔄 وضعیت")
def status(message):
    if instagram.cl.user_id:
        bot.reply_to(message, "✅ اتصال به اینستاگرام: فعال")
    else:
        bot.reply_to(message, "⚠️ اتصال به اینستاگرام: غیرفعال")

@bot.message_handler(func=lambda m: m.text == "📥 دانلود")
def ask_link(message):
    msg = bot.send_message(message.chat.id, "🔗 لینک را بفرستید:")
    bot.register_next_step_handler(msg, handle_link)

@bot.message_handler(func=lambda m: "instagram.com" in m.text or "instagr.am" in m.text)
def handle_link(message):
    bot.reply_to(message, "⏳ دانلود شروع شد...")
    threading.Thread(target=download_and_send, args=(message.text, message.chat.id)).start()

# --- اجرا ---
if __name__ == "__main__":
    print("🚀 ربات در حال راه‌اندازی...")
    
    # لاگین به اینستاگرام
    if instagram.login():
        print("✅ اتصال به اینستاگرام برقرار شد")
    else:
        print("⚠️ اتصال به اینستاگرام برقرار نشد")
    
    print("🤖 ربات تلگرام فعال شد")
    bot.infinity_polling(skip_pending=True)
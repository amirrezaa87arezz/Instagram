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

# --- تنظیمات حرفه‌ای برای جلوگیری از بن ---
class InstagramManager:
    def __init__(self):
        self.cl = Client()
        self.session_id = "72867675539%3AACcKqkPmesZgdm%3A27%3AAYh8Md6lF1xwQD0eTS-5plrnrAOgIcDSDjRR3RwqzQ"
        self.last_request = 0
        self.request_count = 0
        self.is_connected = False
        
    def login(self):
        """لاگین با Session ID"""
        try:
            # تنظیمات پیشرفته
            self.cl.set_locale("en_US")
            self.cl.set_country_code("US")
            self.cl.delay_range = [5, 10]
            
            # تلاش برای لاگین
            self.cl.login_by_sessionid(self.session_id)
            
            # ذخیره session برای استفاده بعدی
            with open(SESSION_FILE, 'wb') as f:
                pickle.dump(self.cl.get_settings(), f)
            
            self.is_connected = True
            print("✅ اتصال به اینستاگرام موفق بود")
            return True
            
        except Exception as e:
            print(f"❌ خطا در اتصال به اینستاگرام: {e}")
            self.is_connected = False
            return False
    
    def get_cookies(self):
        """تبدیل session به کوکی برای yt-dlp"""
        try:
            if self.is_connected:
                # ساخت فایل کوکی موقت
                cookies = {
                    'sessionid': self.session_id,
                    'ds_user_id': str(self.cl.user_id) if self.cl.user_id else '',
                }
                return cookies
        except:
            pass
        return None

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

# --- تابع دانلود با چند روش مختلف ---
def download_and_send(url, chat_id):
    # روش اول: با instagrapi
    if instagram.is_connected:
        try:
            proc_msg = bot.send_message(chat_id, "⏳ در حال دانلود با روش مستقیم...")
            
            # استخراج media_id
            media_pk = instagram.cl.media_pk_from_url(url)
            media_path = instagram.cl.video_download(media_pk, folder="downloads")
            
            if media_path and os.path.exists(media_path):
                with open(media_path, 'rb') as f:
                    bot.send_video(chat_id, f, caption="🐲 @dragonn_dl (مستقیم)")
                os.remove(media_path)
                bot.delete_message(chat_id, proc_msg.message_id)
                
                # ثبت آمار
                db["stats"][str(chat_id)] = db["stats"].get(str(chat_id), 0) + 1
                save_db()
                return
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ روش مستقیم failed، تلاش با روش دوم...")
    
    # روش دوم: با yt-dlp و کوکی
    try:
        proc_msg = bot.send_message(chat_id, "⏳ در حال دانلود با روش دوم...")
        
        opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
            'extract_flat': False,
            'force_generic_extractor': False,
        }
        
        if not os.path.exists('downloads'): 
            os.makedirs('downloads')
        
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # پیدا کردن فایل دانلود شده
            file_found = False
            if os.path.exists(filename):
                with open(filename, 'rb') as f:
                    bot.send_video(chat_id, f, caption="🐲 @dragonn_dl")
                os.remove(filename)
                file_found = True
            else:
                for file in os.listdir('downloads'):
                    if file.endswith(('.mp4', '.mkv', '.webm')):
                        with open(f'downloads/{file}', 'rb') as f:
                            bot.send_video(chat_id, f, caption="🐲 @dragonn_dl")
                        os.remove(f'downloads/{file}')
                        file_found = True
                        break
            
            if file_found:
                bot.delete_message(chat_id, proc_msg.message_id)
                db["stats"][str(chat_id)] = db["stats"].get(str(chat_id), 0) + 1
                save_db()
            else:
                bot.send_message(chat_id, "❌ فایل دانلود نشد")
                
    except Exception as e:
        bot.send_message(chat_id, f"❌ خطا: {str(e)[:100]}")

# --- ایجاد فایل کوکی ---
def create_cookie_file():
    try:
        cookie_content = f"""# Netscape HTTP Cookie File
.instagram.com	TRUE	/	FALSE	1735689600	sessionid	{instagram.session_id}
"""
        with open('cookies.txt', 'w') as f:
            f.write(cookie_content)
        print("✅ فایل کوکی ساخته شد")
    except:
        pass

# --- هندلرهای تلگرام ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📥 دانلود"),
        types.KeyboardButton("📊 آمار"),
        types.KeyboardButton("🔄 وضعیت اتصال"),
        types.KeyboardButton("🔑 لاگین مجدد")
    )
    
    status = "✅ متصل" if instagram.is_connected else "❌ قطع"
    
    bot.send_message(
        message.chat.id,
        f"🐲 **ربات دانلود اینستاگرام**\n\n"
        f"📱 **وضعیت اتصال:** {status}\n"
        f"🔗 **لینک اینستاگرام بفرست تا دانلود کنم**\n\n"
        f"⚡ پشتیبانی از: ریلز، پست، استوری",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "📊 آمار")
def stats(message):
    count = db["stats"].get(str(message.chat.id), 0)
    bot.reply_to(message, f"📊 تعداد دانلودهای شما: {count}")

@bot.message_handler(func=lambda m: m.text == "🔄 وضعیت اتصال")
def status(message):
    if instagram.is_connected:
        bot.reply_to(message, "✅ اتصال به اینستاگرام: فعال")
    else:
        bot.reply_to(message, "❌ اتصال به اینستاگرام: قطع")
        # تلاش مجدد
        if instagram.login():
            bot.reply_to(message, "✅ اتصال مجدد موفق بود")

@bot.message_handler(func=lambda m: m.text == "🔑 لاگین مجدد")
def relogin(message):
    msg = bot.send_message(message.chat.id, "⏳ در حال اتصال مجدد...")
    if instagram.login():
        bot.edit_message_text("✅ اتصال موفق بود", message.chat.id, msg.message_id)
    else:
        bot.edit_message_text("❌ اتصال ناموفق", message.chat.id, msg.message_id)

@bot.message_handler(func=lambda m: m.text == "📥 دانلود")
def ask_link(message):
    msg = bot.send_message(message.chat.id, "🔗 لینک اینستاگرام را بفرستید:")
    bot.register_next_step_handler(msg, handle_link)

@bot.message_handler(func=lambda m: "instagram.com" in m.text or "instagr.am" in m.text)
def handle_link(message):
    bot.reply_to(message, "⏳ لینک دریافت شد، دانلود شروع شد...")
    threading.Thread(target=download_and_send, args=(message.text, message.chat.id)).start()

# --- تمدید خودکار اتصال ---
def auto_reconnect():
    while True:
        time.sleep(3600)  # هر ساعت یکبار
        if not instagram.is_connected:
            instagram.login()
        else:
            # تست اتصال
            try:
                instagram.cl.user_id
            except:
                instagram.is_connected = False
                instagram.login()

# --- اجرا ---
if __name__ == "__main__":
    print("🚀 ربات در حال راه‌اندازی...")
    
    # لاگین به اینستاگرام
    if instagram.login():
        create_cookie_file()
    
    # شروع تمدید خودکار
    reconnect_thread = threading.Thread(target=auto_reconnect, daemon=True)
    reconnect_thread.start()
    
    print("🤖 ربات تلگرام فعال شد")
    bot.infinity_polling(skip_pending=True)
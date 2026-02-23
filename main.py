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
        self.user_agents = [
            "Instagram 269.0.0.18.85 Android (30/11; 420dpi; 1080x1920; samsung)",
            "Instagram 270.0.0.20.85 Android (31/12; 440dpi; 1080x2340; Xiaomi)",
            "Instagram 271.0.0.30.85 iPhone (iOS 16_5; iPhone14,3)",
            "Instagram 272.0.0.35.85 Android (33/13; 480dpi; 1440x3200; google/pixel)",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"
        ]
        self.last_request = 0
        self.request_count = 0
        self.setup_client()
    
    def setup_client(self):
        """تنظیمات اولیه کلاینت"""
        # تنظیم User-Agent تصادفی
        self.cl.set_user_agent(random.choice(self.user_agents))
        
        # تنظیم Delay متغیر
        self.cl.delay_range = [3, 8]
        
        # تنظیم زبان و لوکیشن
        self.cl.set_locale("en_US")
        self.cl.set_country_code("US")
    
    def human_delay(self):
        """ایجاد تاخیر شبیه انسان"""
        now = time.time()
        if self.last_request > 0:
            elapsed = now - self.last_request
            min_delay = 5
            
            if elapsed < min_delay:
                sleep_time = min_delay - elapsed + random.uniform(1, 3)
                time.sleep(sleep_time)
        
        self.last_request = time.time()
        self.request_count += 1
        
        # هر 10 درخواست، توقف طولانی‌تر
        if self.request_count % 10 == 0:
            time.sleep(random.uniform(15, 25))
    
    def login(self):
        """لاگین با Session ID"""
        try:
            # بارگذاری Session ذخیره شده
            if os.path.exists(SESSION_FILE):
                with open(SESSION_FILE, 'rb') as f:
                    settings = pickle.load(f)
                    self.cl.set_settings(settings)
                    self.cl.login_by_sessionid(self.session_id)
                    print("✅ لاگین با Session ذخیره شده موفق بود")
                    return True
            
            # لاگین جدید
            self.human_delay()
            self.cl.login_by_sessionid(self.session_id)
            
            # ذخیره Session
            with open(SESSION_FILE, 'wb') as f:
                pickle.dump(self.cl.get_settings(), f)
            
            print("✅ لاگین جدید موفق بود")
            return True
            
        except Exception as e:
            print(f"❌ خطا در لاگین: {e}")
            return False
    
    def get_post_info(self, url):
        """دریافت اطلاعات پست با تاخیر هوشمند"""
        self.human_delay()
        
        # تغییر User-Agent هر 5 درخواست
        if self.request_count % 5 == 0:
            self.cl.set_user_agent(random.choice(self.user_agents))
        
        try:
            # استخراج اطلاعات پست
            media_pk = self.cl.media_pk_from_url(url)
            media_info = self.cl.media_info(media_pk)
            return media_info
        except Exception as e:
            print(f"❌ خطا در دریافت پست: {e}")
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

# --- تابع دانلود ---
def download_and_send(url, chat_id):
    opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'user_agent': random.choice(instagram.user_agents),
        'extract_flat': False,
        'force_generic_extractor': False,
        'http_headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }
    
    try:
        proc_msg = bot.send_message(chat_id, "⏳ در حال پردازش لینک...")
        
        if not os.path.exists('downloads'): 
            os.makedirs('downloads')
        
        # تاخیر قبل از دانلود
        time.sleep(random.uniform(2, 4))
        
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # بررسی وجود فایل
            if os.path.exists(filename):
                with open(filename, 'rb') as f:
                    bot.send_video(chat_id, f, caption="🐲 @dragonn_dl")
                os.remove(filename)
                bot.delete_message(chat_id, proc_msg.message_id)
                
                # ثبت آمار
                db["stats"][str(chat_id)] = db["stats"].get(str(chat_id), 0) + 1
                save_db()
            else:
                bot.send_message(chat_id, "❌ فایل دانلود نشد")
                
    except Exception as e:
        bot.send_message(chat_id, f"❌ خطا: {str(e)[:100]}")

# --- هندلرهای تلگرام ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📥 دانلود ویدیو"),
        types.KeyboardButton("📊 آمار من"),
        types.KeyboardButton("🔄 وضعیت اتصال")
    )
    
    welcome_text = """
🐲 **به ربات دانلود دراگون خوش آمدید!**

✅ **اتصال به اینستاگرام:** فعال
🔗 **روش استفاده:** لینک پست اینستاگرام را بفرستید

📱 **پشتیبانی از:** ریلز، پست، استوری، IGTV
⚡ **سرعت بالا | کیفیت اصلی**

@dragonn_dl
    """
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "📊 آمار من")
def stats(message):
    count = db["stats"].get(str(message.chat.id), 0)
    bot.reply_to(message, f"📊 تعداد دانلودهای شما: {count}")

@bot.message_handler(func=lambda m: m.text == "🔄 وضعیت اتصال")
def connection_status(message):
    status = "✅ متصل" if instagram.cl.user_id else "❌ قطع"
    bot.reply_to(message, f"📱 وضعیت اینستاگرام: {status}")

@bot.message_handler(func=lambda m: m.text == "📥 دانلود ویدیو")
def ask_link(message):
    msg = bot.send_message(
        message.chat.id,
        "🔗 لینک پست اینستاگرام را بفرستید:"
    )
    bot.register_next_step_handler(msg, handle_link)

@bot.message_handler(func=lambda m: "instagram.com" in m.text)
def handle_link(message):
    # بررسی اتصال اینستاگرام
    if not instagram.cl.user_id:
        bot.reply_to(message, "⏳ در حال اتصال به اینستاگرام...")
        if not instagram.login():
            bot.reply_to(message, "❌ خطا در اتصال به اینستاگرام، اما دانلود با لینک ادامه دارد")
    
    # دانلود ویدیو
    threading.Thread(target=download_and_send, args=(message.text, message.chat.id)).start()
    bot.reply_to(message, "⏳ لینک دریافت شد، دانلود شروع شد...")

# --- تمدید خودکار Session ---
def auto_refresh_session():
    """هر 2 هفته یکبار Session رو تمدید کن"""
    while True:
        time.sleep(14 * 24 * 60 * 60)  # 14 روز
        try:
            instagram.login()
            print("✅ Session تمدید شد")
        except:
            print("❌ خطا در تمدید Session")

# --- اجرای اصلی ---
if __name__ == "__main__":
    print("🚀 ربات در حال راه‌اندازی...")
    
    # لاگین اولیه
    if instagram.login():
        print("✅ اتصال به اینستاگرام برقرار شد")
    else:
        print("⚠️ اتصال به اینستاگرام برقرار نشد")
    
    # شروع تمدید خودکار Session
    refresh_thread = threading.Thread(target=auto_refresh_session, daemon=True)
    refresh_thread.start()
    
    # اجرای ربات
    print("🤖 ربات تلگرام فعال شد")
    bot.infinity_polling(skip_pending=True)
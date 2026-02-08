import telebot
from telebot import types
import os, time, threading
from yt_dlp import YoutubeDL
from instagrapi import Client

# --- تنظیمات اصلی ---
TOKEN = "8576338411:AAGRw-zAM2U5CaBsn53fUTWGl1ju_UW3n4I"
INSTA_USER = "dragonn.dl"
INSTA_PASS = "#dragon#$123321"

bot = telebot.TeleBot(TOKEN)
cl = Client()

# --- تابع اصلی دانلود و ارسال (بدون نقص) ---
def download_and_send(url, chat_id):
    opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': f'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True
    }
    try:
        # ارسال پیام در حال پردازش برای اطمینان کاربر
        processing_msg = bot.send_message(chat_id, "⏳ در حال پردازش ویدیو... لطفا شکیبا باشید.")
        
        if not os.path.exists('downloads'): os.makedirs('downloads')
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
            with open(path, 'rb') as v:
                bot.send_video(chat_id, v, caption="بفرمایید! 🐲 @dragonn_dl")
            os.remove(path)
            bot.delete_message(chat_id, processing_msg.message_id)
    except Exception as e:
        bot.send_message(chat_id, f"❌ متاسفانه در دانلود این لینک مشکلی پیش آمد.\nارور: {str(e)[:50]}...")

# --- بخش اینستاگرام (در لایه امنیتی TRY) ---
def safe_insta_login():
    try:
        print("Dragon is trying to login to Instagram... 🐲")
        sid = "72867675539%3AACcKqkPmesZgdm%3A27%3AAYh8Md6lF1xwQD0eTS-5plrnrAOgIcDSDjRR3RwqzQ"
        cl.login_by_sessionid(sid)
        print("Instagram Connected! ✅")
        return True
    except Exception as e:
        print(f"⚠️ Instagram Login Failed: {e}. Bot will still work for Telegram links.")
        return False

def watch_directs_loop():
    while True:
        try:
            # فقط اگر لاگین بود چک کن
            if cl.user_id:
                threads = cl.direct_threads(amount=3)
                for thread in threads:
                    msg = thread.messages[0]
                    if msg.text and "instagram.com" in msg.text and msg.user_id != cl.user_id:
                        if not msg.reactions:
                            # اینجا ایدی تلگرام خودت رو برای تست بذار (مثلا ۵۸۴۳۱۱۰۵۹)
                            threading.Thread(target=download_and_send, args=(msg.text, 584311059)).start()
                            cl.direct_message_react(thread.id, msg.id, '❤️')
            time.sleep(60)
        except:
            time.sleep(120) # اگر ارور داد زمان استراحت رو بیشتر کن

# --- هندلرهای تلگرام (بخش کپی-پیست مستقیم) ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🐲 اژدها بیدار شد!\n\nلینک ریلز اینستاگرام رو اینجا بفرست تا مستقیم دانلود کنم.\n(بخش دایرکت هم در پس‌زمینه فعال است)")

@bot.message_handler(func=lambda m: "instagram.com" in m.text)
def handle_direct_link(message):
    # این بخش همیشه کار می‌کند، حتی اگر اینستاگرام بلاک باشد
    threading.Thread(target=download_and_send, args=(message.text, message.chat.id)).start()

# --- اجرای ربات ---
if __name__ == "__main__":
    # تلاش برای لاگین اینستاگرام در پس‌زمینه
    if safe_insta_login():
        threading.Thread(target=watch_directs_loop, daemon=True).start()
    
    print("Telegram Bot is running... 🚀")
    # استفاده از skip_pending برای جلوگیری از ارور Conflict ۴۰۹
    bot.infinity_polling(skip_pending=True)
    

import telebot
from telebot import types
import os, time, threading
from yt_dlp import YoutubeDL
from instagrapi import Client

# --- تنظیمات اصلی ---
TOKEN = "8576338411:AAGRw-zAM2U5CaBsn53fUTWGl1ju_UW3n4I"
bot = telebot.TeleBot(TOKEN)
cl = Client()

# --- تابع دانلود با استفاده از کوکی (برای رفع ارور Requested content) ---
def download_and_send(url, chat_id):
    # تنظیمات yt-dlp برای عبور از سد اینستاگرام
    opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': f'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        # استفاده از فایل کوکی برای اینکه اینستاگرام اجازه دانلود بدهد
        'cookiefile': 'session.json' if os.path.exists('session.json') else None,
        'add_header': [
            'User-Agent:Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept-Language:en-US,en;q=0.9'
        ]
    }
    
    try:
        processing_msg = bot.send_message(chat_id, "⏳ در حال تلاش برای دانلود ویدیو (نسخه ضد-بلاک)...")
        
        if not os.path.exists('downloads'): os.makedirs('downloads')
        
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
            
            with open(path, 'rb') as v:
                bot.send_video(chat_id, v, caption="بفرمایید! 🐲\n(با موفقیت از سد محدودیت عبور کردیم)")
            
            os.remove(path)
            bot.delete_message(chat_id, processing_msg.message_id)
            
    except Exception as e:
        error_text = str(e)
        if "Requested content is not available" in error_text:
            bot.send_message(chat_id, "❌ اینستاگرام اجازه دسترسی به این ویدیو را نداد. احتمالاً پیج خصوصی است یا آی‌پی سرور موقتاً محدود شده.")
        else:
            bot.send_message(chat_id, f"❌ خطای غیرمنتظره: {error_text[:100]}")

# --- بخش دایرکت اینستاگرام (لایه امنیتی) ---
def safe_insta_login():
    try:
        sid = "72867675539%3AACcKqkPmesZgdm%3A27%3AAYh8Md6lF1xwQD0eTS-5plrnrAOgIcDSDjRR3RwqzQ"
        cl.login_by_sessionid(sid)
        print("Instagram Connected! ✅")
        return True
    except Exception as e:
        print(f"⚠️ Instagram Login Failed: {e}")
        return False

def watch_directs_loop():
    while True:
        try:
            if cl.user_id:
                threads = cl.direct_threads(amount=3)
                for thread in threads:
                    msg = thread.messages[0]
                    if msg.text and "instagram.com" in msg.text and msg.user_id != cl.user_id:
                        if not msg.reactions:
                            # آیدی عددی خودت را اینجا قرار بده
                            threading.Thread(target=download_and_send, args=(msg.text, 584311059)).start()
                            cl.direct_message_react(thread.id, msg.id, '❤️')
            time.sleep(60)
        except:
            time.sleep(120)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🐲 اژدها آماده است!\nلینک ریلز را بفرست تا با سیستم جدید دانلود کنم.")

@bot.message_handler(func=lambda m: "instagram.com" in m.text)
def handle_link(message):
    threading.Thread(target=download_and_send, args=(message.text, message.chat.id)).start()

if __name__ == "__main__":
    if safe_insta_login():
        threading.Thread(target=watch_directs_loop, daemon=True).start()
    bot.infinity_polling(skip_pending=True)
    

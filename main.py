import telebot
from telebot import types
import os, json, threading, time
from yt_dlp import YoutubeDL
import logging

# --- تنظیمات اصلی ---
TOKEN = "8576338411:AAGRw-zAM2U5CaBsn53fUTWGl1ju_UW3n4I"
bot = telebot.TeleBot(TOKEN)
DB_FILE = "users_data.json"

# --- دیتابیس ---
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

# --- تابع دانلود ---
def download_and_send(url, chat_id):
    opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    try:
        proc_msg = bot.send_message(chat_id, "⏳ در حال دانلود...")
        
        if not os.path.exists('downloads'): 
            os.makedirs('downloads')
        
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # پیدا کردن فایل دانلود شده
            if os.path.exists(filename):
                with open(filename, 'rb') as f:
                    bot.send_video(chat_id, f, caption="🐲 @dragonn_dl")
                os.remove(filename)
            else:
                # اگه فایل با اسم دیگه ذخیره شده
                for file in os.listdir('downloads'):
                    if file.endswith(('.mp4', '.mkv', '.webm')):
                        with open(f'downloads/{file}', 'rb') as f:
                            bot.send_video(chat_id, f, caption="🐲 @dragonn_dl")
                        os.remove(f'downloads/{file}')
                        break
            
            bot.delete_message(chat_id, proc_msg.message_id)
            
            # ثبت آمار
            db["stats"][str(chat_id)] = db["stats"].get(str(chat_id), 0) + 1
            save_db()
            
    except Exception as e:
        bot.send_message(chat_id, f"❌ خطا: {str(e)[:100]}")

# --- هندلرهای تلگرام ---
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📥 دانلود"),
        types.KeyboardButton("📊 آمار")
    )
    
    bot.send_message(
        message.chat.id,
        "🐲 **ربات دانلود اینستاگرام**\n\n"
        "✅ **فقط کافیه لینک پست یا ریلز بفرستی**\n"
        "مثال: https://www.instagram.com/reel/...\n\n"
        "⚡ بدون نیاز به اتصال به اینستاگرام",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text == "📊 آمار")
def stats(message):
    count = db["stats"].get(str(message.chat.id), 0)
    bot.reply_to(message, f"📊 تعداد دانلودهای شما: {count}")

@bot.message_handler(func=lambda m: m.text == "📥 دانلود")
def ask_link(message):
    msg = bot.send_message(message.chat.id, "🔗 لینک اینستاگرام را بفرستید:")
    bot.register_next_step_handler(msg, handle_link)

@bot.message_handler(func=lambda m: "instagram.com" in m.text or "instagr.am" in m.text)
def handle_link(message):
    bot.reply_to(message, "⏳ لینک دریافت شد، دانلود شروع شد...")
    threading.Thread(target=download_and_send, args=(message.text, message.chat.id)).start()

# --- اجرا ---
if __name__ == "__main__":
    print("🚀 ربات در حال راه‌اندازی...")
    print("🤖 ربات تلگرام فعال شد")
    bot.infinity_polling(skip_pending=True)
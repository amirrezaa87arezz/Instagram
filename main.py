import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from yt_dlp import YoutubeDL

# فعال‌سازی لاگ برای عیب‌یابی راحت در Railway
logging.basicConfig(level=logging.INFO)

# دریافت توکن
TOKEN = "8576338411:AAGRw-zAM2U5CaBsn53fUTWGl1ju_UW3n4I"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# تنظیمات حرفه‌ای yt-dlp
YDL_OPTIONS = {
    'format': 'best[ext=mp4]/best', 
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
}

async def download_insta(url):
    try:
        with YoutubeDL(YDL_OPTIONS) as ydl:
            # استخراج اطلاعات و دانلود
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        logging.error(f"Download Error: {e}")
        return None

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.reply(
        "👋 سلام! من ربات دانلودر اینستاگرام هستم.\n\n"
        "🔗 کافیه لینک **Post**, **Reels** یا **Story** رو بفرستی تا برات دانلود کنم."
    )

@dp.message(F.text.contains("instagram.com"))
async def handle_instagram_link(message: types.Message):
    sent_msg = await message.reply("⏳ در حال پردازش لینک... لطفاً کمی صبر کنید.")
    
    # اجرای عملیات دانلود در پس‌زمینه
    file_path = await asyncio.to_thread(download_insta, message.text)

    if file_path and os.path.exists(file_path):
        try:
            await sent_msg.edit_text("📤 در حال آپلود فایل...")
            video_file = types.FSInputFile(file_path)
            
            # ارسال به عنوان ویدیو
            await message.answer_video(
                video_file, 
                caption="✅ دانلود شده توسط ربات شما",
                supports_streaming=True
            )
        except Exception as e:
            await message.answer(f"❌ خطا در ارسال فایل: {e}")
        finally:
            # حذف فایل برای جلوگیری از پر شدن حافظه هاست
            if os.path.exists(file_path):
                os.remove(file_path)
            await sent_msg.delete()
    else:
        await sent_msg.edit_text("❌ متأسفانه نتونستم این لینک رو دانلود کنم.\n"
                               "مطمئن شو صفحه عمومی (Public) باشه.")

async def main():
    # ایجاد پوشه دانلود اگر وجود نداشته باشه
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    
    logging.info("Bot is running...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

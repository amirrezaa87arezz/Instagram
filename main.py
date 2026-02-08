import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from yt_dlp import YoutubeDL

logging.basicConfig(level=logging.INFO)

TOKEN = "8576338411:AAGRw-zAM2U5CaBsn53fUTWGl1ju_UW3n4I"
bot = Bot(token=TOKEN)
dp = Dispatcher()

YDL_OPTIONS = {
    'format': 'best[ext=mp4]/best', 
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
}

async def download_insta(url):
    try:
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=True)
            return ydl.prepare_filename(info)
    except Exception as e:
        logging.error(f"Download Error: {e}")
        return None

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.reply("سلام! لینک اینستاگرام رو بفرست تا برات دانلود کنم. 🔥")

@dp.message(F.text.contains("instagram.com"))
async def handle_instagram_link(message: types.Message):
    sent_msg = await message.reply("⏳ در حال پردازش...")
    
    file_path = await asyncio.to_thread(download_insta, message.text)

    if file_path and os.path.exists(file_path):
        try:
            await sent_msg.edit_text("📤 در حال ارسال به تلگرام...")
            video_file = types.FSInputFile(file_path)
            await message.answer_video(video_file, caption="بفرمایید! ✅")
        except Exception as e:
            await message.answer(f"❌ خطای ارسال: {e}")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
            await sent_msg.delete()
    else:
        await sent_msg.edit_text("❌ خطا در دانلود! مطمئن شوید پیج عمومی است.")

async def main():
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

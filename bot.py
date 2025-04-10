import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile
from aiogram.utils import executor

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
OWNER_ID = int(os.getenv("OWNER_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start_cmd(msg: types.Message):
    if msg.from_user.id == OWNER_ID:
        await msg.reply("👑 Welcome, Admin. Send me a video to upload.")
    else:
        await msg.reply("🚫 Access Denied.")

@dp.message_handler(content_types=types.ContentType.VIDEO)
async def handle_video(msg: types.Message):
    if msg.from_user.id != OWNER_ID:
        return await msg.reply("🚫 You're not authorized.")
    
    await msg.reply("✅ Got the video. Now send the **title**.")
    dp.register_message_handler(get_title, content_types=types.ContentType.TEXT, state=None, video=msg.video)

async def get_title(msg: types.Message, video):
    title = msg.text
    await msg.reply("📸 Now send the **thumbnail image**.")
    dp.register_message_handler(get_thumb, content_types=types.ContentType.PHOTO, state=None, video=video, title=title)

async def get_thumb(msg: types.Message, video, title):
    photo = msg.photo[-1]
    file = await bot.get_file(photo.file_id)
    thumb_path = await photo.download(destination_file="thumb.jpg")

    await bot.send_video(
        chat_id=CHANNEL_ID,
        video=video.file_id,
        caption=f"🎬 <b>{title}</b>",
        parse_mode="HTML",
        thumbnail=InputFile("thumb.jpg")
    )
    await msg.reply("✅ Video uploaded to channel!")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

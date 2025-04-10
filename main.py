from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InputFile
import os

API_TOKEN = '8110894182:AAHjRQyoWxKVcIvC6vspcRxLB7Nu0MjDlMs'
ADMIN_ID = 6734490263
CHANNEL_ID = -1002509288899

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(content_types=types.ContentType.VIDEO)
async def handle_video(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    await message.reply("Send me the *title* of the video:", parse_mode="Markdown")
    dp.register_message_handler(lambda msg: get_title(msg, message.video), content_types=types.ContentType.TEXT, state=None)

async def get_title(title_msg: types.Message, video):
    title = title_msg.text
    await title_msg.reply("Now send me the *thumbnail* image (or type 'skip')", parse_mode="Markdown")
    
    dp.register_message_handler(lambda msg: get_thumbnail(msg, video, title), content_types=[types.ContentType.PHOTO, types.ContentType.TEXT], state=None)

async def get_thumbnail(thumbnail_msg: types.Message, video, title):
    if thumbnail_msg.text and thumbnail_msg.text.lower() == "skip":
        await bot.send_video(chat_id=CHANNEL_ID, video=video.file_id, caption=title)
    elif thumbnail_msg.photo:
        thumbnail_file_id = thumbnail_msg.photo[-1].file_id
        await bot.send_video(chat_id=CHANNEL_ID, video=video.file_id, caption=title, thumb=thumbnail_file_id)
    else:
        await thumbnail_msg.reply("Invalid thumbnail. Try again or type 'skip'.")

if __name__ == '__main__':
    executor.start_polling(dp)

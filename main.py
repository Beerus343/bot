import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile
from aiogram.dispatcher.webhook import get_new_configured_app

API_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

WEBHOOK_HOST = 'https://your-render-app-name.onrender.com'
WEBHOOK_PATH = f'/webhook/{API_TOKEN}'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

@dp.message_handler(content_types=types.ContentType.VIDEO, user_id=ADMIN_ID)
async def handle_video(message: types.Message):
    await message.reply("Send the thumbnail image now:")
    dp.register_message_handler(get_thumbnail, content_types=types.ContentType.PHOTO, state=None)

async def get_thumbnail(message: types.Message):
    thumbnail = message.photo[-1]
    await message.reply("Send the title for the video:")
    dp.register_message_handler(lambda m: post_to_channel(m, thumbnail), content_types=types.ContentType.TEXT, state=None)

async def post_to_channel(message: types.Message, thumbnail):
    caption = message.text
    file_id = message.reply_to_message.video.file_id
    await bot.send_video(CHANNEL_ID, video=file_id, caption=caption, thumb=thumbnail.file_id)
    await message.reply("✅ Posted to channel!")

async def on_shutdown(app):
    await bot.delete_webhook()

app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_PATH)
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=int(os.environ.get('PORT', 3000)))

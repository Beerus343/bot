from aiogram import Bot, Dispatcher, types
from aiogram.types import FSInputFile
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

@dp.message(commands=["start"])
async def start_handler(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Send me a video, bro.")

@dp.message(content_types=types.ContentType.VIDEO)
async def handle_video(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer("Send me the title.")
    dp["video"] = message.video.file_id  # Store video temporarily
    dp["step"] = "awaiting_title"

@dp.message()
async def handle_title_and_post(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    if dp.get("step") == "awaiting_title":
        video_file = dp["video"]
        title = message.text
        await bot.send_video(CHANNEL_ID, video=video_file, caption=title)
        await message.answer("Video sent to channel.")
        dp["step"] = None
        dp["video"] = None

# Webhook app setup
async def on_startup(app):
    webhook_url = os.getenv("WEBHOOK_URL")
    await bot.set_webhook(webhook_url)

app = web.Application()
app["bot"] = bot
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path="/webhook")
app.on_startup.append(on_startup)
setup_application(app, dp, bot=bot)

if __name__ == "__main__":
    web.run_app(app, port=int(os.getenv("PORT", 8000)))

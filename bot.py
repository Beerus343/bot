import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from datetime import datetime
import aiofiles

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Store state per user session
user_sessions = {}

# Command: /start
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return
    await message.reply("Yo! Send the video you want to upload.")

# Step 1: Receive Video
@dp.message_handler(content_types=types.ContentType.VIDEO)
async def handle_video(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return

    user_sessions[message.from_user.id] = {"video": message.video.file_id}
    await message.reply("Now send the thumbnail image.")

# Step 2: Receive Thumbnail
@dp.message_handler(content_types=types.ContentType.PHOTO)
async def handle_thumbnail(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return

    if message.from_user.id in user_sessions:
        user_sessions[message.from_user.id]["thumbnail"] = message.photo[-1].file_id
        await message.reply("Cool. Now send the title for your post.")

# Step 3: Receive Title and Post Options
@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_title_or_schedule(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return

    session = user_sessions.get(message.from_user.id, {})
    if "thumbnail" in session and "video" in session and "title" not in session:
        session["title"] = message.text
        user_sessions[message.from_user.id] = session
        await message.reply("Got it. Send time to post (HH:MM in 24hr) or type `now`.")
        return

    # Step 4: Time to post
    session = user_sessions.get(message.from_user.id, {})
    if "title" in session and session.get("scheduled") != True:
        if message.text.lower() == "now":
            await post_video(session)
        else:
            try:
                post_time = datetime.strptime(message.text, "%H:%M").time()
                session["scheduled"] = True
                now = datetime.now()
                target_time = datetime.combine(now.date(), post_time)
                if target_time < now:
                    target_time = datetime.combine(now.date(), post_time) + timedelta(days=1)
                delay = (target_time - now).total_seconds()
                await message.reply(f"Scheduled! Will post at {post_time.strftime('%H:%M')}.")
                asyncio.create_task(schedule_post(session, delay))
            except Exception as e:
                await message.reply("Invalid time format. Use HH:MM (24hr).")

async def schedule_post(session, delay):
    await asyncio.sleep(delay)
    await post_video(session)

async def post_video(session):
    video = session["video"]
    thumb = session["thumbnail"]
    title = session["title"]

    # DISKWALA upload logic would be here - simulated for now
    diskwala_link = "https://diskwala.link/yourvideo"

    btn = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="📥 Download Now", url=diskwala_link)
    ]])

    await bot.send_video(
        chat_id=CHANNEL_ID,
        video=video,
        thumb=thumb,
        caption=f"🔥 {title}",
        reply_markup=btn
    )

    # Optionally send a success log to admin or store it

    del user_sessions[OWNER_ID]

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp)

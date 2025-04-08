from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os, requests
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")

LV_COOKIES = os.getenv("LINKVERTISE_COOKIES")
LV_USER_AGENT = os.getenv("LINKVERTISE_USER_AGENT")

app = Client("diskwala_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_sessions = {}

def shorten_linkvertise(diskwala_url):
    headers = {
        "Cookie": LV_COOKIES,
        "User-Agent": LV_USER_AGENT,
    }
    data = {
        "url": diskwala_url
    }
    response = requests.post("https://publisher.linkvertise.com/api/link/create", headers=headers, data=data)
    try:
        return response.json()['data']['link']
    except:
        return None

@app.on_message(filters.private & filters.text)
async def handle_link(client, message):
    user_id = message.from_user.id
    if user_id not in user_sessions:
        if not message.text.startswith("http"):
            await message.reply("Send a valid DiskWala link to start.")
            return
        user_sessions[user_id] = {'link': message.text}
        await message.reply("Send the title for the post:")
    elif 'title' not in user_sessions[user_id]:
        user_sessions[user_id]['title'] = message.text
        await message.reply("Send the thumbnail image URL:")
    elif 'thumbnail' not in user_sessions[user_id]:
        user_sessions[user_id]['thumbnail'] = message.text
        link = user_sessions[user_id]['link']
        title = user_sessions[user_id]['title']
        thumb = user_sessions[user_id]['thumbnail']

        short_link = shorten_linkvertise(link)
        if not short_link:
            await message.reply("❌ Failed to shorten with Linkvertise. Check your cookies/session.")
            user_sessions.pop(user_id)
            return

        caption = f"""📥 <b>{title}</b>

🎯 <b>Fast Download via DiskWala</b>  
💸 <i>Powered by Linkvertise</i>  
        
Click the button below to download ⬇️"""

        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("📥 Download Now", url=short_link)]
        ])

        try:
            await client.send_photo(
                chat_id=CHANNEL_ID,
                photo=thumb,
                caption=caption,
                reply_markup=btn,
                parse_mode="html"
            )
            await message.reply("✅ Successfully posted to channel.")
        except Exception as e:
            await message.reply(f"❌ Failed to post: {e}")

        user_sessions.pop(user_id)

app.run()

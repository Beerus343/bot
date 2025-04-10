import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
CHANNEL_ID = os.getenv("CHANNEL_ID")

user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    await update.message.reply_text("👀 Send the video file.")

async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    file_id = update.message.video.file_id
    user_sessions[update.effective_user.id] = {'video': file_id}
    await update.message.reply_text("📷 Now send the thumbnail image.")

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    user_sessions[update.effective_user.id]['thumb'] = update.message.photo[-1].file_id
    await update.message.reply_text("✍️ Send the title for the video.")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    session = user_sessions.get(update.effective_user.id)
    if session and 'video' in session and 'thumb' in session:
        title = update.message.text
        await context.bot.send_video(
            chat_id=CHANNEL_ID,
            video=session['video'],
            thumb=session['thumb'],
            caption=f"🔥 <b>{title}</b>",
            parse_mode="HTML"
        )
        await update.message.reply_text("✅ Uploaded successfully.")
        user_sessions.pop(update.effective_user.id)
    else:
        await update.message.reply_text("⚠️ Please start with /start and send the video first.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO, video_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), text_handler))

    app.run_polling()

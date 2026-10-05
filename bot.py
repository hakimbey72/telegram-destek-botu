import os
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8113543475:AAGVok833wnF6H2UZ_x8ML9rFSqm_4YJih0"
ADMIN_GROUP_ID = -5300290442

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Merhaba! Destek hattına hoş geldiniz. Mesajınızı buraya yazabilirsiniz.")

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == 'private':
        user = update.effective_user
        info_text = (
            f"📩 **Yeni Destek Mesajı**\n"
            f"👤 **Gönderen:** {user.full_name} (@{user.username or 'Yok'})\n"
            f"🆔 **User ID:** `{user.id}`\n"
            f"----------------------------------------"
        )
        await context.bot.send_message(chat_id=ADMIN_GROUP_ID, text=info_text, parse_mode='Markdown')
        await update.message.forward(chat_id=ADMIN_GROUP_ID)
        await update.message.reply_text("Mesajınız destek ekibimize iletildi.")

async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id == ADMIN_GROUP_ID and update.message.reply_to_message:
        reply_to = update.message.reply_to_message
        target_user_id = None

        if reply_to.forward_from:
            target_user_id = reply_to.forward_from.id
        elif reply_to.text and "User ID:" in reply_to.text:
            try:
                target_user_id = int(reply_to.text.split("User ID:")[1].split("\n")[0].strip().replace("`", ""))
            except Exception:
                pass

        if target_user_id:
            try:
                await context.bot.copy_message(
                    chat_id=target_user_id,
                    from_chat_id=ADMIN_GROUP_ID,
                    message_id=update.message.message_id
                )
            except Exception as e:
                await update.message.reply_text(f"❌ Mesaj iletilemedi: {e}")

# Render'ın uyanık kalması için web yanıtı
async def handle_ping(request):
    return web.Response(text="Bot 7/24 Aktif!")

async def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ChatType.PRIVATE & ~filters.COMMAND, handle_user_message))
    application.add_handler(MessageHandler(filters.CHAT & ~filters.COMMAND, handle_admin_reply))

    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    async with application:
        await application.start()
        await application.updater.start_polling()
        await asyncio.Event().wait()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
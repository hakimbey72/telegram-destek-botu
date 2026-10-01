import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Log ayarları
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# BOT BİLGİLERİN
BOT_TOKEN = "8113543475:AAGVok833wnF6H2UZ_x8ML9rFSqm_4YJih0"
YONETICI_GRUP_ID = -5300290442

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = (
        f"Merhaba {user.first_name}! 👋\n\n"
        "Şikayet, öneri veya destek talebinizi bu sohbet üzerinden yazabilirsiniz. "
        "Ekibimiz en kısa sürede size dönüş yapacaktır."
    )
    await update.message.reply_text(welcome_text)

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Yönetici grubundan gelen mesajları işleme alma
    if update.effective_chat.id == YONETICI_GRUP_ID:
        return

    header = (
        f"📩 **Yeni Destek/Şikayet Mesajı**\n"
        f"👤 **Gönderen:** {user.full_name} (@{user.username if user.username else 'Yok'})\n"
        f"🆔 **ID:** `{user.id}`\n"
        f"-----------------------------------\n"
    )

    # Yönetici grubuna bilgilendirme ve mesaj iletimi
    await context.bot.send_message(
        chat_id=YONETICI_GRUP_ID,
        text=header,
        parse_mode="Markdown"
    )
    
    forwarded_msg = await update.message.forward(chat_id=YONETICI_GRUP_ID)
    context.bot_data[forwarded_msg.message_id] = user.id

    await update.message.reply_text("Mesajınız destek ekibimize iletildi. En kısa sürede yanıt alacaksınız.")

async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != YONETICI_GRUP_ID:
        return

    reply_to = update.message.reply_to_message
    if not reply_to:
        return

    target_user_id = None
    if reply_to.forward_from:
        target_user_id = reply_to.forward_from.id
    elif reply_to.message_id in context.bot_data:
        target_user_id = context.bot_data[reply_to.message_id]

    if target_user_id:
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"💬 **Destek Ekibinden Yanıt:**\n\n{update.message.text}"
            )
            await update.message.reply_text("✅ Yanıt kullanıcıya iletildi.")
        except Exception as e:
            await update.message.reply_text(f"❌ Yanıt iletilemedi. Hata: {e}")
    else:
        await update.message.reply_text("⚠️ Yanıtlanacak kullanıcı tespit edilemedi.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & ~filters.COMMAND, handle_user_message))
    app.add_handler(MessageHandler(filters.Chat(YONETICI_GRUP_ID) & filters.REPLY, handle_admin_reply))

    print("Bot basariyla baslatildi ve dinleniyor...")
    app.run_polling()
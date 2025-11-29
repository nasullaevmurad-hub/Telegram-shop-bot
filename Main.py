import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, filters, ContextTypes

ASK_NAME, ASK_PHONE, ASK_PRODUCT = range(3)

logging.basicConfig(level=logging.INFO)

ADMIN_ID = 123456789       # O'zingning ID'ingni qo'y
TOKEN = "BOT_TOKEN"        # Bot tokenni qo'y

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Ismingizni kiriting:")
    return ASK_NAME

async def ask_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text

    keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton("📞 Telefon raqamni yuborish", request_contact=True)]],
        resize_keyboard=True
    )
    await update.message.reply_text("Telefon raqamingizni yuboring:", reply_markup=keyboard)
    return ASK_PHONE

async def save_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    if contact:
        context.user_data["phone"] = contact.phone_number
    else:
        context.user_data["phone"] = update.message.text

    await update.message.reply_text(
        "Qaysi tovarni sotib olmoqchisiz? Rasm yoki to'liq nomini yuboring.",
        reply_markup=None
    )
    return ASK_PRODUCT

async def save_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data.get("name")
    phone = context.user_data.get("phone")

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        product_info = "📷 Rasm yuborildi"
    else:
        file_id = None
        product_info = f"📝 Mahsulot nomi: {update.message.text}"

    admin_text = (
        f"🟢 Yangi buyurtma:\n\n"
        f"👤 Ism: {name}\n"
        f"📞 Telefon: {phone}\n"
        f"{product_info}"
    )

    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text)

    if file_id:
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=file_id)

    await update.message.reply_text("Rahmat! Buyurtmangiz qabul qilindi.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Jarayon bekor qilindi.")
    return ConversationHandler.END


def main():
    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            ASK_PHONE: [MessageHandler(filters.CONTACT | filters.TEXT, save_phone)],
            ASK_PRODUCT: [MessageHandler(filters.PHOTO | filters.TEXT, save_product)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__":
    main()

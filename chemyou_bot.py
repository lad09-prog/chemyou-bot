import logging
import re
import requests
from io import BytesIO
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ⬇️ Замените на свой токен
TELEGRAM_BOT_TOKEN = "K85732521188957"
OCR_API_KEY = "helloworld"  # Тестовый ключ от OCR.space

logging.basicConfig(level=logging.INFO)

# 📌 Регулярное выражение для извлечения показателей
VALUE_REGEX = re.compile(r'([\w\s\-%\(\)/]+):\s*([0-9]+[.,]?[0-9]*)')

def parse_blood_values(text):
    matches = VALUE_REGEX.findall(text)
    if not matches:
        return None
    return "\n".join([f"{k.strip()}: {v}" for k, v in matches])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send me your blood test results as text or a photo.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    parsed = parse_blood_values(user_text)
    if parsed:
        await update.message.reply_text(f"✅ I found these results:\n\n{parsed}")
    else:
        await update.message.reply_text(
            "❌ Sorry, I couldn't recognize your test results.\n\nPlease send them in this format:\nHemoglobin: 120\nIron: 9\nVitamin D: 18"
        )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    photo_bytes = BytesIO()
    await photo_file.download_to_memory(out=photo_bytes)
    photo_bytes.seek(0)

    try:
        ocr_text = extract_text_with_ocr(photo_bytes)
        parsed = parse_blood_values(ocr_text)
        if parsed:
            await update.message.reply_text(f"📸 Extracted results:\n\n{parsed}")
        else:
            await update.message.reply_text("❌ I couldn't extract values from the image.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error processing image: {str(e)}")

def extract_text_with_ocr(image_bytes):
    response = requests.post(
        'https://api.ocr.space/parse/image',
        files={'file': ('image.jpg', image_bytes)},
        data={'apikey': OCR_API_KEY, 'language': 'eng'},
    )
    result = response.json()
    return result['ParsedResults'][0]['ParsedText'] if result['IsErroredOnProcessing'] is False else ""

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    main()

import logging
import pytesseract
from PIL import Image
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CommandHandler, ContextTypes

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Your Bot Token (replace with your actual token before running)
BOT_TOKEN = "8440029324:AAEcZt7-GOcCzOles_tkXzncgJcul8OXhLY"

# Expanded test keywords for better recognition
TEST_KEYWORDS = {
    "Hemoglobin": "HGB",
    "Iron": "Fe",
    "Vitamin D": "Vit D",
    "Glucose": "Glucose",
    "WBC": "WBC",
    "RBC": "RBC",
    "HCT": "HCT",
    "MCV": "MCV",
    "MCH": "MCH",
    "MCHC": "MCHC",
    "PLT": "PLT",
    "NEUT": "NEUT",
    "LYMPH": "LYMPH",
    "MO": "MO",
    "EO": "EO",
    "BA": "BA",
    "ESR": "ESR",
    "Neutrophils": "NE",
    "Lymphocytes": "LY",
    "Monocytes": "MO",
    "Eosinophils": "EO",
    "Basophils": "BA",
    "Sedimentation rate": "ESR",
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to ChemYou bot! ð¤\nPlease send a photo or write your blood test like:\nHemoglobin: 120\nIron: 9\nVitamin D: 18")

def extract_values(text: str):
    result = {}
    lines = text.splitlines()
    for line in lines:
        for key in TEST_KEYWORDS.keys():
            if key.lower() in line.lower():
                parts = line.split(":")
                if len(parts) >= 2:
                    try:
                        val = float(parts[1].split()[0])
                        result[TEST_KEYWORDS[key]] = val
                    except:
                        continue
    return result

def get_recommendations(values):
    recs = []
    if "HGB" in values and values["HGB"] < 117:
        recs.append("Your hemoglobin is low. Consider iron supplements and check ferritin.")
    if "Iron" in values and values["Iron"] < 8:
        recs.append("Iron appears to be low. Consider dietary sources like red meat or supplementation.")
    if "Vit D" in values and values["Vit D"] < 30:
        recs.append("Vitamin D is low. A D3 supplement may help.")
    if "WBC" in values and values["WBC"] > 10:
        recs.append("High white blood cells may indicate inflammation or infection.")
    if not recs:
        recs.append("Everything looks fine from the data provided. ð")
    return "\n".join(recs)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    photo_file = await photo.get_file()
    photo_path = "temp_photo.jpg"
    await photo_file.download_to_drive(photo_path)

    try:
        text = pytesseract.image_to_string(Image.open(photo_path), lang="eng+rus")
        values = extract_values(text)
        if values:
            summary = "\n".join([f"{k}: {v}" for k, v in values.items()])
            recs = get_recommendations(values)
            await update.message.reply_text(f"Detected values:\n{summary}\n\nRecommendations:\n{recs}")
        else:
            await update.message.reply_text("Sorry, I couldn't read any known values. Please try a clearer image.")
    except Exception as e:
        await update.message.reply_text(f"Error processing image: {e}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    values = extract_values(user_text)
    if values:
        summary = "\n".join([f"{k}: {v}" for k, v in values.items()])
        recs = get_recommendations(values)
        await update.message.reply_text(f"Detected values:\n{summary}\n\nRecommendations:\n{recs}")
    else:
        await update.message.reply_text("Sorry, I couldn't recognize your test results. Please send in format:\nHemoglobin: 120\nIron: 9\nVitamin D: 18")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if name == "__main__":
    main()

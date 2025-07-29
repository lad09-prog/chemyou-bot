from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Вставь свой токен сюда
TELEGRAM_TOKEN = "8440029324:AAEcZt7-GOcCzOles_tkXzncgJcul8OXhLY"

# Нормальные диапазоны (пример)
REFERENCE = {
    "hemoglobin": (120, 160),    # g/l
    "iron": (10, 30),            # umol/l
    "vitamin d": (30, 100),      # ng/ml
    "glucose": (3.9, 6.1)        # mmol/l
}

def analyze_value(param, value):
    if param in REFERENCE:
        low, high = REFERENCE[param]
        if value < low:
            return "low", "🟡"
        elif value > high:
            return "high", "🟡"
        else:
            return "normal", "🟢"
    return "unknown", "⚪"

def parse_blood_test(text):
    results = []
    lines = text.lower().split('\n')
    for line in lines:
        for param in REFERENCE.keys():
            if param in line:
                try:
                    value = float(''.join([ch for ch in line if (ch.isdigit() or ch=='.' or ch==',')]).replace(',', '.'))
                    status, emoji = analyze_value(param, value)
                    results.append((param.title(), value, status, emoji))
                except Exception:
                    results.append((param.title(), 'N/A', 'unknown', '⚪'))
    return results

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I’m ChemYou Bot — your personal chemical profile assistant.\n"
        "Please send your blood test results (as text, e.g.\n"
        "'Hemoglobin: 120\\nIron: 9\\nVitamin D: 18\\nGlucose: 5.0')"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send me your blood test results and I’ll analyze them and give you recommendations!"
    )

async def analyze_blood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "guide" in text:
        await guide_command(update, context)
        return
    results = parse_blood_test(text)
    if not results:
        await update.message.reply_text(
            "Sorry, I couldn't recognize your test results. Please send in format:\nHemoglobin: 120\nIron: 9\nVitamin D: 18\nGlucose: 5.0"
        )
        return
    summary = "Here’s your chemical profile:\n"
    advice = []
    flag = False
    for param, value, status, emoji in results:
        summary += f"{param}: {value} ({status}) {emoji}\n"
        if status == "low":
            advice.append(f"- {param}: Increase intake or consult a doctor.")
            flag = True
        elif status == "high":
            advice.append(f"- {param}: May be above normal, check with a specialist.")
            flag = True
    if not advice:
        advice.append("All values are in the normal range. Keep up the good work!")
    motivation = (
        "\n\nMotivational tip:\n"
        "Change takes time — small steps matter! If you want a free guide on building habits, just type 'Guide'."
    )
    await update.message.reply_text(summary + "\nRecommendations:\n" + "\n".join(advice) + motivation)

async def guide_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Building new habits is a journey! Here’s a quick-start guide: [insert link to PDF or article here].\n"
        "Remember: celebrate small wins and take it step by step. ChemYou is here to support you!"
    )

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_blood))
    app.add_handler(MessageHandler(filters.Regex("(?i)guide"), guide_command))

    print("Bot is running... Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()

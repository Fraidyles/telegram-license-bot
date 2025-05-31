import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)

# Логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Состояния
CHOOSING, CHECK_LICENSE, SEND_TEMPLATE, SEND_PROGRAM = range(4)

# Шаблоны резюме
templates = {
    "GP": "📄 *Шаблон резюме для GP*:\n\nОбучение на платформе Геткурс...\n(текст шаблона GP)",
    "BT": "📄 *Шаблон резюме для BT*:\n\nКурс включает 20 онлайн-занятий...\n(текст шаблона BT)",
    "GD Полина Ганжара": "📄 *Шаблон для GD Полина Ганжара*:\n\n20 занятий по 2 часа...\n(текст шаблона Ганжара)",
    "GD Ксения Исламова": "📄 *Шаблон для GD Ксения Исламова*:\n\n54 мини-урока по 30 минут...\n(текст шаблона Исламова)",
    "Specialist Гинеколог": "📄 *Шаблон для Specialist-гинеколога*:\n\n15 занятий по 2 часа...\n(текст шаблона Specialist)",
    "Резидентура": "📄 *Шаблон для Резидентуры*:\n\nСопровождение поступления...\n(текст резидентуры)"
}

# Программы курсов
programs = {
    "GP": "📘 *Программа курса GP*:\n\n- Кардиология\n- Пульмонология\n...",
    "BT": "📘 *Программа курса BT*:\n\n🔗 Ссылка: https://clck.ru/3FAPvx",
    "GD Полина Ганжара": "📘 *Программа курса GD (Полина Ганжара)*:\n\n1. Патология полости рта\n2. Инфекции\n...",
    "Specialist Гинеколог": "📘 *Программа курса Specialist - Гинекология*:\n\n1. Анатомия и физиология\n2. Планирование беременности\n...",
    "Spec Дерматолог": "📘 *Дерматология*:\n\nБлок 1 (Н. Калешук): Acne, Psoriasis, Skin Cancer\nБлок 2 (Ю. Кузьменко): Hair, Nails, AGA\n...",
    "Spec Кардиолог": "📘 *Кардиология*:\n\n1. Hypertension, ECG, MI\n2. Atrial Fibrillation\n..."
}

# Клавиатуры
main_keyboard = [["🩺 Определить лицензию"], ["📄 Шаблоны резюме"], ["📘 Программа курса"]]
template_keyboard = [[key] for key in templates]
program_keyboard = [[key] for key in programs]

# Обработчики
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "👋 Привет! Я помогу тебе с медицинской лицензией в ОАЭ. Выбери опцию:",
        reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
    )
    return CHOOSING

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    if text == "🩺 Определить лицензию":
        await update.message.reply_text("🔍 Напиши, какой у тебя диплом, опыт, и в какой области хочешь получить лицензию.")
        return CHECK_LICENSE
    elif text == "📄 Шаблоны резюме":
        await update.message.reply_text("Выбери шаблон:", reply_markup=ReplyKeyboardMarkup(template_keyboard, resize_keyboard=True))
        return SEND_TEMPLATE
    elif text == "📘 Программа курса":
        await update.message.reply_text("Выбери курс:", reply_markup=ReplyKeyboardMarkup(program_keyboard, resize_keyboard=True))
        return SEND_PROGRAM
    else:
        await update.message.reply_text("Пожалуйста, выбери одну из опций.")
        return CHOOSING

async def check_license(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    msg = update.message.text.lower()
    result = "⚠️ Не удалось определить. Попробуй описать подробнее."
    if "гинеколог" in msg or "акушер" in msg:
        result = "✅ Вам подходит лицензия Specialist."
    elif "стоматолог" in msg:
        result = "✅ Вам подходит лицензия General Dentist (GD)."
    elif "терапевт" in msg or "педиатр" in msg:
        result = "✅ Вам подходит лицензия GP."
    await update.message.reply_text(result)
    return CHOOSING

async def send_template(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    key = update.message.text
    text = templates.get(key, "⚠️ Не найден шаблон для этой категории.")
    await update.message.reply_text(text, parse_mode="Markdown")
    return CHOOSING

async def send_program(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    key = update.message.text
    text = programs.get(key, "⚠️ Не найдена программа для этой категории.")
    await update.message.reply_text(text, parse_mode="Markdown")
    return CHOOSING

# Запуск бота
def main():
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    application = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_choice)],
            CHECK_LICENSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_license)],
            SEND_TEMPLATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_template)],
            SEND_PROGRAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_program)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == "__main__":
    main()
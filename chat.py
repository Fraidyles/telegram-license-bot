import json
import os

# Загрузка шаблонов резюме
with open("templates.json", "r", encoding="utf-8") as f:
    templates = json.load(f)

# Загрузка программ курсов
with open("programs.json", "r", encoding="utf-8") as f:
    programs = json.load(f)
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
CHOOSING, PROFESSION, EDUCATION, SPECIALITY_CHECK, EXPERIENCE, POSTGRADUATE_EDU, POSTGRADUATE_YEARS, ACCREDITATION, FROM_RUSSIA, SEND_TEMPLATE, SEND_PROGRAM = range(11)

# Кнопки
main_keyboard = [["🩺 Определить лицензию"], ["📄 Шаблоны резюме"], ["📘 Программа курса"]]
programs = {
    "GP": "...текст программы GP...",
    "BT": "Ссылка на программу - https://clck.ru/3FAPvx",
    "GD Полина Ганжара": "...текст программы Ганжара...",
    "Specialist Гинеколог": "...текст программы Гинекология...",
    "Spec Дерматолог": "...",
    "Spec Кардиолог": "..."
}

# Шаблоны резюме
templates = {
    "GP": "...текст шаблона GP...",
    "BT": programs["BT"],  # вставляем уже готовый текст из programs
    "GD Полина Ганжара": "...текст шаблона Ганжара...",
    "GD Ксения Исламова": "...текст шаблона Исламова...",
    "Specialist Гинеколог": "...текст шаблона Гинеколог...",
    "Резидентура": "...текст шаблона Резидентура..."
}

# Клавиатура
template_keyboard = [[key] for key in templates]

# Обработчик выбора (пример)
async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text

    if choice in templates:
        await update.message.reply_text(templates[choice])
    elif choice in programs:
        await update.message.reply_text(programs[choice])
    else:
        await update.message.reply_text("Неизвестный выбор.")
program_keyboard = [[key] for key in programs]

# --- Лицензии (осталась старая логика) ---
SPECIALITIES_GP = [
    "Терапевт", "Кардиология", "Реаниматология", "Скорая медицинская помощь",
    "Семейная медицина", "Педиатрия", "Общая хирургия", "Акушерство и гинекология"
]
POSTGRADUATE_OPTIONS = [
    "Интернатура",
    "Ординатура 2 года",
    "Ординатура 3+ лет или резидентура 3+ лет",
    "Аспирантура и КМН"
]
async def handle_resume_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    response = templates.get(user_input)
    if response:
        await update.message.reply_text(response, parse_mode="Markdown")
    else:
        await update.message.reply_text("Пожалуйста, выбери один из доступных шаблонов.")


async def handle_program_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    response = programs.get(user_input)
    if response:
        await update.message.reply_text(response, parse_mode="Markdown")
    else:
        await update.message.reply_text("Пожалуйста, выбери одну из доступных программ.")

program_buttons = [[key] for key in programs.keys()]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Выбери, что хочешь сделать:",
                                    reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True))
    return CHOOSING

async def main_menu_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice == "🩺 Определить лицензию":
        await update.message.reply_text("Вы врач или стоматолог?",
                                        reply_markup=ReplyKeyboardMarkup([["врач", "стоматолог"]], one_time_keyboard=True, resize_keyboard=True))
        return PROFESSION
    elif choice == "📄 Шаблоны резюме":
        await update.message.reply_text("Выбери шаблон:", reply_markup=ReplyKeyboardMarkup(template_keyboard, resize_keyboard=True))
        return SEND_TEMPLATE
    elif choice == "📘 Программа курса":
        await update.message.reply_text("Выбери курс:", reply_markup=ReplyKeyboardMarkup(program_keyboard, resize_keyboard=True))
        return SEND_PROGRAM
    else:
        await update.message.reply_text("Пожалуйста, выбери одну из опций.")
        return CHOOSING

# --- Основной диалог (лицензии) ---
async def profession(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['profession'] = update.message.text.lower()
    await update.message.reply_text("У вас есть высшее образование?",
                                    reply_markup=ReplyKeyboardMarkup([["да", "нет"]], one_time_keyboard=True, resize_keyboard=True))
    return EDUCATION

async def education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    context.user_data['education'] = text
    if text == "да":
        if context.user_data['profession'] == "врач":
            await update.message.reply_text("Ваша специальность из списка: " + ", ".join(SPECIALITIES_GP) + "?",
                                            reply_markup=ReplyKeyboardMarkup([["да", "нет"]], one_time_keyboard=True, resize_keyboard=True))
            return SPECIALITY_CHECK
        else:
            await update.message.reply_text("Сколько лет стоматологического стажа?")
            return EXPERIENCE
    else:
        await update.message.reply_text("Без высшего образования лицензия невозможна.")
        return ConversationHandler.END

async def speciality_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['speciality_match'] = (update.message.text.lower() == "да")
    await update.message.reply_text("Сколько лет у вас стажа?")
    return EXPERIENCE

async def experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['experience'] = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Введите число.")
        return EXPERIENCE

    if context.user_data['profession'] == "врач":
        await update.message.reply_text("Какое у вас постдипломное образование?",
                                        reply_markup=ReplyKeyboardMarkup([POSTGRADUATE_OPTIONS], one_time_keyboard=True, resize_keyboard=True))
        return POSTGRADUATE_EDU
    else:
        await update.message.reply_text("Есть ли у вас действующая аккредитация по стоматологии?",
                                        reply_markup=ReplyKeyboardMarkup([["да", "нет"]], one_time_keyboard=True, resize_keyboard=True))
        return ACCREDITATION

async def postgraduate_edu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['postgraduate_edu'] = update.message.text
    if update.message.text in ["Ординатура 3+ лет или резидентура 3+ лет", "Аспирантура и КМН"]:
        await update.message.reply_text("Прошло ли 3 года после окончания постдипломного образования?",
                                        reply_markup=ReplyKeyboardMarkup([["да", "нет"]], one_time_keyboard=True, resize_keyboard=True))
        return POSTGRADUATE_YEARS
    else:
        await update.message.reply_text("Есть ли у вас аккредитация?",
                                        reply_markup=ReplyKeyboardMarkup([["да", "нет"]], one_time_keyboard=True, resize_keyboard=True))
        return ACCREDITATION

async def postgraduate_years(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['postgraduate_years_passed'] = (update.message.text.lower() == "да")
    await update.message.reply_text("Есть ли у вас аккредитация?",
                                    reply_markup=ReplyKeyboardMarkup([["да", "нет"]], one_time_keyboard=True, resize_keyboard=True))
    return ACCREDITATION

async def accreditation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['accreditation'] = (update.message.text.lower() == "да")
    await update.message.reply_text("Вы из России?",
                                    reply_markup=ReplyKeyboardMarkup([["да", "нет"]], one_time_keyboard=True, resize_keyboard=True))
    return FROM_RUSSIA

async def from_russia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['from_russia'] = (update.message.text.lower() == "да")
    result = determine_license(context.user_data)
    await update.message.reply_text(result)
    return CHOOSING

def determine_license(data):
    prof = data.get('profession')
    edu = data.get('education') == "да"
    speciality_match = data.get('speciality_match', False)
    experience = data.get('experience', 0)
    postgrad = data.get('postgraduate_edu', "")
    postgrad_years_passed = data.get('postgraduate_years_passed', False)
    accreditation = data.get('accreditation', False)
    from_russia = data.get('from_russia', False)

    specialist_postgrad = postgrad in ["Ординатура 3+ лет или резидентура 3+ лет", "Аспирантура и КМН"]
    if edu and specialist_postgrad and postgrad_years_passed and accreditation and experience >= 3:
        return "✅ Вы проходите на Specialist."

    if prof == "врач" and edu:
        if speciality_match:
            if experience >= 4 and accreditation:
                return "✅ Вы проходите на GP."
            elif experience >= 2 and postgrad == "Интернатура":
                return "✅ Вы проходите на GP."
            elif from_russia:
                return "Можно оформить аккредитацию и стаж для GP."
            else:
                return "⛔️ Пока не проходите ни на одну лицензию."
        else:
            if experience >= 4 and accreditation:
                return "Возможно GP, если оформить аккредитацию по нужной специальности."
            elif from_russia:
                return "Можно оформить стаж и аккредитацию для GP."
            else:
                return "⛔️ Пока не проходите ни на одну лицензию."

    if prof == "стоматолог" and edu:
        if experience >= 4 and accreditation:
            return "✅ Вы проходите на GD."
        else:
            return "⛔️ Вы не проходите на лицензию GD."

    return "⛔️ Пока не проходите ни на одну лицензию."

# --- Шаблоны / Программы ---
async def send_template(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(templates.get(update.message.text, "⚠️ Шаблон не найден."))
    return CHOOSING

async def send_program(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(programs.get(update.message.text, "⚠️ Программа не найдена."))
    return CHOOSING

def main():
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_choice)],
            PROFESSION: [MessageHandler(filters.TEXT, profession)],
            EDUCATION: [MessageHandler(filters.TEXT, education)],
            SPECIALITY_CHECK: [MessageHandler(filters.TEXT, speciality_check)],
            EXPERIENCE: [MessageHandler(filters.TEXT, experience)],
            POSTGRADUATE_EDU: [MessageHandler(filters.TEXT, postgraduate_edu)],
            POSTGRADUATE_YEARS: [MessageHandler(filters.TEXT, postgraduate_years)],
            ACCREDITATION: [MessageHandler(filters.TEXT, accreditation)],
            FROM_RUSSIA: [MessageHandler(filters.TEXT, from_russia)],
            SEND_TEMPLATE: [MessageHandler(filters.TEXT, send_template)],
            SEND_PROGRAM: [MessageHandler(filters.TEXT, send_program)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
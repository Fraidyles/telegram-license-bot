import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, ContextTypes, filters

(
    MAIN_MENU,
    PROFESSION,
    EDUCATION,
    SPECIALITY_CHECK,
    EXPERIENCE,
    POSTGRADUATE_EDU,
    POSTGRADUATE_YEARS,
    ACCREDITATION,
    FROM_RUSSIA,
    RESUME_TEMPLATE_CHOICE,
    COURSE_PROGRAM_CHOICE,
) = range(11)

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

RESUME_TEMPLATES = {
    "GP": "Обучение проходит на платформе геткурс, где будет доступ к материалам и записям лекций...\n(далее текст шаблона GP)",
    "BT": "В начале идет подготовка к сдаче экзамена, называется Prometric Exam...\n(далее текст шаблона BT)",
    "GD Полина Ганжара": "Программа: 20 занятий по 2 часа, теория на русском, практика на английском...\n(далее текст GD Полина)",
    "GD Ксения Исламова": "54 мини-урока по 30 минут — максимум пользы при минимуме времени...\n(далее текст GD Ксения)",
    "Specialist Гинеколог": "Добрый день! Отправляю вам подробности по интенсивному курсу по акушерству и гинекологии...\n(далее текст Specialist Гинеколог)",
    "Резидентура": "Пакет 'Поступление в резидентуру' включает...\n(далее текст резидентура)",
}

COURSE_PROGRAMS = {
    "GP": "Разбор основных дисциплин: Кардиология, Пульмонология, Хирургия, Маммология...",
    "BT": "Ссылка на программу - https://clck.ru/3FAPvx",
    "GD Полина Ганжара": "Патология полости рта: норма, травма, наследственная патология слизистой...",
    "Specialist Гинеколог": "Занятие 1: Анатомия, физиология и фармакология в акушерстве...",
    "Spec Дерматолог": "Basic dermatology, Histology, Drugs overview, Acne vulgaris, rosacea...",
    "Spec Кардиолог": "Hypertension. Main steps of treatment. Structure of the heart...",
    "Spec Семейная Медицина": "Занятие 1: Артериальная гипертензия, ИБС, СН, ЭКГ...",
    "Spec Внутренняя Медицина": "Занятие 1: ИБС, инфаркт, гипертензия, ЭКГ, кардиомиопатии...",
    "Spec Педиатр": "Milestone+vaccination, Neonatology, Syndroms, Nephrology, Cardio...",
    "Хирург": "Острый живот, пищевод, желудок, кишечник, печень, поджелудочная...",
    "Эндокринолог": "Диабет, ожирение, тиреоидиты, гипофиз, надпочечники, витамин D...",
    "Spec Отолоринголог": "Отоневрология, аудиология, ринология, экстренные состояния...",
    "Spec Травматолог": "Ортопедия, травмы, артрозы, спортивные травмы, опухоли, финальный тест...",
    "Spec Уролог": "Хирургия, инфекции, МКБ, ПН, опухоли, педиатрическая урология...",
    "Spec Пластический хирург": "Wound repair, Anesthesia, Burns, Head and Neck, Breast, Safety...",
    "Spec Сосудистый хирург": "Vasculitis, thrombosis, anatomy, ischemia, diabetes, endovascular...",
    "Spec Невролог": "Инсульт, эпилепсия, когнитивные, иммунные, мышечные, финальный обзор...",
    "Spec Анестезиолог": "Airway, Neuro/Cardiac anesthesia, Pediatrics, Ethics, Pain, NORA...",
}

# Главное меню
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Узнать лицензию"], ["Шаблоны резюмирования"], ["Программа курса"]]
    await update.message.reply_text(
        "Выберите, что вы хотите сделать:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return MAIN_MENU

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice == "Узнать лицензию":
        keyboard = [["врач", "стоматолог"]]
        await update.message.reply_text(
            "Здравствуйте! Вы являетесь врачом или стоматологом?",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return PROFESSION
    elif choice == "Шаблоны резюмирования":
        keyboard = [[key] for key in RESUME_TEMPLATES.keys()]
        await update.message.reply_text(
            "Выберите шаблон резюмирования:",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return RESUME_TEMPLATE_CHOICE
    elif choice == "Программа курса":
        keyboard = [[key] for key in COURSE_PROGRAMS.keys()]
        await update.message.reply_text(
            "Выберите курс, для которого хотите получить программу:",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return COURSE_PROGRAM_CHOICE
    else:
        await update.message.reply_text("Пожалуйста, выберите один из предложенных вариантов.")
        return MAIN_MENU

async def resume_template_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = update.message.text
    template = RESUME_TEMPLATES.get(key)
    if template:
        await update.message.reply_text(template)
    else:
        await update.message.reply_text("Шаблон не найден.")
    return ConversationHandler.END

async def course_program_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = update.message.text
    program = COURSE_PROGRAMS.get(key)
    if program:
        await update.message.reply_text(program)
    else:
        await update.message.reply_text("Программа не найдена.")
    return ConversationHandler.END

# 👇 (оставляем остальную часть: profession → from_russia — без изменений)
# — [ТВОЙ КОД ЛИЦЕНЗИРОВАНИЯ от PROFESSION до determine_license() — сюда вставь как есть] —
# — [не забудь вернуть все функции: cancel, determine_license и т.д.] —

# Запуск
def main():
    import asyncio
    from telegram.ext import Application

    TOKEN = os.getenv("TOKEN")
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            RESUME_TEMPLATE_CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, resume_template_choice)],
            COURSE_PROGRAM_CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, course_program_choice)],

            # 👇 ниже — блок лицензирования, не трогаем
            PROFESSION: [MessageHandler(filters.Regex("^(врач|стоматолог)$"), profession)],
            EDUCATION: [MessageHandler(filters.Regex("^(да|нет)$"), education)],
            SPECIALITY_CHECK: [MessageHandler(filters.Regex("^(да|нет)$"), speciality_check)],
            EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, experience)],
            POSTGRADUATE_EDU: [MessageHandler(filters.Regex("^(" + "|".join(POSTGRADUATE_OPTIONS) + ")$"), postgraduate_edu)],
            POSTGRADUATE_YEARS: [MessageHandler(filters.Regex("^(да|нет)$"), postgraduate_years)],
            ACCREDITATION: [MessageHandler(filters.Regex("^(да|нет)$"), accreditation)],
            FROM_RUSSIA: [MessageHandler(filters.Regex("^(да|нет)$"), from_russia)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
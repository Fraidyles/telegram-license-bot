import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

# Состояния диалога
(
    PROFESSION,
    EDUCATION,
    SPECIALITY_CHECK,
    EXPERIENCE,
    POSTGRADUATE_EDU,
    POSTGRADUATE_YEARS,
    ACCREDITATION,
    FROM_RUSSIA,
) = range(8)

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["врач", "стоматолог"]]
    await update.message.reply_text(
        "Здравствуйте! Вы являетесь врачом или стоматологом?",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return PROFESSION

async def profession(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['profession'] = update.message.text.lower()
    keyboard = [["да", "нет"]]
    await update.message.reply_text(
        "У вас есть высшее образование?",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return EDUCATION

async def education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    context.user_data['education'] = text
    if text == "да":
        if context.user_data['profession'] == "врач":
            keyboard = [["да", "нет"]]
            await update.message.reply_text(
                "Ваша специальность одна из: " + ", ".join(SPECIALITIES_GP) + "?",
                reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            )
            return SPECIALITY_CHECK
        else:
            # Для стоматолога сразу спрашиваем опыт
            await update.message.reply_text("Сколько лет у вас стоматологического стажа?")
            return EXPERIENCE
    else:
        await update.message.reply_text("К сожалению, без высшего образования лицензия невозможна.")
        return ConversationHandler.END

async def speciality_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    context.user_data['speciality_match'] = (text == "да")
    await update.message.reply_text("Сколько лет у вас стажа по специальности?")
    return EXPERIENCE

async def experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        exp = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число.")
        return EXPERIENCE
    context.user_data['experience'] = exp

    if context.user_data['profession'] == "врач":
        keyboard = [POSTGRADUATE_OPTIONS]
        await update.message.reply_text(
            "Какое у вас постдипломное образование? Выберите вариант:",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return POSTGRADUATE_EDU
    else:
        # Для стоматолога
        keyboard = [["да", "нет"]]
        await update.message.reply_text(
            "Есть ли у вас действующая аккредитация по стоматологии?",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return ACCREDITATION

async def postgraduate_edu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data['postgraduate_edu'] = text

    if text == "Ординатура 3+ лет или резидентура 3+ лет" or text == "Аспирантура и КМН":
        keyboard = [["да", "нет"]]
        await update.message.reply_text(
            "После окончания вашего постдипломного прошло 3 года?",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return POSTGRADUATE_YEARS
    else:
        # Если нет 3+ лет ординатуры/резидентуры/аспира, то сразу спрашиваем аккредитацию
        keyboard = [["да", "нет"]]
        await update.message.reply_text(
            "Есть ли у вас действующая аккредитация по вашей специальности?",
            reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        )
        return ACCREDITATION

async def postgraduate_years(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    context.user_data['postgraduate_years_passed'] = (text == "да")
    keyboard = [["да", "нет"]]
    await update.message.reply_text(
        "Есть ли у вас действующая аккредитация по вашей специальности?",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return ACCREDITATION

async def accreditation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    context.user_data['accreditation'] = (text == "да")

    keyboard = [["да", "нет"]]
    await update.message.reply_text(
        "Вы из России?",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return FROM_RUSSIA

async def from_russia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    context.user_data['from_russia'] = (text == "да")

    # Логика определения лицензии
    res = determine_license(context.user_data)
    await update.message.reply_text(res)
    return ConversationHandler.END

def determine_license(data):
    prof = data.get('profession')
    edu = data.get('education') == "да"
    speciality_match = data.get('speciality_match', False)
    experience = data.get('experience', 0)
    postgrad = data.get('postgraduate_edu', "")
    postgrad_years_passed = data.get('postgraduate_years_passed', False)
    accreditation = data.get('accreditation', False)
    from_russia = data.get('from_russia', False)

    # Проверяем Specialist
    specialist_postgrad = postgrad in ["Ординатура 3+ лет или резидентура 3+ лет", "Аспирантура и КМН"]
    if edu and specialist_postgrad and postgrad_years_passed and accreditation and experience >= 3:
        return "Вы проходите на Specialist."

    # Проверка GP
    gp_specialities = SPECIALITIES_GP
    if prof == "врач" and edu:
        if speciality_match:
            if experience >= 4 and accreditation:
                return "Вы проходите на лицензию GP."
            elif experience >= 2 and postgrad == "Интернатура":
                return "Вы проходите на лицензию GP."
            elif from_russia:
                return "Вы из России — можем сделать аккредитацию и стаж для GP."
            else:
                return "К сожалению, вы пока не проходите ни на одну лицензию."
        else:
            # Если специальность не из списка, но по остальным параметрам подходит GP
            if experience >= 4 and accreditation:
                return "Клиент в теории проходит на GP, но нужно сделать стаж и аккредитацию по одной из подходящих специальностей."
            elif from_russia:
                return "Вы из России — можем сделать аккредитацию и стаж для GP."
            else:
                return "К сожалению, вы пока не проходите ни на одну лицензию."

    # Проверка GD
    if prof == "стоматолог" and edu:
        if experience >= 4 and accreditation:
            return "Вы проходите на лицензию GD."
        else:
            return "К сожалению, вы не проходите на лицензию GD."

    return "К сожалению, вы пока не проходите ни на одну лицензию."

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Диалог прерван. Если хотите начать заново, напишите /start.")
    return ConversationHandler.END


def main():
    import asyncio
    from telegram.ext import Application, ConversationHandler, CommandHandler, MessageHandler, filters

    TOKEN = os.getenv("TOKEN")
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
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
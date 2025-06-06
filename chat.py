import json
import os
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ConversationHandler, ContextTypes, filters
)

def with_main_menu_button(keyboard: list[list[str]]) -> list[list[str]]:
    return keyboard + [["⬅️ Главное меню"]]

# Загрузка шаблонов резюме
with open("templates.json", "r", encoding="utf-8") as f:
    templates = json.load(f)

# Загрузка программ курсов
with open("programs.json", "r", encoding="utf-8") as f:
    programs = json.load(f)

# Загрузка цен
with open("full_prices_complete.json", "r", encoding="utf-8") as f:
    full_prices = json.load(f)

# Логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Состояния
(
    CHOOSING, PROFESSION, EDUCATION, SPECIALITY_CHECK, EXPERIENCE,
    POSTGRADUATE_EDU, POSTGRADUATE_YEARS, ACCREDITATION, FROM_RUSSIA,
    SEND_TEMPLATE, SEND_PROGRAM, NURSE_EDU_DURATION, NURSE_LICENSE,
    PRICE_CATEGORY, PRICE_OPTION
) = range(15)

# Кнопки
main_keyboard = [["🩺 Определить лицензию"], ["📄 Шаблоны резюме"], ["📘 Программа курса"], ["💰 Цены"]]
template_keyboard = [[key] for key in templates]
program_keyboard = [[key] for key in programs]

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
    await update.message.reply_text("Привет! Выбери, что хочешь сделать:",
                                    reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True))
    return CHOOSING

async def main_menu_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice == "⬅️ Главное меню":
        return await start(update, context)

    if choice == "🩺 Определить лицензию":
        await update.message.reply_text("Кто вы по профессии?",
            reply_markup=ReplyKeyboardMarkup(with_main_menu_button([["врач", "стоматолог", "медсестра/фельдшер"]]),
            one_time_keyboard=True, resize_keyboard=True))
        return PROFESSION
    elif choice == "📄 Шаблоны резюме":
        await update.message.reply_text("Выбери шаблон:",
            reply_markup=ReplyKeyboardMarkup(with_main_menu_button(template_keyboard), resize_keyboard=True))
        return SEND_TEMPLATE
    elif choice == "📘 Программа курса":
        await update.message.reply_text("Выбери курс:",
            reply_markup=ReplyKeyboardMarkup(with_main_menu_button(program_keyboard), resize_keyboard=True))
        return SEND_PROGRAM
    elif choice == "💰 Цены":
        categories = list(full_prices.keys())
        category_keyboard = [[c] for c in categories]
        await update.message.reply_text("Выбери категорию:",
            reply_markup=ReplyKeyboardMarkup(with_main_menu_button(category_keyboard), resize_keyboard=True))
        return PRICE_CATEGORY
    else:
        await update.message.reply_text("Пожалуйста, выбери одну из опций.")
        return CHOOSING
async def profession(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "⬅️ Главное меню":
        return await start(update, context)

    profession_choice = update.message.text.lower()
    context.user_data['profession'] = profession_choice

    if profession_choice == "медсестра/фельдшер":
        await update.message.reply_text("Ваше среднее медицинское образование длилось 3 года и дольше?",
            reply_markup=ReplyKeyboardMarkup(with_main_menu_button([["да", "нет"]]),
            one_time_keyboard=True, resize_keyboard=True))
        return NURSE_EDU_DURATION

    await update.message.reply_text("У вас есть высшее образование?",
        reply_markup=ReplyKeyboardMarkup(with_main_menu_button([["да", "нет"]]),
        one_time_keyboard=True, resize_keyboard=True))
    return EDUCATION

async def nurse_edu_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "⬅️ Главное меню":
        return await start(update, context)

    if update.message.text.lower() == "да":
        context.user_data['nurse_edu'] = True
        await update.message.reply_text("У вас есть действующая лицензия медсестры/фельдшера?",
            reply_markup=ReplyKeyboardMarkup(with_main_menu_button([["да", "нет"]]),
            one_time_keyboard=True, resize_keyboard=True))
        return NURSE_LICENSE
    else:
        await update.message.reply_text("⛔️ Вы можете попробовать податься на Beauty Therapist")
        return CHOOSING

async def nurse_license(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "⬅️ Главное меню":
        return await start(update, context)

    has_license = update.message.text.lower() == "да"
    if has_license and context.user_data.get('nurse_edu', False):
        message = "✅ Вы проходите на лицензию Registered Nurse."
    else:
        message = "⛔️ Вы можете попробовать податься на Beauty Therapist."

    await update.message.reply_text(
        message + "\n\n⬅️ Вернуться в главное меню:",
        reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
    )
    return CHOOSING

async def education(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "⬅️ Главное меню":
        return await start(update, context)

    text = update.message.text.lower()
    context.user_data['education'] = text
    if text == "да":
        if context.user_data['profession'] == "врач":
            await update.message.reply_text(
                "Ваша специальность из списка: " + ", ".join(SPECIALITIES_GP) + "?",
                reply_markup=ReplyKeyboardMarkup(with_main_menu_button([["да", "нет"]]),
                                                 one_time_keyboard=True, resize_keyboard=True)
            )
            return SPECIALITY_CHECK
        elif context.user_data['profession'] == "стоматолог":
            await update.message.reply_text("Сколько лет у вас стоматологического стажа?",
                                            reply_markup=ReplyKeyboardMarkup(with_main_menu_button([]),
                                                                             one_time_keyboard=True, resize_keyboard=True))
            return EXPERIENCE
    else:
        await update.message.reply_text("Без высшего образования вы можете претендовать только на лицензию BT или рассмотреть Anti-Age ")
        return ConversationHandler.END

async def speciality_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "⬅️ Главное меню":
        return await start(update, context)

    context.user_data['speciality_match'] = (update.message.text.lower() == "да")
    await update.message.reply_text("Сколько лет у вас стажа?")
    return EXPERIENCE

async def experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "⬅️ Главное меню":
        return await start(update, context)

    try:
        context.user_data['experience'] = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Введите число.")
        return EXPERIENCE

    await update.message.reply_text("Какое у вас постдипломное образование?",
                                    reply_markup=ReplyKeyboardMarkup(with_main_menu_button([POSTGRADUATE_OPTIONS]),
                                                                     one_time_keyboard=True, resize_keyboard=True))
    return POSTGRADUATE_EDU

async def postgraduate_edu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "⬅️ Главное меню":
        return await start(update, context)

    context.user_data['postgraduate_edu'] = update.message.text
    if update.message.text in ["Ординатура 3+ лет или резидентура 3+ лет", "Аспирантура и КМН"]:
        await update.message.reply_text("Прошло ли 3 года после окончания постдипломного образования?",
                                        reply_markup=ReplyKeyboardMarkup(with_main_menu_button([["да", "нет"]]),
                                                                         one_time_keyboard=True, resize_keyboard=True))
        return POSTGRADUATE_YEARS
    else:
        await update.message.reply_text("Есть ли у вас аккредитация?",
                                        reply_markup=ReplyKeyboardMarkup(with_main_menu_button([["да", "нет"]]),
                                                                         one_time_keyboard=True, resize_keyboard=True))
        return ACCREDITATION

async def postgraduate_years(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "⬅️ Главное меню":
        return await start(update, context)

    context.user_data['postgraduate_years_passed'] = (update.message.text.lower() == "да")
    await update.message.reply_text("Есть ли у вас аккредитация?",
                                    reply_markup=ReplyKeyboardMarkup(with_main_menu_button([["да", "нет"]]),
                                                                     one_time_keyboard=True, resize_keyboard=True))
    return ACCREDITATION

async def accreditation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "⬅️ Главное меню":
        return await start(update, context)

    context.user_data['accreditation'] = (update.message.text.lower() == "да")
    await update.message.reply_text("Вы из России?",
                                    reply_markup=ReplyKeyboardMarkup(with_main_menu_button([["да", "нет"]]),
                                                                     one_time_keyboard=True, resize_keyboard=True))
    return FROM_RUSSIA

async def from_russia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "⬅️ Главное меню":
        return await start(update, context)

    context.user_data['from_russia'] = (update.message.text.lower() == "да")
    result = determine_license(context.user_data)
    await update.message.reply_text(
        result + "\n\n⬅️ Вернуться в главное меню:",
        reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
    )
    return CHOOSING

async def send_template(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "⬅️ Главное меню":
        return await start(update, context)

    await update.message.reply_text(
        templates.get(update.message.text, "⚠️ Шаблон не найден.") + "\n\n⬅️ Вернуться в главное меню:",
        reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
    )
    return CHOOSING

async def send_program(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "⬅️ Главное меню":
        return await start(update, context)

    await update.message.reply_text(
        programs.get(update.message.text, "⚠️ Программа не найдена.") + "\n\n⬅️ Вернуться в главное меню:",
        reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
    )
    return CHOOSING
async def choose_price_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "⬅️ Главное меню":
        return await start(update, context)

    category = update.message.text
    context.user_data['price_category'] = category

    if category not in full_prices:
        await update.message.reply_text("⚠️ Такой категории нет.")
        return CHOOSING

    options = list(full_prices[category].keys())
    option_buttons = [[o] for o in options]
    await update.message.reply_text(
        f"Выберите вариант для {category}:",
        reply_markup=ReplyKeyboardMarkup(with_main_menu_button(option_buttons), resize_keyboard=True)
    )
    return PRICE_OPTION

async def choose_price_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "⬅️ Главное меню":
        return await start(update, context)

    option = update.message.text
    category = context.user_data.get('price_category')

    if not category or category not in full_prices:
        await update.message.reply_text("⚠️ Ошибка категории.")
        return CHOOSING

    if option not in full_prices[category]:
        await update.message.reply_text("⚠️ Такой опции нет.")
        return CHOOSING

    price_value = full_prices[category][option]
    await update.message.reply_text(
        f"{category} — {option}:\n💰 {price_value}\n\n⬅️ Вернуться в главное меню:",
        reply_markup=ReplyKeyboardMarkup(main_keyboard, resize_keyboard=True)
    )
    return CHOOSING

# ----------- Логика лицензии -----------

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

    if prof == "стоматолог" and edu:
        if specialist_postgrad and postgrad_years_passed and accreditation and experience >= 3:
            return "✅ Вы проходите на лицензию GD Specialist."
        elif experience >= 4 and accreditation:
            return "✅ Вы проходите на лицензию GD, только если ваша специальность не ЧЛХ."
        else:
            return "⛔️ Вы не проходите на лицензию GD."

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
                return "⛔️Без лицензии вы можете претендовать только на лицензию BT или рассмотреть Anti-Age."
        else:
            if experience >= 4 and accreditation:
                return "Возможно GP, если оформить стаж и аккредитацию по нужной специальности."
            elif from_russia:
                return "Можно оформить стаж и аккредитацию для GP."
            else:
                return "⛔️Без лицензии вы можете претендовать только на лицензию BT или рассмотреть Anti-Age"

    return "⛔️Без лицензии вы можете претендовать только на лицензию BT или рассмотреть Anti-Age."

# ----------- Главная функция -----------

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
            NURSE_EDU_DURATION: [MessageHandler(filters.TEXT, nurse_edu_duration)],
            NURSE_LICENSE: [MessageHandler(filters.TEXT, nurse_license)],
            PRICE_CATEGORY: [MessageHandler(filters.TEXT, choose_price_category)],
            PRICE_OPTION: [MessageHandler(filters.TEXT, choose_price_option)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
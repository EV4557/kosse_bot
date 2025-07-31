from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, ConversationHandler
)

CHOOSE_ACTION, CHOOSE_EVENT, ASK_QUESTION, DETAIL_QUESTION = range(4)

event_details = {
    "НЕБОСВОД": {
        "ссылка": "https://qtickets.ru/event/177134",
        "цена": "🎟️ White DC — 1000₽\n💎 VIP — 1500₽\n🎩 Классика без DC — 2000₽",
        "время": "🕖 2 августа\nНачало в 19:00, окончание в 05:00",
        "место": "📍 Правая набережная, 9, «Браво Италия»"
    },
    "AYAWASKA PARTY": {
        "ссылка": "https://qtickets.ru/event/179188",
        "цена": "🎟️ Летний стиль, яркий лук, купальники — 1000₽ на старте\n🎩 Классика — 1500₽",
        "время": "🕖 16 августа\nНачало в 19:00, окончание в 05:00",
        "место": "📍 Клуб “W DoubleU”, проспект Мира 31"
    }
}

organizer_contact = "@elenaelectrodvor"

main_menu = ReplyKeyboardMarkup([
    ["Купить билет", "Контакты"],
    ["Ближайшие мероприятия", "Немного о нас"],
    ["Дресс-код и правила посещения", "Задать вопрос"]
], resize_keyboard=True)

# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот Electrodvor 🎟️\nВыберите, что вас интересует:",
        reply_markup=main_menu
    )
    return CHOOSE_ACTION

# Главное меню
async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Купить билет":
        keyboard = [[name] for name in event_details]
        keyboard.append(["⬅ Назад"])
        await update.message.reply_text(
            "Выберите мероприятие:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return CHOOSE_EVENT

    elif text == "Контакты":
        await update.message.reply_text(
            f"📞 Свяжитесь с организатором:\n{organizer_contact}",
            reply_markup=main_menu
        )
        return CHOOSE_ACTION

        elif text == "Ближайшие мероприятия":
        for name, details in event_details.items():
            caption = (
                f"🎉 *{name}*\n"
                f"{details['время']}\n"
                f"{details['место']}\n\n"
                f"{details['цена']}\n\n"
                f"[Купить билет]({details['ссылка']})"
            )

            # Добавляем изображение для каждого мероприятия, если есть
            if name == "НЕБОСВОД":
                photo_url = "https://raw.githubusercontent.com/EV4557/electrodvor-bot/main/logo.PNG"
            elif name == "AYAWASKA PARTY":
                photo_url = "https://raw.githubusercontent.com/EV4557/electrodvor-bot/main/ayawaska_party.png"
            else:
                photo_url = None

            if photo_url:
                await update.message.reply_photo(photo=photo_url, caption=caption, parse_mode="Markdown", reply_markup=main_menu)
            else:
                await update.message.reply_text(caption, parse_mode="Markdown", reply_markup=main_menu)

        return CHOOSE_ACTION

    elif text == "Немного о нас":
        photo_url = "https://raw.githubusercontent.com/EV4557/electrodvor-bot/main/logo.PNG"
        short_caption = "Проект ELECTRODVOR 👇"

        description = (
            "ELECTRODVOR — на данный момент самое свежее веяние музыкальной и развлекательной индустрии города. "
            "Абсолютно новый арт-проект, создающий уникальные ивенты в Калининграде.\n\n"
            "Команда, запустившая ELECTRODVOR, имеет опыт проведения более 400+ ивентов, большинство из которых являются "
            "самыми крупными и популярными в городе.\n\n"
            "Общая аудитория в интернете перевалила за 15 000.\n\n"
            "Проект управлял такими глобальными объектами, как бастион Астрономический — 2 года, провёл там 13 концептуальных "
            "опен-эйров и под сотню других ивентов.\n\n"
            "Такие события, как Хеллоуин, День города, Небосвод, Астероид, FULL MOON PARTY, ЗАБРОШКА, НИКОТИН, LAGUNA BEACH — "
            "одни из самых крупных и уникальных в стране.\n\n"
            "ELECTRODVOR — творческая, движущая сила города, что подтверждается самой высокой посещаемостью в области.\n\n"
            "Основатель и продюсер проекта — Евгений Зязев, творческие псевдонимы — Хром Бом, Джонни Легенда, имеет десятки кейсов "
            "по созданию и успешному запуску концертных площадок и баров. Фирменный почерк в брендинге и организации мероприятий "
            "любого уровня и характера. Багаж международных и федеральных проектов.\n\n"
            "Сейчас проект полностью перешёл в формат развития электронной сцены Калининграда. "
            "Проект насчитывает более 50 специалистов и сотрудников. Команда занимается полным циклом создания мероприятий: "
            "от барного/ресторанного менеджмента до музыкального продакшна, SMM, промо, съёмки, упаковки под ключ любой задачи.\n\n"
            "С любовью,\nELECTRODVOR"
        )

        await update.message.reply_photo(photo=photo_url, caption=short_caption, reply_markup=main_menu)
        await update.message.reply_text(description, reply_markup=main_menu)
        return CHOOSE_ACTION

    elif text == "Дресс-код и правила посещения":
        rules = (
            "🎟️ *Дресс-код и правила посещения:*\n\n"
            "1️⃣ Вход строго по билетам.\n"
            "2️⃣ Посетители обязаны иметь при себе документ, удостоверяющий личность.\n"
            "3️⃣ Мы оставляем за собой право отказать в посещении мероприятия без объяснения причин и без возврата стоимости билета.\n"
            "4️⃣ На мероприятие не допускаются лица в грязной, неопрятной, спортивной или неподобающей обстановке одежде.\n"
            "5️⃣ Организаторы не несут ответственности за потерю личных вещей.\n"
            "6️⃣ Запрещены: агрессия, наркотики, оружие.\n"
            "7️⃣ Нарушители порядка могут быть удалены с мероприятия без компенсации.\n\n"
            "🙏 Благодарим за понимание!"
        )
        await update.message.reply_text(rules, parse_mode="Markdown", reply_markup=main_menu)
        return CHOOSE_ACTION

    elif text == "Задать вопрос":
        keyboard = [
            ["Цена", "Время", "Место", "Оформить возврат билета"],
            ["⬅ Назад"]
        ]
        await update.message.reply_text(
            "❓ Часто задаваемые вопросы:\n"
            "• Цена — узнать стоимость билетов\n"
            "• Время — когда начало и конец\n"
            "• Место — где проходит мероприятие\n"
            "• Оформить возврат билета\n\n"
            "Выберите пункт или задайте свой вопрос:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return ASK_QUESTION

    else:
        await update.message.reply_text(
            "Пожалуйста, выберите вариант из меню.",
            reply_markup=main_menu
        )
        return CHOOSE_ACTION

    question = text.lower()
    PRICE_KEYWORDS = ["цена", "цен", "стоимость", "сколько стоит"]
    TIME_KEYWORDS = ["время", "времен", "когда", "во сколько"]
    PLACE_KEYWORDS = ["место", "мест", "где"]

    if any(word in question for word in PRICE_KEYWORDS):
        context.user_data["question_type"] = "цена"
    elif any(word in question for word in TIME_KEYWORDS):
        context.user_data["question_type"] = "время"
    elif any(word in question for word in PLACE_KEYWORDS):
        context.user_data["question_type"] = "место"
    else:
        context.user_data["fail_count"] = context.user_data.get("fail_count", 0) + 1
        if context.user_data["fail_count"] >= 2:
            await update.message.reply_text(
                f"Похоже, я не могу ответить на ваш вопрос 😔\nСвяжитесь с организатором: {organizer_contact}",
                reply_markup=main_menu
            )
            return CHOOSE_ACTION
        else:
            await update.message.reply_text("Я не понял вопрос. Попробуйте переформулировать.")
            return ASK_QUESTION

    keyboard = [[name] for name in event_details]
    keyboard.append(["⬅ Назад"])
    await update.message.reply_text(
        "О каком мероприятии идёт речь?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return DETAIL_QUESTION

# Уточнение вопроса
async def handle_detail_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "⬅ Назад":
        return await handle_question(update, context)

    question_type = context.user_data.get("question_type")

    if text not in event_details or question_type not in event_details[text]:
        await update.message.reply_text("Что-то пошло не так. Попробуйте снова.", reply_markup=main_menu)
        return CHOOSE_ACTION

    answer = event_details[text][question_type]
    await update.message.reply_text(answer, reply_markup=main_menu)
    return CHOOSE_ACTION

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Возвращаюсь в главное меню.", reply_markup=main_menu)
    return CHOOSE_ACTION

# Основной запуск
def main():
    import os
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_TOKEN")).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_action)],
            CHOOSE_EVENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_event_choice)],
            ASK_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question)],
            DETAIL_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_detail_question)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__":
    main()
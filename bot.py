import os
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

# Обработка выбора мероприятия при покупке билета
async def handle_event_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "⬅ Назад":
        await update.message.reply_text("Возвращаюсь в главное меню.", reply_markup=main_menu)
        return CHOOSE_ACTION
    if text in event_details:
        link = event_details[text]["ссылка"]
        await update.message.reply_text(
            f"Ссылка на покупку билета для {text}:\n{link}",
            reply_markup=main_menu
        )
        return CHOOSE_ACTION
    else:
        await update.message.reply_text(
            "Пожалуйста, выберите мероприятие из списка или вернитесь назад.",
            reply_markup=ReplyKeyboardMarkup([[name] for name in event_details] + [["⬅ Назад"]], resize_keyboard=True)
        )
        return CHOOSE_EVENT

# Обработка вопросов
async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "⬅ Назад":
        await update.message.reply_text("Вы вернулись в главное меню.", reply_markup=main_menu)
        return CHOOSE_ACTION

    if "возврат" in text.lower():
        await update.message.reply_text(
            f"🧾 Для оформления возврата билета напишите на {organizer_contact} и укажите следующую информацию:\n\n"
            "1️⃣ Номер заказа\n"
            "2️⃣ Название мероприятия\n"
            "3️⃣ Какие билеты вы хотите вернуть\n"
            "4️⃣ Почта, на которую был оформлен заказ\n"
            "5️⃣ Скриншот оплаты\n"
            "6️⃣ Причина возврата\n\n"
            "📌 Условия возврата:\n"
            "• Более 10 дней — удержание 0%\n"
            "• От 5 до 10 дней — удержание 50%\n"
            "• От 3 до 5 дней — удержание 70%\n"
            "• Менее 3 дней — возврат невозможен",
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

    question_type = context.user_data.get("question_type")

    if text not in event_details or not question_type or question_type not in event_details[text]:
        await update.message.reply_text("Что-то пошло не так. Попробуйте снова.", reply_markup=main_menu)
        return CHOOSE_ACTION

    answer = event_details[text][question_type]
    await update.message.reply_text(answer, reply_markup=main_menu)
    return CHOOSE_ACTION

# Главное меню
async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Купить билет":
        keyboard = [[name] for name in event_details]
        keyboard.append(["⬅ Назад"])
        await update.message.reply_text("Выберите мероприятие:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return CHOOSE_EVENT

    elif text == "Контакты":
        await update.message.reply_text(f"📞 Свяжитесь с организатором:\n{organizer_contact}", reply_markup=main_menu)
        return CHOOSE_ACTION

    elif text == "Ближайшие мероприятия":
        info = "\n".join(
            f"🎉 {name}\n{event_details[name]['время']}\n{event_details[name]['место']}\n"
            f"Билеты: {event_details[name]['ссылка']}\n"
            for name in event_details
        )
        await update.message.reply_text(f"📅 Ближайшие мероприятия:\n\n{info}", reply_markup=main_menu)
        return CHOOSE_ACTION

    elif text == "Немного о нас":
        photo_url = "https://raw.githubusercontent.com/EV4557/electrodvor-bot/main/logo.PNG"
        short_caption = "Проект ELECTRODVOR 👇"
        description = (
            "ELECTRODVOR — на данный момент самое свежее веяние музыкальной и развлекательной индустрии города. "
            "Абсолютно новый арт-проект, создающий уникальные ивенты в Калининграде.\n\n"
            "... (оставьте полный текст как у вас было) ..."
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
        context.user_data["fail_count"] = 0
        return ASK_QUESTION

    else:
        await update.message.reply_text("Пожалуйста, выберите вариант из меню.", reply_markup=main_menu)
        return CHOOSE_ACTION

# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Возвращаюсь в главное меню.", reply_markup=main_menu)
    return CHOOSE_ACTION

# Запуск
def main():
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
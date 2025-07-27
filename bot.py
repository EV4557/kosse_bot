from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, ConversationHandler
)

CHOOSE_ACTION, CHOOSE_EVENT, ASK_QUESTION, DETAIL_QUESTION = range(4)

event_details = {
    "НЕБОСВОД": {
        "ссылка": "https://qtickets.ru/event/177134",
        "цена": "White DC: 1000₽\nVIP: 1500₽\nКлассика без DC: 2000₽",
        "время": "2 августа\nНачало в 19:00\nКонец в 05:00",
        "место": "Место проведения: Правая набережная 9, «Браво Италия»"
    }
}

organizer_contact = "@elenaelectrodvor"

main_menu = ReplyKeyboardMarkup([
    ["Купить билет", "Контакты"],
    ["Задать вопрос", "Ближайшие мероприятия"],
    ["Дресс-код и правила", "Немного о нас"]
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
            f"Свяжитесь с организатором здесь:\n{organizer_contact}",
            reply_markup=main_menu
        )
        return CHOOSE_ACTION

    elif text == "Задать вопрос":
        keyboard = [
            ["Цена", "Время", "Место", "Оформить возврат билета"],
            ["⬅ Назад"]
        ]
        await update.message.reply_text(
            "Вы можете выбрать один из часто задаваемых вопросов или задать свой текстом:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return ASK_QUESTION

    elif text == "Ближайшие мероприятия":
        msg = ""
        for name, info in event_details.items():
            msg += f"🎉 {name}\n🕒 {info['время']}\n📍 {info['место']}\n💳 {info['цена']}\n🔗 {info['ссылка']}\n\n"
        await update.message.reply_text(msg.strip(), reply_markup=main_menu)
        return CHOOSE_ACTION

    elif text == "Дресс-код и правила":
        rules = (
            "👗 *Дресс-код:*\n"
            "1. Белый total look — приветствуется\n"
            "2. Без спортивной одежды\n"
            "3. Ухоженный внешний вид\n\n"
            "📌 *Правила посещения:*\n"
            "1. Возрастное ограничение 18+\n"
            "2. Организаторы имеют право отказать во входе без объяснения причин\n"
            "3. Билеты не подлежат возврату менее чем за 3 дня до мероприятия"
        )
        await update.message.reply_text(rules, parse_mode="Markdown", reply_markup=main_menu)
        return CHOOSE_ACTION

    elif text == "Немного о нас":
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://raw.githubusercontent.com/EV4557/electrodvor-bot/main/logo.PNG",
            caption=(
                "📖 *Немного о нас:*\n\n"
                "Мы — команда Electrodvor, создающая атмосферные вечеринки с уклоном в электронную музыку. "
                "Наша миссия — собирать людей, объединённых любовью к искусству, музыке и эстетике. "
                "Каждое мероприятие — это больше, чем просто событие, это — впечатление, которое остаётся с вами надолго."
            ),
            parse_mode="Markdown",
            reply_markup=main_menu
        )
        return CHOOSE_ACTION

    else:
        await update.message.reply_text(
            "Пожалуйста, выберите вариант из меню.",
            reply_markup=main_menu
        )
        return CHOOSE_ACTION


# Выбор мероприятия
async def handle_event_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "⬅ Назад":
        await update.message.reply_text("Вы вернулись в главное меню.", reply_markup=main_menu)
        return CHOOSE_ACTION

    if text in event_details:
        link = event_details[text]["ссылка"]
        await update.message.reply_text(
            f"Вот ссылка для покупки билета на '{text}':\n{link}",
            reply_markup=main_menu
        )
        return CHOOSE_ACTION
    else:
        await update.message.reply_text("Такого мероприятия нет. Выберите из списка.")
        return CHOOSE_EVENT


# Вопросы
async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "⬅ Назад":
        await update.message.reply_text("Вы вернулись в главное меню.", reply_markup=main_menu)
        return CHOOSE_ACTION

    if text == "Оформить возврат билета":
        await update.message.reply_text(
            f"🧾 Для возврата билета напишите на {organizer_contact} и укажите:\n"
            "1️⃣ Номер заказа\n2️⃣ Название мероприятия\n3️⃣ Билеты\n4️⃣ Почту\n5️⃣ Скрин оплаты\n6️⃣ Причину\n\n"
            "📌 Условия:\n– >10 дней: 100% возврат\n– 5–10 дней: 50%\n– 3–5 дней: 30%\n– <3 дней: без возврата",
            reply_markup=main_menu
        )
        return CHOOSE_ACTION

    question = text.lower()
    PRICE = ["цена", "цен", "стоимость"]
    TIME = ["время", "когда", "во сколько"]
    PLACE = ["место", "где"]

    if any(w in question for w in PRICE):
        context.user_data["question_type"] = "цена"
    elif any(w in question for w in TIME):
        context.user_data["question_type"] = "время"
    elif any(w in question for w in PLACE):
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
            await update.message.reply_text("Я не понял вопрос. Попробуйте иначе.")
            return ASK_QUESTION

    keyboard = [[name] for name in event_details]
    keyboard.append(["⬅ Назад"])
    await update.message.reply_text(
        "О каком мероприятии идёт речь?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return DETAIL_QUESTION


# Уточнение по мероприятию
async def handle_detail_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "⬅ Назад":
        await update.message.reply_text("Выберите вопрос снова:", reply_markup=main_menu)
        return ASK_QUESTION

    question_type = context.user_data.get("question_type")
    if text not in event_details or question_type not in event_details[text]:
        await update.message.reply_text("Что-то пошло не так. Попробуйте снова.", reply_markup=main_menu)
        return CHOOSE_ACTION

    await update.message.reply_text(event_details[text][question_type], reply_markup=main_menu)
    return CHOOSE_ACTION


# Отмена
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Возвращаюсь в главное меню.", reply_markup=main_menu)
    return CHOOSE_ACTION


# Запуск
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
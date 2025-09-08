import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters, ConversationHandler
)

CHOOSE_ACTION, CHOOSE_EVENT, ASK_QUESTION, DETAIL_QUESTION = range(4)

event_details = {
    "Хоровод Света": {
        "ссылка": "https://kaliningrad.qtickets.events/183804-khorovod-sveta",
        "цена": "🎟️ Дети с 4-12 — 700₽\n💎 Стандартный — 1000₽\n🎩 Все включено — 1400₽",
        "время": "🕖 13 сентября\nНачало в 13:00, окончание в 22:00",
        "место": "📍 Кемпинг Kosse.club, ул. Советская, 10, Янтарный."
    }
}

organizer_contact = "@kosse_club"

main_menu = ReplyKeyboardMarkup([
    ["Купить билет", "Контакты"],
    ["Ближайшие мероприятия", "Немного о нас"],
    ["Дресс-код и правила посещения", "Задать вопрос"]
], resize_keyboard=True)

# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот Kosse.club 🎟️\nВыберите, что вас интересует:",
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
            "• Более 5 дней — удержание 0%\n"
            "• От 4 до 5 дней — удержание 50%\n"
            "• От 3 до 4 дней — удержание 70%\n"
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
        short_caption = "Проект Kosse.club 👇"
        description = (
            "KOSSE.club - ..."
        )
        await update.message.reply_photo(photo=photo_url, caption=short_caption, reply_markup=main_menu)
        await update.message.reply_text(description, reply_markup=main_menu)
        return CHOOSE_ACTION

elif text == "Дресс-код и правила посещения":
    rules = (
        "🎟️ *Правила посещения и дресс-код:*\n\n"
        "1️⃣ Вход возможен только при наличии билета.\n"
        "2️⃣ Каждый гость должен иметь при себе документ, удостоверяющий личность.\n"
        "3️⃣ Организаторы оставляют за собой право отказать во входе без объяснения причин и без возврата средств.\n"
        "4️⃣ На мероприятие не допускаются лица в спортивной, грязной или неподобающей обстановке одежде.\n"
        "5️⃣ Ответственность за сохранность личных вещей и инвентаря турбазы несут посетители.\n"
        "6️⃣ Запрещены: агрессивное поведение, наркотические вещества, алкогольные напитки и оружие.\n"
        "7️⃣ Нарушители правил могут быть удалены без компенсации стоимости билета.\n\n"
        "🙏 Спасибо за понимание и уважение к правилам!"
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
            "• Возврат билета\n\n"
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
    app = Application.builder().token("8244050011:AAGP565NclU046a-WsP-nO8hNOcvkwQCh0U").build()

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
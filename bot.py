from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

# Состояния диалога
CHOOSE_ACTION, CHOOSE_EVENT, ASK_QUESTION, DETAIL_QUESTION = range(4)

# Информация о мероприятиях
event_details = {
    "Концерт в Парке": {
        "ссылка": "https://example.com/tickets/concert",
        "цена": "Цена на 'Концерт в Парке': 1200₽",
        "время": "Начало в 19:00",
        "место": "Парк Горького, сцена у фонтана"
    },
    "Фестиваль Света": {
        "ссылка": "https://example.com/tickets/festival",
        "цена": "Цена на 'Фестиваль Света': 2500₽",
        "время": "Начало в 20:30",
        "место": "ВДНХ, павильон №1"
    }
}

# Ссылка на контакт организатора
organizer_contact = "https://t.me/your_telegram_username"  # Замени на свою ссылку

# Главное меню
main_menu = ReplyKeyboardMarkup([
    ["Купить билет", "Контакты"],
    ["Задать вопрос"]
], resize_keyboard=True)

# Стартовая команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот Electrodvor 🎟️\nВыберите, что вас интересует:",
        reply_markup=main_menu
    )
    return CHOOSE_ACTION

# Обработка выбора действия
async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Купить билет":
        keyboard = [[name] for name in event_details]
        await update.message.reply_text("Выберите мероприятие:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return CHOOSE_EVENT

    elif text == "Контакты":
        await update.message.reply_text(f"Свяжитесь с организатором здесь:\n{organizer_contact}", reply_markup=main_menu)
        return CHOOSE_ACTION

    elif text == "Задать вопрос":
        keyboard = [["Цена", "Время", "Место"]]
        await update.message.reply_text(
            "Вы можете выбрать один из часто задаваемых вопросов или задать свой текстом:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return ASK_QUESTION

    else:
        await update.message.reply_text("Пожалуйста, выберите вариант из меню.", reply_markup=main_menu)
        return CHOOSE_ACTION

# Обработка выбора мероприятия
async def handle_event_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    event = update.message.text
    if event in event_details:
        link = event_details[event]["ссылка"]
        await update.message.reply_text(f"Вот ссылка для покупки билета на '{event}':\n{link}", reply_markup=main_menu)
        return CHOOSE_ACTION
    else:
        await update.message.reply_text("Такого мероприятия нет. Выберите из списка.")
        return CHOOSE_EVENT

# Обработка вопроса пользователя
async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text.lower()

    PRICE_KEYWORDS = ["цена", "цен"]
    TIME_KEYWORDS = ["время", "времен", "когда"]
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

    # Предложить выбор мероприятия
    keyboard = [[name] for name in event_details]
    await update.message.reply_text("О каком мероприятии идет речь?", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    return DETAIL_QUESTION

# Ответ на уточнённый вопрос
async def handle_detail_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    event = update.message.text
    question_type = context.user_data.get("question_type")

    if event not in event_details or question_type not in event_details[event]:
        await update.message.reply_text("Что-то пошло не так. Попробуйте снова.", reply_markup=main_menu)
        return CHOOSE_ACTION

    answer = event_details[event][question_type]
    await update.message.reply_text(answer, reply_markup=main_menu)
    return CHOOSE_ACTION

# Отмена диалога
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Возвращаюсь в главное меню.", reply_markup=main_menu)
    return CHOOSE_ACTION

# Запуск бота
def main():
    app = ApplicationBuilder().token("8082063845:AAEXePqi4ixBNVB95uzDbxbfbrLmSKG3Mh0").build()  # <-- Вставь свой токен

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
from telegram import Update, ReplyKeyboardMarkup, InputMediaPhoto
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
        "место": "Правая набережная 9, «Браво Италия»"
    }
}

organizer_contact = "@elenaelectrodvor"

main_menu = ReplyKeyboardMarkup([
    ["Купить билет", "Контакты"],
    ["Задать вопрос", "Ближайшие мероприятия"],
    ["Дресс-код и правила посещения", "Немного о нас"]
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
        result = []
        for name, info in event_details.items():
            result.append(f"🎉 {name}\n📍 {info['место']}\n🕖 {info['время']}\n💳 {info['цена']}")
        await update.message.reply_text("\n\n".join(result), reply_markup=main_menu)
        return CHOOSE_ACTION

    elif text == "Дресс-код и правила посещения":
        await update.message.reply_text(
            "👗 *Дресс-код и правила посещения:*\n\n"
            "1️⃣ Белый дресс-код приветствуется (White DC)\n"
            "2️⃣ Улыбка и хорошее настроение обязательны\n"
            "3️⃣ Уважение к другим гостям\n"
            "4️⃣ Не допускается пронос алкоголя и запрещённых веществ\n"
            "5️⃣ Организаторы оставляют за собой право отказать во входе без объяснения причин",
            reply_markup=main_menu,
            parse_mode="Markdown"
        )
        return CHOOSE_ACTION

    elif text == "Немного о нас":
        await update.message.reply_photo(
            photo="URL_ТВОЕГО_ЛОГОТИПА",
            caption=(
                "🎶 *История Electrodvor*\n\n"
                "Мы начали с маленькой вечеринки для друзей, а сегодня собираем сотни единомышленников на уникальные мероприятия с особенной атмосферой, музыкой и заботой о каждом госте. "
                "Electrodvor — это не просто вечеринки, это стиль жизни, единство и эстетика.\n\n"
                "Присоединяйся к нашему движению ❤️"
            ),
            parse_mode="Markdown",
            reply_markup=main_menu
        )
        return CHOOSE_ACTION

    else:
        await update.message.reply_text("Пожалуйста, выберите вариант из меню.", reply_markup=main_menu)
        return CHOOSE_ACTION

# Остальные обработчики без изменений (ты можешь вставить их из своего кода):
# handle_event_choice, handle_question, handle_detail_question, cancel

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
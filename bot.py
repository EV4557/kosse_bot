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
        "место": "Место проведения: Правая набережная 9, «Браво Италия»"
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

    elif text == "Ближайшие мероприятия":
        message = ""
        for name, details in event_details.items():
            message += f"🎉 *{name}*\n📍 {details['место']}\n🕒 {details['время']}\n💸 {details['цена']}\n🔗 {details['ссылка']}\n\n"
        await update.message.reply_text(message, parse_mode="Markdown", reply_markup=main_menu)
        return CHOOSE_ACTION

    elif text == "Немного о нас":
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo="https://raw.githubusercontent.com/EV4557/electrodvor-bot/refs/heads/main/logo.PNG",
            caption=(
                "✨ *Немного о нас*\n\n"
                 "ELECTRODVOR — на данный момент самое свежее веяние музыкальной, развлекательной индустрии города. "
            "Абсолютно новый арт-проект, создающий уникальные ивенты в Калининграде.\n\n"
            "Команда, запустившая ELECTRODVOR, имеет опыт проведения более 400 ивентов, большинство из которых являются "
            "самыми востребованными и крупными для города.\n\n"
            "Проект управлял такими глобальными объектами, как бастион Астрономический — 2 года, провёл там 13 концептуальных "
            "опен-эйров и под сотню других ивентов.\n\n"
            "Такие события, как Хеллоуин, День города, Небосвод, Астероид, Full Moon Party, Заброшка, Никитин, Laguna Beach — "
            "одни из самых крупных и уникальных в стране.\n\n"
            "ELECTRODVOR — творческая, движущая сила города, что подтверждается самой высокой посещаемостью в области.\n\n"
            "Основатель и продюсер проекта — Евгений Зязев (творческие псевдонимы: Хром Бом, Джонни Легенда) — имеет десятки кейсов "
            "по созданию и успешному запуску концертных площадок и баров. Фирменный почерк в брендинге и организации мероприятий "
            "любого уровня и характера. Багаж — международные и федеральные проекты.\n\n"
            "Сейчас проект полностью перешёл в формат развития электронной сцены Калининграда. Проект насчитывает более 50 специалистов "
            "и участников. Команда занимается полным циклом создания мероприятий: от барного/ресторанного менеджмента до музыкального "
            "продакшена, SMM, промо, съёмки, упаковки под ключ любой задачи.\n\n"
            "С любовью,\nELECTRODVOR"
            ),
            parse_mode="Markdown"
        )
        return CHOOSE_ACTION

    elif text == "Дресс-код и правила посещения":
        rules = (
            "🎩 *Дресс-код и правила посещения:*\n\n"
            "1️⃣ Одежда должна быть чистой, опрятной и соответствовать тематике мероприятия.\n"
            "2️⃣ Запрещена спортивная одежда, пляжная, сильно порванная или загрязнённая.\n"
            "3️⃣ Проявляйте уважение к другим гостям и персоналу.\n"
            "4️⃣ Мы оставляем за собой право отказать в посещении без объяснения причин и возврата средств.\n"
            "5️⃣ Билеты не подлежат возврату менее чем за 3 дня до мероприятия.\n\n"
            "📌 Благодарим за понимание и соблюдение правил. До встречи на Electrodvor!"
        )
        await update.message.reply_text(rules, parse_mode="Markdown", reply_markup=main_menu)
        return CHOOSE_ACTION

    elif text == "Задать вопрос":
        keyboard = [
            ["Цена", "Время", "Место", "Оформить возврат билета"],
            ["⬅ Назад"]
        ]
        await update.message.reply_text(
            "❓ Вы можете выбрать один из часто задаваемых вопросов:\n\n"
            "— Цена билета\n"
            "— Время мероприятия\n"
            "— Место проведения\n"
            "— Оформить возврат билета\n\n"
            "Или введите свой вопрос текстом:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return ASK_QUESTION

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
        await update.message.reply_text(
            "Вы вернулись в главное меню.",
            reply_markup=main_menu
        )
        return CHOOSE_ACTION

    if text in event_details:
        link = event_details[text]["ссылка"]
        await update.message.reply_text(
            f"Вот ссылка для покупки билета на '{text}':\n{link}",
            reply_markup=main_menu
        )
        return CHOOSE_ACTION
    else:
        await update.message.reply_text(
            "Такого мероприятия нет. Выберите из списка."
        )
        return CHOOSE_EVENT


# Вопросы
async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "⬅ Назад":
        await update.message.reply_text(
            "Вы вернулись в главное меню.",
            reply_markup=main_menu
        )
        return CHOOSE_ACTION

    if text == "Оформить возврат билета":
        await update.message.reply_text(
            f"🧾 Для оформления возврата билета напишите на {organizer_contact} и укажите следующую информацию:\n\n"
            "1️⃣ Номер заказа\n"
            "2️⃣ Название мероприятия\n"
            "3️⃣ Какие билеты вы хотите вернуть\n"
            "4️⃣ Почта, на которую был оформлен заказ\n"
            "5️⃣ Скриншот оплаты с банка\n"
            "6️⃣ Причина возврата\n\n"
            "📌 Условия возврата:\n"
            "– Более 10 дней до мероприятия — удержание 0%\n"
            "– От 5 до 10 дней — удержание 50%\n"
            "– От 3 до 5 дней — удержание 70%\n"
            "– Менее 3 дней — возврат невозможен",
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
        "О каком мероприятии идет речь?",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return DETAIL_QUESTION


# Уточнение вопроса
async def handle_detail_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "⬅ Назад":
        keyboard = [["Цена", "Время", "Место"], ["⬅ Назад"]]
        await update.message.reply_text(
            "Выберите вопрос снова:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return ASK_QUESTION

    question_type = context.user_data.get("question_type")

    if text not in event_details or question_type not in event_details[text]:
        await update.message.reply_text(
            "Что-то пошло не так. Попробуйте снова.",
            reply_markup=main_menu
        )
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
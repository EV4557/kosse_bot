import sys
sys.path.insert(0, "/home/ispasatel/www/kosse_bot/site-packages")  # путь на сервере
import os
from telegram import (
    Update, ReplyKeyboardMarkup,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, filters, ConversationHandler
)

print("🚀 Запускается новый код Kosse Bot!")

CHOOSE_ACTION, ASK_QUESTION, BUY_TICKET, CHOOSE_EVENT_FOR_QUESTION = range(4)

organizer_contact = "@kosse_club"

ABOUT_TEXT = (
    "Kosse.club — это турбаза «Кемпинг зона», созданная для проведения мероприятий семейного и бизнес-формата.\n\n"
    "Мы предлагаем:\n"
    "• 👨‍👩‍👧‍👦 Семейные праздники — свадьбы, дни рождения, аренда территории для личных мероприятий.\n"
    "• 🏢 Корпоративные форматы — майсы, ивенты, тимбилдинги, ретриты.\n"
    "• 🎯 Развлечения и активный отдых — пейнтбол, командные игры («Крокодил», «Битва Героев»).\n"
    "• 🍷 Гастрономические программы — дегустации вин и других напитков, сомелье сессии.\n"
    "• 🎨 Творческие мастер-классы — лепка, керамика, создание трендовых игрушек и изделий.\n\n"
    "У нас вы найдёте всё для яркого отдыха и сплочения команды — от душевных семейных торжеств до масштабных корпоративных событий."
)

ABOUT_PHOTO = "https://raw.githubusercontent.com/EV4557/KOSSE.club---bot/main/logoKosse.png"

# Главное меню
main_menu = ReplyKeyboardMarkup([
    ["Контакты", "Ближайшие мероприятия"],
    ["Немного о нас", "Дресс-код и правила посещения"],
    ["Задать вопрос", "Купить билет"]
], resize_keyboard=True)

# Мероприятия
EVENTS = {
    "Хоровод Света": {
        "ссылка": "https://kaliningrad.qtickets.events/183804-khorovod-sveta",
        "цена": "🎟️ Дети с 4-12 — 700₽\n💎 Стандартный — 1000₽\n🎩 Все включено — 1400₽",
        "время": "🕖 13 сентября\nНачало в 13:00, окончание в 22:00",
        "место": "📍 Кемпинг Kosse.club, ул. Советская, 10, Янтарный."
    }
}

# Ключевые слова
PRICE_KEYWORDS = ["цена", "цен", "стоимость", "сколько стоит", "билет", "прайс", "оплата", "денег", "руб", "₽"]
TIME_KEYWORDS = ["время", "времен", "когда", "во сколько", "расписание", "дата", "число", "сроки", "день", "начало", "окончание"]
PLACE_KEYWORDS = ["место", "мест", "где", "адрес", "локация", "территория", "площадка", "кемпинг", "kosse", "kosse.club", "как добраться"]
RETURN_KEYWORDS = ["возврат", "вернуть", "обмен", "refund", "отмена", "отменить", "сдать билет", "вернуть деньги"]
CONTACT_KEYWORDS = ["контакт", "связь", "телефон", "почта", "email", "организатор", "поддержка", "админ"]
ABOUT_KEYWORDS = ["о вас", "о клубе", "о нас", "инфо", "информация", "что такое kosse", "немного о вас", "чем занимаетесь"]

# --- Handlers ---

# Старт
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот Kosse.club 🎟️\nВыберите, что вас интересует:",
        reply_markup=main_menu
    )
    return CHOOSE_ACTION

# Обработка FAQ (выбор категории)
async def handle_faq_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_clean = update.message.text.strip().lower()

    if text_clean in ["цена", "время", "место"]:
        context.user_data["faq_type"] = text_clean
        keyboard = [[name] for name in EVENTS.keys()] + [["⬅ Назад"]]
        await update.message.reply_text(
            "Выберите мероприятие, про которое хотите узнать:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return CHOOSE_EVENT_FOR_QUESTION

    elif text_clean == "возврат билета":
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

    elif text_clean == "⬅ назад":
        await update.message.reply_text("Возвращаюсь в главное меню.", reply_markup=main_menu)
        return CHOOSE_ACTION

    else:
        await update.message.reply_text("Пожалуйста, выберите вариант из меню.")
        return ASK_QUESTION

# Обработка выбора мероприятия для FAQ
async def handle_faq_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "⬅ Назад":
        await update.message.reply_text("Возвращаюсь в главное меню.", reply_markup=main_menu)
        return CHOOSE_ACTION

    faq_type = context.user_data.get("faq_type")
    event_info = EVENTS.get(text)

    if not event_info:
        await update.message.reply_text("Пожалуйста, выберите мероприятие из списка.")
        return CHOOSE_EVENT_FOR_QUESTION

    if faq_type == "цена":
        msg = f"Цена на {text}:\n{event_info.get('цена', 'Цены уточняются.')}"
    elif faq_type == "время":
        msg = f"Время проведения {text}:\n{event_info.get('время', 'Время уточняется.')}"
    elif faq_type == "место":
        msg = f"Место проведения {text}:\n{event_info.get('место', 'Место уточняется.')}"
    else:
        msg = "Информация недоступна."

    await update.message.reply_text(msg, reply_markup=main_menu)
    context.user_data.pop("faq_type", None)
    return CHOOSE_ACTION

# Главное меню
async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_clean = update.message.text.strip().lower()

    # Купить билет
    if text_clean == "купить билет":
        keyboard = [[event] for event in EVENTS.keys()] + [["⬅ Назад"]]
        await update.message.reply_text(
            "Выберите мероприятие для покупки билета:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        return BUY_TICKET

    # Контакты / поддержка
    elif any(word in text_clean for word in CONTACT_KEYWORDS + ["поддержка", "связь", "контакт"]):
        await update.message.reply_text(f"📞 Свяжитесь с организатором:\n{organizer_contact}", reply_markup=main_menu)
        return CHOOSE_ACTION

    # Ближайшие мероприятия
    elif text_clean == "ближайшие мероприятия":
        if not EVENTS:
            await update.message.reply_text("📅 Список ближайших мероприятий пока пуст.", reply_markup=main_menu)
            return CHOOSE_ACTION
        for name, info in EVENTS.items():
            message = f"🎉 {name}\n{info.get('время','')}\n{info.get('место','')}"
            keyboard = [[InlineKeyboardButton("Купить билет", url=info['ссылка'])]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(message, reply_markup=reply_markup)
        return CHOOSE_ACTION

    # О нас
    elif text_clean == "немного о нас":
        await update.message.reply_photo(photo=ABOUT_PHOTO, caption="Проект Kosse.club 👇", reply_markup=main_menu)
        await update.message.reply_text(ABOUT_TEXT, reply_markup=main_menu)
        return CHOOSE_ACTION

    # Дресс-код
    elif text_clean == "дресс-код и правила посещения":
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

    # Задать вопрос
    elif text_clean == "задать вопрос":
        keyboard = [
            ["Цена", "Время", "Место", "Возврат билета"],
            ["⬅ Назад"]
        ]
        await update.message.reply_text(
            "❓ Часто задаваемые вопросы:\nВыберите категорию:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )
        context.user_data["fail_count"] = 0
        return ASK_QUESTION

    # Проверка ключевых слов для FAQ
    elif any(word in text_clean for word in PRICE_KEYWORDS + TIME_KEYWORDS + PLACE_KEYWORDS + RETURN_KEYWORDS + ABOUT_KEYWORDS):
        return await handle_faq_question(update, context)

    # Любой другой текст
    else:
        await update.message.reply_text("Пожалуйста, выберите вариант из меню.", reply_markup=main_menu)
        return CHOOSE_ACTION

# Обработка покупки билета
async def handle_buy_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "⬅ Назад":
        await update.message.reply_text("Возвращаюсь в главное меню.", reply_markup=main_menu)
        return CHOOSE_ACTION

    if text in EVENTS:
        await update.message.reply_text(f"🎫 Ссылка для покупки билета:\n{EVENTS[text]['ссылка']}", reply_markup=main_menu)
        return CHOOSE_ACTION
    else:
        await update.message.reply_text("Пожалуйста, выберите мероприятие из списка.")
        return BUY_TICKET

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
            ASK_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_faq_question)],
            CHOOSE_EVENT_FOR_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_faq_event)],
            BUY_TICKET: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buy_ticket)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    app.run_polling()

if __name__ == "__main__":
    main()
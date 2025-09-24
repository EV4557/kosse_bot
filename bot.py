import sys
sys.path.insert(0, "/home/ispasatel/www/kosse_bot/site-packages")  # путь к сторонним библиотекам
import os
import json
import pytz
import datetime
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler, CallbackQueryHandler

# --- Работа с Google Sheets ---
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- Для загрузки переменных окружения ---
from dotenv import load_dotenv
load_dotenv()

# ================== НАСТРОЙКИ ==================
organizer_contact = "@kosse_club"

ABOUT_PHOTO = "https://raw.githubusercontent.com/EV4557/KOSSE.club---bot/main/logoKosse.png"
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

# Главное меню старта
start_menu = ReplyKeyboardMarkup([
    ["Узнать о мероприятиях", "Узнать об аренде"]
], resize_keyboard=True)

# Основное меню мероприятий
events_menu = ReplyKeyboardMarkup([
    ["Контакты", "Ближайшие мероприятия"],
    ["Немного о нас", "Правила посещения"],
    ["Задать вопрос", "Купить билет"],
    ["⬅ Главное меню"]
], resize_keyboard=True)

# ================== GOOGLE SHEETS ==================
def get_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_json = os.getenv("GOOGLE_CREDS_JSON")
    if not creds_json:
        raise ValueError("⚠️ GOOGLE_CREDS_JSON не найден! Добавьте переменную окружения на Railway")
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

def load_events_from_sheets():
    client = get_client()
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id:
        raise ValueError("⚠️ GOOGLE_SHEET_ID не найден! Укажи его в .env")
    sheet = client.open_by_key(sheet_id).sheet1
    rows = sheet.get_all_records()

    events = {}
    for row in rows:
        if str(row.get("Активно", "")).strip().lower() != "да":
            continue
        events[row["Название"]] = {
            "ссылка": row.get("Ссылка", ""),
            "цена": row.get("Цена", ""),
            "время": row.get("Время", ""),
            "место": row.get("Место", ""),
            "дресс-код": row.get("Дресс-код", "").strip(),
            "описание": row.get("Описание", "").strip()
        }
    return events

# ================== АРЕНДА ==================
RENT_DATA = None
RENT_LAST_UPDATE = None
RENT_UPDATE_INTERVAL = 10 * 60  # 10 минут
RENT_CHAT_MAP = {}  # словарь для chat_id по лицевым счетам
REMINDER_LAST_SENT = {}  # чтобы учитывать дату последнего напоминания

def load_rent_sheet(force=False):
    global RENT_DATA, RENT_LAST_UPDATE
    now = datetime.datetime.now().timestamp()
    if force or RENT_DATA is None or RENT_LAST_UPDATE is None or (now - RENT_LAST_UPDATE) > RENT_UPDATE_INTERVAL:
        client = get_client()
        rent_sheet_id = os.getenv("GOOGLE_SHEET_RENT_ID")
        sheet = client.open_by_key(rent_sheet_id).worksheet("РАБОЧАЯ_2 квартал")
        RENT_DATA = sheet.get_all_values()
        RENT_LAST_UPDATE = now
        print("🔄 Таблица аренды автоматически обновлена")
    return RENT_DATA

def get_rent_info(account_number):
    try:
        all_rows = load_rent_sheet(force=True)
        if not all_rows or len(all_rows) < 3:
            return {"error": "❌ Лист пустой или нет данных."}

        # Текущий месяц и год
        now = datetime.datetime.now()
        month_name = now.strftime("%B").capitalize()
        month_rus = {
            "January":"Январь","February":"Февраль","March":"Март","April":"Апрель",
            "May":"Май","June":"Июнь","July":"Июль","August":"Август","September":"Сентябрь",
            "October":"Октябрь","November":"Ноябрь","December":"Декабрь"
        }[month_name]
        current_month = f"{month_rus} {now.year}"

        # Столбец лицевых счетов (A)
        account_col_idx = 0
        account_row = None
        account_number_str = str(account_number).strip()
        for row in all_rows[2:]:
            if len(row) > account_col_idx and str(row[account_col_idx]).strip() == account_number_str:
                account_row = row
                break
        if not account_row:
            return {"error": f"❌ Лицевой счёт {account_number} не найден."}

        # Колонка нужного месяца
        header_row = all_rows[0]
        month_col_idx = None
        for idx, val in enumerate(header_row):
            if str(val).strip().lower() == current_month.lower():
                month_col_idx = idx
                break
        if month_col_idx is None:
            return {"error": f"ℹ️ Данные за {current_month} не найдены."}

        total_col_idx = month_col_idx + 4
        total_value = account_row[total_col_idx] if len(account_row) > total_col_idx else "0"
        try:
            total_value_num = float(str(total_value).replace(",", "."))
        except:
            total_value_num = 0

        return {
            "account": account_number_str,
            "month": current_month,
            "total": total_value_num
        }

    except Exception as e:
        return {"error": f"Ошибка при получении данных: {e}"}

# ================== СОСТОЯНИЯ ==================
CHOOSE_ACTION, ASK_QUESTION, BUY_TICKET, CHOOSE_EVENT_FOR_QUESTION, ASK_ACCOUNT = range(5)

# ================== КЛЮЧЕВЫЕ СЛОВА ==================
PRICE_KEYWORDS = ["цена", "стоимость", "билет", "оплата", "руб", "₽"]
TIME_KEYWORDS = ["время", "когда", "расписание", "дата", "начало", "окончание"]
PLACE_KEYWORDS = ["место", "где", "адрес", "локация", "кемпинг"]
RETURN_KEYWORDS = ["возврат", "вернуть", "обмен", "отмена", "сдать билет"]
CONTACT_KEYWORDS = ["контакт", "связь", "телефон", "почта", "email", "организатор"]
ABOUT_KEYWORDS = ["о вас", "о клубе", "о нас", "инфо", "информация"]

# ================== ОБРАБОТЧИКИ ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот Kosse.club 🎟️\nВыберите, что вас интересует:",
        reply_markup=start_menu
    )
    return CHOOSE_ACTION

async def refresh_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global EVENTS
    EVENTS = load_events_from_sheets()
    await update.message.reply_text("✅ Список мероприятий обновлён!", reply_markup=events_menu)
    return CHOOSE_ACTION

async def refresh_rent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    load_rent_sheet(force=True)
    await update.message.reply_text("✅ Таблица аренды обновлена!", reply_markup=start_menu)
    return CHOOSE_ACTION

async def handle_faq_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_clean = update.message.text.strip().lower()
    if text_clean in ["цена", "время", "место"]:
        context.user_data["faq_type"] = text_clean
        keyboard = [[name] for name in EVENTS.keys()] + [["⬅ Главное меню"]]
        await update.message.reply_text("Выберите мероприятие:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
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
            reply_markup=events_menu
        )
        return CHOOSE_ACTION
    elif text_clean == "⬅ главное меню":
        await update.message.reply_text("Выберите, что вас интересует:", reply_markup=start_menu)
        return CHOOSE_ACTION
    else:
        await update.message.reply_text("Пожалуйста, выберите вариант из меню.")
        return ASK_QUESTION

async def handle_faq_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "⬅ Главное меню":
        await update.message.reply_text("Выберите, что вас интересует:", reply_markup=start_menu)
        return CHOOSE_ACTION
    faq_type = context.user_data.get("faq_type")
    event_info = EVENTS.get(text)
    if not event_info:
        await update.message.reply_text("Выберите мероприятие из списка.")
        return CHOOSE_EVENT_FOR_QUESTION
    if faq_type == "цена":
        msg = f"Цена на {text}: {event_info.get('цена', 'Уточняется')}"
    elif faq_type == "время":
        msg = f"Время проведения {text}: {event_info.get('время', 'Уточняется')}"
    elif faq_type == "место":
        msg = f"Место проведения {text}: {event_info.get('место', 'Уточняется')}"
    else:
        msg = "Информация недоступна."
    await update.message.reply_text(msg, reply_markup=events_menu)
    context.user_data.pop("faq_type", None)
    return CHOOSE_ACTION

async def handle_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_clean = update.message.text.strip().lower()
    if text_clean == "⬅ главное меню":
        await update.message.reply_text("Выберите, что вас интересует:", reply_markup=start_menu)
        return CHOOSE_ACTION
    if text_clean == "узнать о мероприятиях":
        await update.message.reply_text("Выберите вариант:", reply_markup=events_menu)
        return CHOOSE_ACTION
    elif text_clean == "узнать об аренде":
        await update.message.reply_text("Введите ваш лицевой счёт (например: 12345):")
        return ASK_ACCOUNT
    elif text_clean == "купить билет":
        keyboard = [[event] for event in EVENTS.keys()] + [["⬅ Главное меню"]]
        await update.message.reply_text("Выберите мероприятие:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return BUY_TICKET
    elif any(word in text_clean for word in CONTACT_KEYWORDS):
        await update.message.reply_text(f"📞 Контакты:\n{organizer_contact}", reply_markup=events_menu)
        return CHOOSE_ACTION
    elif text_clean == "ближайшие мероприятия":
        if not EVENTS:
            await update.message.reply_text("Сейчас мероприятий нет.", reply_markup=events_menu)
        else:
            for name, info in sorted(EVENTS.items()):
                msg = f"🎉 {name}\n{info.get('время','')}\n{info.get('место','')}"
                keyboard = []
                link = info.get("ссылка", "").strip()
                if link and (link.startswith("http://") or link.startswith("https://")):
                    keyboard.append([InlineKeyboardButton("Купить билет", url=link)])
                if info.get("дресс-код"):
                    keyboard.append([InlineKeyboardButton("Дресс-код", callback_data=f"dress:{name}")])
                if info.get("описание"):
                    keyboard.append([InlineKeyboardButton("Подробнее", callback_data=f"about:{name}")])
                reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
                await update.message.reply_text(msg, reply_markup=reply_markup)
        return CHOOSE_ACTION
    elif text_clean == "немного о нас":
        await update.message.reply_photo(photo=ABOUT_PHOTO, caption="Проект Kosse.club 👇", reply_markup=events_menu)
        await update.message.reply_text(ABOUT_TEXT, reply_markup=events_menu)
        return CHOOSE_ACTION
    elif text_clean == "правила посещения":
        rules = (
            "🎟️ *Правила посещения:*\n\n"
            "1️⃣ Вход возможен только при наличии билета.\n"
            "2️⃣ Каждый гость должен иметь при себе документ, удостоверяющий личность.\n"
            "3️⃣ Организаторы оставляют за собой право отказать во входе без объяснения причин и без возврата средств.\n"
            "4️⃣ На мероприятие не допускаются лица в спортивной, грязной или неподобающей обстановке одежде.\n"
            "5️⃣ Ответственность за сохранность личных вещей и инвентаря турбазы несут посетители.\n"
            "6️⃣ Запрещены: агрессивное поведение, наркотические вещества, алкогольные напитки и оружие.\n"
            "7️⃣ Нарушители правил могут быть удалены без компенсации стоимости билета.\n\n"
            "🙏 Спасибо за понимание и уважение к правилам!"
        )
        await update.message.reply_text(rules, parse_mode="Markdown", reply_markup=events_menu)
        return CHOOSE_ACTION
    elif text_clean == "задать вопрос":
        keyboard = [["Цена", "Время", "Место", "Возврат билета"], ["⬅ Главное меню"]]
        await update.message.reply_text("❓ Выберите категорию:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return ASK_QUESTION
    elif any(word in text_clean for word in PRICE_KEYWORDS + TIME_KEYWORDS + PLACE_KEYWORDS + RETURN_KEYWORDS + ABOUT_KEYWORDS):
        return await handle_faq_question(update, context)
    else:
        await update.message.reply_text("Выберите вариант из меню.", reply_markup=events_menu)
        return CHOOSE_ACTION

async def handle_buy_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "⬅ Главное меню":
        await update.message.reply_text("Выберите, что вас интересует:", reply_markup=start_menu)
        return CHOOSE_ACTION
    if text in EVENTS:
        await update.message.reply_text(f"🎫 Ссылка для покупки билета:\n{EVENTS[text]['ссылка']}", reply_markup=events_menu)
        return CHOOSE_ACTION
    else:
        await update.message.reply_text("Выберите мероприятие из списка.")
        return BUY_TICKET

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("dress:"):
        event_name = data.split(":", 1)[1]
        dress = EVENTS.get(event_name, {}).get("дресс-код", "Информация отсутствует")
        await query.message.reply_text(f"👔 Дресс-код для {event_name}:\n{dress}")
    elif data.startswith("about:"):
        event_name = data.split(":", 1)[1]
        about = EVENTS.get(event_name, {}).get("описание", "Информация отсутствует")
        await query.message.reply_text(f"ℹ️ Подробнее о {event_name}:\n{about}")

async def handle_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    account = update.message.text.strip()
    info = get_rent_info(account)

    if "error" in info:
        await update.message.reply_text(info["error"], reply_markup=start_menu)
        return CHOOSE_ACTION

    amount = info["total"]
    month_rus = info["month"]

    if amount < 0:
        await update.message.reply_text(
            f"💳 По лицевому №{account} за {month_rus} задолженность: {abs(amount)} руб.",
            reply_markup=start_menu
        )
    elif amount > 0:
        await update.message.reply_text(
            f"✅ По лицевому №{account} за {month_rus} переплата: {amount} руб. Платить не нужно.",
            reply_markup=start_menu
        )
    else:
        await update.message.reply_text(
            f"✅ По лицевому №{account} за {month_rus} задолженности нет (0 руб).",
            reply_markup=start_menu
        )

    return CHOOSE_ACTION

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Главное меню:", reply_markup=start_menu)
    return CHOOSE_ACTION

# ================== РАССЫЛКА ==================

async def send_rent_reminders(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now(pytz.timezone("Europe/Moscow"))

    # Рассылка только с 24 по 2 число включительно
    if now.day < 24 and now.month != 2:  # февраль отдельно, чтобы не сломать
        return
    if now.day > 2 and now.day < 24:
        return

    # Разрешаем только 24-го, 26-го, 28-го, 30-го и 1-го, 2-го числа
    # Проверка "каждые два дня"
    if now.day >= 24 or now.day <= 2:
        if not ((now.day - 24) % 2 == 0 or now.day in [1, 2]):
            return

    load_rent_sheet(force=True)

    for row in RENT_DATA[2:]:
        if len(row) < 2:
            continue
        account_number = row[0].strip()
        chat_id = row[1].strip()
        if not chat_id.isdigit():
            continue
        chat_id = int(chat_id)

        info = get_rent_info(account_number)
        if "error" in info:
            continue
        total = info["total"]
        if total >= 0:
            continue  # нет задолженности

        text_message = (
            f"Здравствуйте, уважаемый абонент!\n\n"
            f"Напоминаем, что абонентская плата должна быть внесена **до 3-го числа** текущего месяца "
            f"(согласно п. 4.1.1 договора).\n\n"
            f"Баланс на сегодня: {abs(total)} р.\n\n"
            "⚠️ Если оплата не поступит до 3-го числа, сумма задолженности будет увеличена!\n\n"
            "Оплатить можно переводом на карту Т-Банк по номеру +79062385238 (Валентина Савватиевна А.).\n"
            "Квитанцию об оплате необходимо прислать на этот номер.\n\n"
            "С уважением, ГК ТырНэт.рф!"
        )
        try:
            await context.bot.send_message(chat_id=chat_id, text=text_message, parse_mode="Markdown")
            print(f"📤 Напоминание отправлено на {chat_id}")
        except Exception as e:
            print(f"❌ Ошибка отправки на {chat_id}: {e}")

# ================== ЗАПУСК БОТА ==================
def main():
    TOKEN = "8244050011:AAGP565NclU046a-WsP-nO8hNOcvkwQCh0U"
    if not TOKEN:
        raise ValueError("⚠️ Токен не найден! Проверьте .env")

    global EVENTS
    EVENTS = load_events_from_sheets()

    app = Application.builder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_action)],
            ASK_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_faq_question)],
            CHOOSE_EVENT_FOR_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_faq_event)],
            BUY_TICKET: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buy_ticket)],
            ASK_ACCOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_account)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("refresh", refresh_events))
    app.add_handler(CommandHandler("refresh_rent", refresh_rent))
    app.add_handler(CallbackQueryHandler(button_handler))

    async def auto_refresh_events(context: ContextTypes.DEFAULT_TYPE):
        global EVENTS
        EVENTS = load_events_from_sheets()
        print("🔄 Список мероприятий автоматически обновлён")

    async def auto_refresh_rent(context: ContextTypes.DEFAULT_TYPE):
        load_rent_sheet()

    # каждые 10 минут обновляем список мероприятий и аренду
    app.job_queue.run_repeating(auto_refresh_events, interval=600, first=10)
    app.job_queue.run_repeating(auto_refresh_rent, interval=600, first=10)

    # проверка должников каждый день, но рассылка только с 24 числа
    # запускать в 16:00 по Москве каждый день
    moscow_tz = pytz.timezone("Europe/Moscow")
    target_time = datetime.time(hour=16, minute=0, tzinfo=moscow_tz)
    app.job_queue.run_daily(send_rent_reminders, time=target_time)

    print("🚀 Бот запущен и готов к работе!")
    app.run_polling()

if __name__ == "__main__":
    main()
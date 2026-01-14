import os
from datetime import date, timedelta
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

ANCHOR_DATE = date(2026, 1, 15)

EMPLOYEES = {
    "Приходько": 0,
    "Иващенко": 8,
    "Вербицкий": -3,
    "Маслак": -6
}

def shift_by_day(day):
    if 1 <= day <= 3:
        return "УТРО (07:00–15:00)"
    if day == 4:
        return "ВЫХОДНОЙ"
    if 5 <= day <= 6:
        return "НОЧЬ (23:00–07:00)"
    if day == 7:
        return "ОТСЫПНОЙ"
    if day == 8:
        return "ВЫХОДНОЙ"
    if 9 <= day <= 11:
        return "ВЕЧЕР (15:00–23:00)"
    return "ВЫХОДНОЙ"

def cycle_day(target_date, offset):
    delta = (target_date - ANCHOR_DATE).days + offset
    return (delta % 12) + 1

def get_shift(name, target_date):
    day = cycle_day(target_date, EMPLOYEES[name])
    return shift_by_day(day)

def month_schedule(name):
    today = date.today()
    first = today.replace(day=1)
    next_month = (first.replace(day=28) + timedelta(days=4)).replace(day=1)
    days = (next_month - first).days

    lines = []
    for d in range(days):
        current = first + timedelta(days=d)
        shift = get_shift(name, current)
        lines.append(f"{current.day:02d} — {shift.split()[0]}")
    return "\n".join(lines)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["📅 Сегодня", "🔁 Смены"]
    ]
    await update.message.reply_text(
        "👷‍♂ Диспетчер смен",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = "Приходько"
    shift = get_shift(name, date.today())
    await update.message.reply_text(
        f"👷 {name}\n\nСмена: {shift}\nМаршрут: Шостка — Кролевец"
    )

async def shifts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[name] for name in EMPLOYEES.keys()]
    await update.message.reply_text(
        "Выберите сотрудника:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def employee(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    if name not in EMPLOYEES:
        return
    today_shift = get_shift(name, date.today())
    schedule = month_schedule(name)
    await update.message.reply_text(
        f"👷 {name}\n\nСегодня: {today_shift}\n\n📆 Текущий месяц:\n{schedule}"
    )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Regex("📅 Сегодня"), today))
app.add_handler(MessageHandler(filters.Regex("🔁 Смены"), shifts))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, employee))

app.run_polling()

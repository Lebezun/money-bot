import telebot
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = "8249235733:AAFcyDukXENtAUpH8WPNg6aux8ljiM4zlls"
bot = telebot.TeleBot(BOT_TOKEN)

conn = sqlite3.connect("expenses.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    category TEXT,
    amount REAL,
    date TEXT
)
''')
conn.commit()

def parse_expense(text):
    try:
        parts = text.strip().split()
        amount = float(parts[-1])
        category = " ".join(parts[:-1]) if len(parts) > 1 else "Інше"
        return category.capitalize(), amount
    except:
        return None, None

def get_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(
        KeyboardButton('Витратив сьогодні'),
        KeyboardButton('Витратив за тиждень'),
        KeyboardButton('Витратив за місяць')
    )
    markup.row(
        KeyboardButton('Найбільше витрачено на товар'),
        KeyboardButton('Графік витрат')
    )
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(
        message.chat.id,
        "Привіт! Я твій Грошовий Інспектор 💸\nВведи витрату у форматі:\nНазва сума\nНаприклад: Кава 50",
        reply_markup=get_markup()
    )

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_id = message.from_user.id
    text = message.text
    markup = get_markup()

    if text == 'Витратив сьогодні':
        date_from = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cursor.execute(
            "SELECT SUM(amount) FROM expenses WHERE user_id = ? AND date >= ?", (user_id, date_from.strftime("%Y-%m-%d %H:%M:%S")))
        total = cursor.fetchone()[0] or 0
        bot.send_message(message.chat.id, f"💰 Витратив сьогодні: {total:.2f} грн", reply_markup=markup)

    elif text == 'Витратив за тиждень':
        date_from = datetime.now() - timedelta(days=7)
        cursor.execute(
            "SELECT SUM(amount) FROM expenses WHERE user_id = ? AND date >= ?", (user_id, date_from.strftime("%Y-%m-%d %H:%M:%S")))
        total = cursor.fetchone()[0] or 0
        bot.send_message(message.chat.id, f"💰 Витратив за останній тиждень: {total:.2f} грн", reply_markup=markup)

    elif text == 'Витратив за місяць':
        date_from = datetime.now() - timedelta(days=30)
        cursor.execute(
            "SELECT SUM(amount) FROM expenses WHERE user_id = ? AND date >= ?", (user_id, date_from.strftime("%Y-%m-%d %H:%M:%S")))
        total = cursor.fetchone()[0] or 0
        bot.send_message(message.chat.id, f"💰 Витратив за останній місяць: {total:.2f} грн", reply_markup=markup)

    elif text == 'Найбільше витрачено на товар':
        cursor.execute(
            "SELECT category, SUM(amount) as total FROM expenses WHERE user_id = ? GROUP BY category ORDER BY total DESC LIMIT 1",
            (user_id,))
        row = cursor.fetchone()
        if row:
            bot.send_message(message.chat.id, f"🛒 Найбільше витрачено на: {row[0]} — {row[1]:.2f} грн", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Поки що немає витрат 😢", reply_markup=markup)

    elif text == 'Графік витрат':
        cursor.execute(
            "SELECT category, SUM(amount) FROM expenses WHERE user_id = ? GROUP BY category",
            (user_id,))
        data = cursor.fetchall()
        if not data:
            bot.send_message(message.chat.id, "Поки що немає витрат 😢", reply_markup=markup)
            return

        df = pd.DataFrame(data, columns=['Категорія', 'Сума'])
        plt.figure(figsize=(8, 6))
        plt.bar(df['Категорія'], df['Сума'], color='orange')
        plt.title('Витрати по категоріях')
        plt.xlabel('Категорія')
        plt.ylabel('Сума, грн')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        bot.send_photo(message.chat.id, buf, reply_markup=markup)

    else:
        category, amount = parse_expense(text)
        if category and amount:
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO expenses (user_id, category, amount, date) VALUES (?, ?, ?, ?)",
                           (user_id, category, amount, date))
            conn.commit()
            bot.send_message(message.chat.id, f"✅ Додано: {category} — {amount:.2f} грн", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "⚠️ Формат неправильний. Наприклад: Піца 150", reply_markup=markup)

bot.infinity_polling()

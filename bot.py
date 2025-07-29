import telebot
from telebot import types
from datetime import date, timedelta
import matplotlib.pyplot as plt
import os

from database import *

TOKEN = '8249235733:AAFcyDukXENtAUpH8WPNg6aux8ljiM4zlls'
bot = telebot.TeleBot(TOKEN)

init_db()

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [
        "📅 Витрати за сьогодні",
        "📈 Витрати за тиждень",
        "🗓 Витрати за місяць",
        "🔝 Найбільше витрат",
        "📊 Графік витрат",
        "🧹 Очистити сьогоднішні витрати"
    ]
    markup.add(*[types.KeyboardButton(b) for b in buttons])
    return markup

@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_message(message.chat.id, "👋 Привіт! Введи витрату у форматі: 'Назва 100'", reply_markup=main_keyboard())

@bot.message_handler(func=lambda msg: msg.text == "📅 Витрати за сьогодні")
def today_expenses(message):
    total = get_total_by_period(date.today(), date.today())
    bot.send_message(message.chat.id, f"Сьогодні ти витратив: {total} грн")

@bot.message_handler(func=lambda msg: msg.text == "📈 Витрати за тиждень")
def week_expenses(message):
    start = date.today() - timedelta(days=7)
    total = get_total_by_period(start, date.today())
    bot.send_message(message.chat.id, f"За останній тиждень ти витратив: {total} грн")

@bot.message_handler(func=lambda msg: msg.text == "🗓 Витрати за місяць")
def month_expenses(message):
    start = date.today().replace(day=1)
    total = get_total_by_period(start, date.today())
    bot.send_message(message.chat.id, f"Цього місяця ти витратив: {total} грн")

@bot.message_handler(func=lambda msg: msg.text == "🔝 Найбільше витрат")
def top_expense(message):
    category, amount = get_biggest_category()
    bot.send_message(message.chat.id, f"🔝 Найбільше ти витратив на: {category} — {amount} грн")

@bot.message_handler(func=lambda msg: msg.text == "📊 Графік витрат")
def plot_expenses(message):
    data = get_today_expenses_grouped()
    if not data:
        bot.send_message(message.chat.id, "Сьогодні витрат ще не було.")
        return
    categories, amounts = zip(*data)
    plt.figure(figsize=(8, 6))
    plt.pie(amounts, labels=categories, autopct='%1.1f%%')
    plt.title('Сьогоднішні витрати')
    plt.savefig("chart.png")
    plt.close()
    with open("chart.png", 'rb') as photo:
        bot.send_photo(message.chat.id, photo)
    os.remove("chart.png")

@bot.message_handler(func=lambda msg: msg.text == "🧹 Очистити сьогоднішні витрати")
def clear_today(message):
    clear_today_expenses()
    bot.send_message(message.chat.id, "Витрати за сьогодні очищено ✅")

@bot.message_handler(func=lambda msg: True)
def add_expense_handler(message):
    try:
        parts = message.text.rsplit(" ", 1)
        category, amount = parts[0], int(parts[1])
        add_expense(category, amount)
        bot.send_message(message.chat.id, f"Додано: {category} — {amount} грн")
    except:
        bot.send_message(message.chat.id, "⚠️ Формат неправильний. Наприклад: Піца 150")

bot.infinity_polling()

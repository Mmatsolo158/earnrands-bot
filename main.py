import os
import telebot
from telebot import types
import sqlite3
from flask import Flask, request

# Configuration
BOT_TOKEN = os.getenv('7835854387:AAH4K9VvV7Zk2EX-YLEj04ydHKsawux-I5s')
PAYFAST_ID = os.getenv('PAYFAST_ID')
ADMIN_ID = os.getenv('6315924441')

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Database setup
def get_db():
    conn = sqlite3.connect('file:earnrands.db?mode=memory&cache=shared', uri=True)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance REAL DEFAULT 10.0,
        premium INTEGER DEFAULT 0
    )''')
    return conn

# Bot commands
@bot.message_handler(commands=['start'])
def start(message):
    conn = get_db()
    conn.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (message.from_user.id,))
    bot.reply_to(message, "🌟 *Bot Activated!* Use /earn")

if __name__ == '__main__':
    from threading import Thread
    Thread(target=app.run, kwargs={'host':'0.0.0.0','port':3000}).start()
    bot.polling()

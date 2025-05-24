import os
import telebot
from telebot import types
import sqlite3
from flask import Flask, request
from threading import Thread

# ======================
# 🛠 CONFIGURATION
# ======================
BOT_TOKEN = os.getenv('7835854387:AAH4K9VvV7Zk2EX-YLEj04ydHKsawux-I5s')  # From Railway variables
PAYFAST_ID = os.getenv('6315924441')  # Your PayFast merchant ID
ADMIN_ID = os.getenv('6315924441')  # Your Telegram ID
PORT = int(os.getenv('PORT', 3000))  # Railway provides this

if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN environment variable missing! Set it in Railway.")

# ======================
# 🏗 INITIALIZE
# ======================
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('file:earnrands.db?mode=memory&cache=shared', uri=True)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance REAL DEFAULT 10.0,
        premium INTEGER DEFAULT 0
    )''')
    conn.commit()
    return conn

# ======================
# 🤖 BOT COMMANDS
# ======================
@bot.message_handler(commands=['start'])
def start(message):
    conn = init_db()
    try:
        conn.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (message.from_user.id,))
        bot.reply_to(message, 
            "🌟 *EarnRands Bot Activated!*\n\n"
            "💰 Balance: R10 (Welcome Bonus!)\n"
            "💸 Earn more with /earn\n"
            "🔐 PayFast Verified | FSCA Compliant",
            parse_mode="Markdown")
    finally:
        conn.close()

@bot.message_handler(commands=['balance'])
def balance(message):
    conn = init_db()
    try:
        balance = conn.execute(
            'SELECT balance FROM users WHERE user_id = ?', 
            (message.from_user.id,)
        ).fetchone()[0]
        
        bot.reply_to(message, 
            f"📊 *Your Balance:* R{balance:.2f}\n\n"
            "💳 Withdraw: /cashout\n"
            "🚀 Boost earnings: /premium",
            parse_mode="Markdown")
    finally:
        conn.close()

# ======================
# 💰 PAYFAST INTEGRATION
# ======================
@app.route('/payfast-callback', methods=['POST'])
def payfast_callback():
    if request.form.get('payment_status') == 'COMPLETE':
        user_id = int(request.form['custom_str1'])
        conn = init_db()
        try:
            conn.execute(
                'UPDATE users SET premium=1, balance=balance+100 WHERE user_id=?',
                (user_id,)
            conn.commit()
            bot.send_message(user_id, "🎉 Premium activated! R100 deposited.")
        finally:
            conn.close()
    return '', 200

# ======================
# 🚀 STARTUP
# ======================
def run_flask():
    app.run(host='0.0.0.0', port=PORT, debug=False)

if __name__ == '__main__':
    # Verify critical config
    if not all([BOT_TOKEN, PAYFAST_ID, ADMIN_ID]):
        raise EnvironmentError("Missing required environment variables!")
    
    print(f"✅ Starting bot with token: {BOT_TOKEN[:10]}...")
    print(f"🔄 PayFast ID: {PAYFAST_ID}")
    print(f"🌐 Web server on port {PORT}")
    
    # Start Flask in separate thread
    Thread(target=run_flask).start()
    
    # Start Telegram bot with auto-reconnect
    bot.polling(none_stop=True, timeout=60)

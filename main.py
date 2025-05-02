import os
import asyncpg
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, render_template
import asyncio

# Telegram Bot API Token
API_TOKEN = os.getenv('API_TOKEN')

# PostgreSQL Database URL
DATABASE_URL = os.getenv('DATABASE_URL')

# Initialize Flask app
flask_app = Flask(__name__)

# Initialize PostgreSQL connection pool
async def init_db():
    return await asyncpg.create_pool(dsn=DATABASE_URL)

db_pool = asyncio.run(init_db())

# Define the /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "Hey! Welcome to Ask ARMY.\n"
        "Got something on your heart?\n"
        "Send your question here anonymously, and we’ll select and address these in our next youth panel or during the youth program."
    )
    await update.message.reply_text(welcome_message)

# Function to save the question to the PostgreSQL database
async def save_question(question: str):
    async with db_pool.acquire() as connection:
        await connection.execute('''
            INSERT INTO questions(question) VALUES($1)
        ''', question)

# Define the function for receiving anonymous questions
async def receive_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    await save_question(question)
    await update.message.reply_text("Thank you for sharing. Your question has been received anonymously.")

# Define the main function to set up the Telegram bot
def start_telegram_bot():
    application = Application.builder().token(API_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_question))
    application.run_polling()

# Flask route to display saved questions
@flask_app.route('/')
def index():
    async def fetch_questions():
        async with db_pool.acquire() as connection:
            rows = await connection.fetch('SELECT question, timestamp FROM questions ORDER BY timestamp DESC LIMIT 10')
            return [{'question': row['question'], 'timestamp': row['timestamp']} for row in rows]

    questions = asyncio.run(fetch_questions())
    return render_template('index.html', questions=questions)

# Run both Telegram bot and Flask app
if __name__ == '__main__':
    from threading import Thread

    # Start Telegram bot in a separate thread
    telegram_thread = Thread(target=start_telegram_bot)
    telegram_thread.start()

    # Start Flask app
    flask_app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

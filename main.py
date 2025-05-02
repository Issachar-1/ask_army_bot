import os
import asyncpg
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask, render_template
import asyncio
from threading import Thread

# Load environment variables
API_TOKEN = os.getenv('API_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')

# Flask app
flask_app = Flask(__name__)

# PostgreSQL connection pool
db_pool = None

# Telegram bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message1 = "Hey! Welcome to Ask ARMY."
    welcome_message2 = (
        "Got something on your heart?\nSend your question here anonymously, and we’ll "
        "select and address these in our next youth panel or during the youth program."
    )
    await update.message.reply_text(welcome_message1)
    await update.message.reply_text(welcome_message2)

async def save_question(question: str):
    async with db_pool.acquire() as connection:
        await connection.execute('INSERT INTO questions (question) VALUES ($1)', question)

async def receive_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    await save_question(question)
    await update.message.reply_text("Thank you for sharing. Your question has been received anonymously.")

def start_telegram_bot():
    application = Application.builder().token(API_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_question))
    application.run_polling()

# Flask route
@flask_app.route('/')
def index():
    async def fetch_questions():
        async with db_pool.acquire() as connection:
            rows = await connection.fetch(
                'SELECT question, timestamp FROM questions ORDER BY timestamp DESC'
            )
            return [{'question': row['question'], 'timestamp': row['timestamp']} for row in rows]

    questions = asyncio.run(fetch_questions())
    return render_template('index.html', questions=questions)

# Entry point
if __name__ == '__main__':
    async def main():
        global db_pool
        db_pool = await asyncpg.create_pool(dsn=DATABASE_URL)

        # Start Telegram bot in separate thread
        Thread(target=start_telegram_bot).start()

        # Start Flask app
        flask_app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))

    asyncio.run(main())

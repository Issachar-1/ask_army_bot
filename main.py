from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, ContextTypes

# Your Telegram Bot's API Token
API_TOKEN = '7974234245:AAGGgR3hPKXxqCwtYIVkS5Y_ZuXlsmVwRbY'

# Define the /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message1 = "Hey! Welcome to Ask ARMY."
    welcome_message2 = "Got something on your heart?\nSend your question here anonymously, and we’ll select and address these in our next youth panel or during the youth program."
    
    await update.message.reply_text(welcome_message1)
    await update.message.reply_text(welcome_message2)

# Function to save the question to a text file
def save_question(question: str):
    # Open the file in append mode ('a')
    with open('questions.txt', 'a') as f:
        # Write the question to the file with a newline
        f.write(question + '\n' + "------------" + '\n')

# Define the function for receiving anonymous questions
async def receive_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Get the message text (question)
    question = update.message.text
    # Save the question to the text file (No need to await this)
    save_question(question)
    # Send the acknowledgment response to the user
    await update.message.reply_text("Thank you for sharing. Your question has been received anonymously.")

# Define the main function to set up the bot
def main():
    application = Application.builder().token(API_TOKEN).build()

    # Register the /start command handler
    application.add_handler(CommandHandler("start", start))
    
    # Register the handler for receiving messages (questions)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_question))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
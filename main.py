from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import openai
import os
from dotenv import load_dotenv
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from pymongo import MongoClient
from sms import send_SMS

nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

load_dotenv()

uri = os.getenv("MONGODB")
openai.api_key = os.getenv("OPENAI_API")

client = MongoClient(uri)
db = client['ListnerAI_DB']
collection = db['UserData']

print('Starting up bot...')

TOKEN: Final = os.getenv("TELEGRAM_KEY")
BOT_USERNAME: Final = '@ListnerAI_bot'


ACTIVE = False
chat_log = []


def generate_response(prompt):
    chat_log.append({"role": "user", "content": prompt})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_log,
    )
    message = response['choices'][0]['message']['content'].strip("\n").strip()
    chat_log.append({"role": "assistant", "content": message.strip("\n").strip()})
    return message

data = {'user_id': '', 'Name': '', 'Contact': ''}
# Lets us use the /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    data['user_id'] = user_id
    await update.message.reply_text('''Hello there! I\'m a bot. What\'s your name?
    use /name <your name> to tell me your name''')

async def name_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text: str = update.message.text
    name = text.replace('/name', '').strip()
    data['Name'] = name
    await update.message.reply_text('Hello '+name+'! use /contact<Country code + Phone number> to tell me your closest person\'s contact information')

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text: str = update.message.text
    contact = text.replace('/contact', '').strip()
    data['Contact'] = contact
    await update.message.reply_text('Thank you for your contact information! check the data using /data')    

async def check_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Name: *{data['Name']}*\nContact: *{data['Contact']}* use /yes to upload the data", parse_mode='Markdown')
    print(data['Name'], data['Contact'])

async def upload_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    collection.insert_one(data)
    global ACTIVE
    ACTIVE = True
    await update.message.reply_text('Data uploaded successfully!')

# Lets us use the /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Try typing anything and I will do my best to respond!')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ACTIVE:
        message_type: str = update.message.chat.type
        text: str = update.message.text

        print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

        if message_type == 'group':
            if BOT_USERNAME in text:
                new_text: str = text.replace(BOT_USERNAME, '').strip()
                response: str = generate_response(new_text)
            else:
                return
        else:
            response: str = generate_response(text)   
            sentiment = sia.polarity_scores(text)['compound']
            if sentiment<0:
                send_SMS(data['Contact'])

        print('Bot:', response, sentiment) 
        await update.message.reply_text(response)
    else:
        await update.message.reply_text('Use /start and follow the steps to use the bot!')

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('name', name_command))
    app.add_handler(CommandHandler('contact', contact_command))
    app.add_handler(CommandHandler('data', check_data))
    app.add_handler(CommandHandler('yes', upload_data))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=5)
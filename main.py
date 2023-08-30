from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from pymongo import MongoClient
from Langchain import *
from func import *

nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

load_dotenv()

uri = os.getenv("MONGODB")

client = MongoClient(uri)
db = client['ListnerAI_DB']
collection = db['UserData']

print('Starting up bot...')

TOKEN: Final = os.getenv("TELEGRAM_KEY")
BOT_USERNAME: Final = '@ListnerAI_bot'

user_id = ''

data = {'user_id': '', 'Name': '', 'Contact': ''}

ACTIVE = False

# Lets us use the /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global user_id
    user_id = update.message.from_user.id
    global ACTIVE
    ACTIVE = check_user_exists(user_id)
    if ACTIVE:
        user = collection.find_one({'user_id': user_id})
        data['Name'] = user['Name']
        data['Contact'] = user['Contact']
        text=(f"hi, my name is {data['Name']}")
        response: str = conversation.predict(input=text).strip("\n").strip()
        await update.message.reply_text(response)  
    else:
        data['user_id'] = user_id
        await update.message.reply_text('''Hello there! Before gtting started What\'s your name? use /name <your name> to tell me your name \n Eg: /name ListenerAI_Bot''')

async def name_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text: str = update.message.text
    name = text.replace('/name', '').strip()
    if not is_valid_name(name):
        await update.message.reply_text('Please enter a valid name! use /name <your name> to tell me your name \n Eg: /name ListenerAI_Bot')
    else:
        data['Name'] = name
        await update.message.reply_text('Hello '+name+'! use /contact <Country code + Phone number> to tell me your closest person\'s contact information \n /contact +911234567890')

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text: str = update.message.text
    contact = text.replace('/contact', '').strip()
    if not is_valid_phone_number(contact):
        await update.message.reply_text('Please enter a valid phone number! use /contact <Country code + Phone number> to tell me your closest person\'s contact information \n /contact +911234567890')
    else:
        data['Contact'] = contact
        await update.message.reply_text('Thank you for your contact information! check the data using /data')    

async def check_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Name: *{data['Name']}*\nContact: *{data['Contact']}* use /yes to upload the data or use the previous commands to make changes", parse_mode='Markdown')
    print(data['Name'], data['Contact'])

async def upload_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    collection.insert_one(data)
    global ACTIVE
    ACTIVE = True
    resp=conversation.predict(input=(f"hi, my name is {data['Name']}"))
    await update.message.reply_text('Data uploaded successfully! ' + resp)

# Lets us use the /help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Try typing anything and I will do my best to respond! or use /start')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if ACTIVE:
        message_type: str = update.message.chat.type
        text: str = update.message.text

        print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

        response: str = conversation.predict(input=text).strip("\n").strip()
        sentiment = sia.polarity_scores(text)['compound']
        print('Bot:', response, sentiment) 
        await update.message.reply_text(response)
        if sentiment < -0.3:
            send_SMS(data['Contact'], data['Name'])
    else:
        await update.message.reply_text('Use /start to start the bot')

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
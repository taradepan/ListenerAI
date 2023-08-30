# ListenerAI
The ListnerAI Bot is a Telegram bot that uses OpenAI's GPT-3 to generate responses to user messages. The bot also has a sentiment analysis feature that sends an SMS to a designated contact if the sentiment of the user's message is negative.

The program is written in Python and uses the telegram and pymongo libraries to interact with the Telegram API and MongoDB database, respectively. It also uses the nltk library for sentiment analysis and the Langchain library for generating responses using GPT-3.

The bot supports several commands, including /start, /name, /contact, /data, /yes, and /help. The /start command prompts the user to enter their name and contact information, while the /name and /contact commands allow the user to set their name and contact information, respectively. The /data command displays the user's name and contact information, and the /yes command uploads the user's data to the database. The /help command displays a help message.

When a user sends a message to the bot, the program uses GPT-3 to generate a response. If the sentiment of the user's message is negative, the program sends an SMS to the designated contact with the user's name and message.

The program uses environment variables to store sensitive information such as API keys and database connection strings. These environment variables are loaded using the dotenv library.
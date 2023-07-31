from pymongo import MongoClient
from twilio.rest import Client
import os
from dotenv import load_dotenv
import re

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

# Create a Twilio client
sms = Client(account_sid, auth_token)

def send_SMS(TO):
    message = "Hello from Twilio! sentiment analysis is negative"

    # Send the SMS message
    message = sms.messages.create(
        body=message,
        from_='+17623395521',
        to=TO
    )

    print(message.sid)


uri = os.getenv("MONGODB")
client = MongoClient(uri)
db = client['ListnerAI_DB']
collection = db['UserData']

def check_user_exists(user_id):
    user = collection.find_one({'user_id': user_id})
    if user:
        return True
    else:
        return False
    

def is_valid_phone_number(phone_number):
    pattern = re.compile(r'^\+\d{1,3}\d{10}$')
    match = pattern.match(phone_number)
    if match:
        return True
    else:
        return False
    
def is_valid_name(name):
    if len(name) > 0:
        return True
    else:
        return False
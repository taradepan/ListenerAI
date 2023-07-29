from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

# Your Twilio account SID and auth token
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

# Create a Twilio client
client = Client(account_sid, auth_token)

def send_SMS(TO):
    message = "Hello from Twilio! sentiment analysis is negative"

    # Send the SMS message
    message = client.messages.create(
        body=message,
        from_='+17623395521',
        to=TO
    )

    print(message.sid)

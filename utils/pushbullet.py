# Import the following modules
import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
PUSHBULLET_API_KEY = os.getenv("PUSHBULLET_API_KEY")

# Function to send Push Notification
def pushbullet_notif(title, body):
     # Make a dictionary that includes, title and body
    msg = {"type": "note", "title": title, "body": body}
    # Sent a posts request
    resp = requests.post('https://api.pushbullet.com/v2/pushes',
                         data=json.dumps(msg),
                         headers={'Authorization': 'Bearer ' + PUSHBULLET_API_KEY,
                                  'Content-Type': 'application/json'})
    if resp.status_code != 200:  # Check if fort message send with the help of status code
        raise Exception('Error', resp.status_code)
    else:
        print('Message sent')
 
 

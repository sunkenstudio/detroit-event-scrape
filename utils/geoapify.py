import requests
import time
from dotenv import load_dotenv
import os

load_dotenv()
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY")

def geoapify_batch_request(data):
    headers = {'Content-Type': 'application/json'}
    url = f'https://api.geoapify.com/v1/batch/geocode/search?&apiKey={GEOAPIFY_API_KEY}'
    retrieval_url = ''
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 202:
        print("202 Accepted. Waiting to retrieve...")
        json = response.json()
        retrieval_url = json['url']
        time.sleep(10)
    else:
        return response.json()
    
    if(retrieval_url != ''):
        print(retrieval_url)
        while True:
            response = requests.get(retrieval_url)
            if(response.status_code == 202):
                print('Still Processing. Waiting 60 seconds...')
                time.sleep(60)
            else:
                return response

import json
from dotenv import load_dotenv
import os

ENV = os.getenv("ENV")

def read_json(filename):
    with open(filename) as json_data:
        data = json.load(json_data)
    json_data.close()
    return data

def save_updated_json(new_json, filename):
    with open(filename, 'w') as f:
        json.dump(new_json, f)

def get_base_url():
    if(ENV == 'prod'):
        return 'https://detroiteventmap.com/api'
    return 'http://localhost:5000/api'
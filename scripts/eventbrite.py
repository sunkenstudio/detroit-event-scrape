import requests
from bs4 import BeautifulSoup
import datetime
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()
WORKING_DIRECTORY = os.getenv("WORKING_DIRECTORY")

def get_new_location(link):
    print('sleeping...')
    time.sleep(5)
    page = requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    # Find the address element
    address_element = soup.find('p', class_='location-info__address-text')

    # Extract the address text
    address = address_element.next_sibling.strip()
    return address

def remove_keywords_from_array(array):
    keywords_to_remove = ["Going fast", "Sales end soon", "Almost full" ]
    return [item for item in array if item not in keywords_to_remove]

def read_json(filename):
    with open(filename) as json_data:
        data = json.load(json_data)
    json_data.close()
    return data

def save_updated_json(new_json, filename):
    with open(filename, 'w') as f:
        json.dump(new_json, f)

def scrape_event(item, locations):
    event = {"title":"", "date":"","datetime":"","url":"","img":"", "location":"", "address":"", "price":""}

    details = item.find("section", class_="event-card-details")
    titleBlock = details.find("a", class_="event-card-link")
    title = details.find("h2").text.strip()
    url = titleBlock['href']
    event["title"] = title
    event["url"] = url
    try:
        paragraphs = details.find_all('p')
        with_tags = []
        for p in paragraphs:
            with_tags.append(p.text.strip())
        without_tags = remove_keywords_from_array(with_tags)
        date_time = without_tags[0]
        location = without_tags[1]
        event["datetime"] = date_time
        event["location"] = location
    except:
        print('error with datetime/location')
    
    imageBlock = details.parent.find('img')
    event["img"] = imageBlock['src']

    try:
        location = event["location"]
        event["lat"] = 0
        event["lng"] = 0
        if(location in locations):
            event["address"] = locations[location]["address"]
            if('lat' in locations[location]):
                event["lat"] = locations[location]["lat"]
                event["lng"] = locations[location]["lng"]
        else:
            print('try find new location')
            address = get_new_location(url)
            locations[location] = {"address":address}
            event["address"] = address
    except:
        print("missing location")
    return event

def get_eventbrite_events():
    final = []
    pageCtr = 1
    startDate = datetime.date.today() + datetime.timedelta(days=1)
    endDate = startDate + datetime.timedelta(days=6)
    startDateString = startDate.strftime("%Y-%m-%d")
    endDateString = endDate.strftime("%Y-%m-%d")
    locations = read_json(f'{WORKING_DIRECTORY}/cache/locations.json')

    while(pageCtr < 2):
        URL = f"https://www.eventbrite.com/d/mi--detroit/all-events/?page={str(pageCtr)}&start_date={startDateString}&end_date={endDateString}"
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")
        items = soup.find_all("div",class_="event-card__horizontal")
        if(len(items)>0):
            for item in items:
                event = scrape_event(item, locations)
                final.append(event)
        pageCtr += 1

    save_updated_json(final, f'{WORKING_DIRECTORY}/backups/eventbrite.json')
    return final

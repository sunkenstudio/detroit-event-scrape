import requests
from bs4 import BeautifulSoup
import datetime
import re
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
WORKING_DIRECTORY = os.getenv("WORKING_DIRECTORY")

def get_dates(date_string):
    date_matches = re.findall(r'(?:Jan(?:uary)?\.?|Feb(?:ruary)?\.?|Mar(?:ch)?\.?|Apr(?:il)?\.?|May|Jun(?:e)?\.?|Jul(?:y)?\.?|Aug(?:ust)?\.?|Sep(?:tember)?\.?|Oct(?:ober)?\.?|Nov(?:ember)?\.?|Dec(?:ember)?)\s\d{1,2}', date_string)
    return date_matches

def format_date(month_day):
    month, day = month_day.strip('.').split(' ')
    month_map = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
    if(len(month)>3):
        return f"2024-{str(month_map[month[:3]]).zfill(2)}-{str(day).zfill(2)}"
    return f"2024-{str(month_map[month]).zfill(2)}-{str(day).zfill(2)}"

def read_json(filename):
    with open(filename) as json_data:
        data = json.load(json_data)
    json_data.close()
    return data

def save_updated_json(new_json, filename):
    with open(filename, 'w') as f:
        json.dump(new_json, f)

def get_new_location(location_block):
    link = location_block['href']
    page = requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")
    # easy
    address_section = soup.find('p', class_="fdn-listing-meta-data-address")
    if(address_section):
        address = address_section.text.replace("\n\n"," ").replace("\n"," ").strip()
        return address
    else:
        # hard
        address_block = soup.find('div', class_="pres-LocationListRectangle")
        sub_block = address_block.find('p', class_="fdn-teaser-infoline")
        address = sub_block.find_all('span')[0].text.strip()
        return address

def scrape_event(item, locations):
    event = {"title":"", "date":"","datetime":"","url":"","img":"", "location":"", "address":"", "price":""}
    try:
        titleBlock = item.find("p", class_="fdn-teaser-headline")
        title = titleBlock.text.strip()
        url = titleBlock.find("a")['href']
        event["title"] = title
        event["url"] = url
    except:
        print("missing title")
    try:
        date_time = item.find("p", class_="fdn-teaser-subheadline").text.strip()
        event["datetime"] = date_time
    except:
        print("missing datetime")
    try:
        image_block = item.find("div", class_="fdn-event-search-image-block")
        image_src = image_block.find("img")['src']
        event["img"] = image_src
    except:
        print("missing image")
    try:
        location_block = item.find("a", class_="fdn-event-teaser-location-link")
        location = location_block.text.strip()
        event["location"] = location
        event["lat"] = 0
        event["lng"] = 0
        if(location in locations):
            event["address"] = locations[location]["address"]
            if('lat' in locations[location]):
                event["lat"] = locations[location]["lat"]
                event["lng"] = locations[location]["lng"]
        else:
            print('try find new location')
            address = get_new_location(location_block)
            locations[location] = {"address":address, "lat": 0, "lng": 0}
            event["address"] = address
    except:
        print("missing location")
    try:
        price_block = item.find("div", class_="fdn-pres-details-split")
        price = price_block.find("span").text.strip()
        event["price"] = price
    except:
        print("missing price")
    return event

def get_metrotimes_events():
    final = []
    pageCtr = 1
    startDate = datetime.date.today()
    endDate = startDate + datetime.timedelta(days=9)
    startDateString = startDate.strftime("%Y-%m-%d")
    endDateString = endDate.strftime("%Y-%m-%d")
    locations = read_json(f'{WORKING_DIRECTORY}/cache/locations.json')
        
    while(pageCtr < 99):
        URL = f"https://www.metrotimes.com/detroit/EventSearch?narrowByDate={startDateString}-to-{endDateString}&page={str(pageCtr)}&sortType=date&v=g"
        page = requests.get(URL)

        soup = BeautifulSoup(page.content, "html.parser")

        grid = soup.find('div', class_="search-results")
        items = grid.find_all("div", class_="fdn-pres-item-content")
        if(len(items)>0):
            for item in items:
                event = scrape_event(item, locations)
                if(event["location"] != "" and event["img"] != ""):
                    if('through' in event['datetime'].lower()):
                        final.append({**event, "date": '*'})
                    else:
                        try:
                            dates = get_dates(event['datetime'])
                            for d in dates:
                                date = format_date(d)
                                final.append({**event, "date": date})
                        except:
                            print('failed to parse dates')
                            final.append(event)
        else:
            break
        pageCtr += 1

    save_updated_json(locations, f'{WORKING_DIRECTORY}/cache/locations.json')
    
    return final

    

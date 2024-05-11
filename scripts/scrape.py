#!/Users/danwarrick/Desktop/Projects/scraping/.venv/bin/python3

import requests
from dotenv import load_dotenv
import os
from metrotimes import get_metrotimes_events
from utils.geoapify import geoapify_batch_request
from utils.helpers import read_json, save_updated_json, get_base_url
from utils.pushbullet import pushbullet_notif
from utils.discord import fire_discord_notif

# Load environment variables from .env file
load_dotenv()
WORKING_DIRECTORY = os.getenv("WORKING_DIRECTORY")
APP_API_KEY = os.getenv("APP_API_KEY")
ENV = os.getenv("ENV")

BASE_URL = get_base_url(ENV)

# get metro times events
metro_times = get_metrotimes_events()
# combine events from different sources
events = [*metro_times]
print(f"{len(events)} scraped!")
# check events for missing lat/lng
missing_coords = []
for e in events:
    if e["address"] != "" and e["lat"] == 0:
        # create geoapify body
        missing_coords.append(e["address"])

found_coords = {}
# make geoapify batch request
if len(missing_coords) > 0:
    print("retrieving missing coordinates...")
    # wait for geoapify success
    geoapify_response = geoapify_batch_request(missing_coords)
    json = geoapify_response.json()
    # parse response as object
    for i in json:
        address = i["query"]["text"]
        lat = i["lat"]
        lng = i["lon"]
        found_coords[address] = {"lat": lat, "lng": lng}

    # update locations.json
    locations_cache = read_json(f"{WORKING_DIRECTORY}/cache/locations.json")
    backup = save_updated_json(
        locations_cache, f"{WORKING_DIRECTORY}/backups/locations.json"
    )

    for l in locations_cache.keys():
        address = locations_cache[l]["address"]
        if address in found_coords:
            locations_cache[l]["lat"] = found_coords[address]["lat"]
            locations_cache[l]["lng"] = found_coords[address]["lng"]

    save_updated_json(locations_cache, f"{WORKING_DIRECTORY}/cache/locations.json")

# validate and add lat/lng to events
final = []
success_count = 0
total_count = 0
for e in events:
    if e["address"] != "":
        if e["lat"] == 0:
            final.append({**e, "lat": lat, "lng": lng})
            success_count += 1
        else:
            final.append(e)
            success_count += 1
    total_count += 1

# post events to api
save_updated_json(final, f"{WORKING_DIRECTORY}/backups/events.json")

headers = {"Content-Type": "application/json"}
url = f"{BASE_URL}/api/events"

response = requests.post(
    url, headers=headers, json={"events": final, "token": APP_API_KEY}
)

discord_embed = {
    "title": "Sunday Event Report",
    "description": "Weekly events scrape for Detroit Event Map",
    "color": "e28743",
    "fields": [
        {
            "name": "MetroTimes",
            "inline": False,
        },
        {
            "name": "Total Events",
            "value": str(total_count),
            "inline": True,
        },
        {
            "name": "Events Added",
            "value": str(success_count),
            "inline": True,
        },
        {
            "name": "Success Rate",
            "value": str(success_count / (total_count)),
            "inline": True,
        },
    ],
}

if response.status_code == 201:
    print(f"Success! {len(final)} events added to db!")
    pushbullet_notif("Detroit Event Map", f"Added {len(final)} events to db!")
    fire_discord_notif(discord_embed)
else:
    print("Failed to post to db")
    pushbullet_notif("Detroit Event Map", f"Failed to post to db\n{str(response)}")

from discord_webhook import DiscordWebhook, DiscordEmbed
from dotenv import load_dotenv
import os

load_dotenv()
DISCORD_WEB_HOOK = os.getenv("DISCORD_WEB_HOOK")

# ex:
# values = {
#     "title": "Sunday Event Report",
#     "description": "Weekly events scrape for Detroit Event Map",
#     "color": "e28743",
#     "fields": [
#         {
#             "name": "MetroTimes",
#             "inline": False,
#         },
#         {
#             "name": "Total Events",
#             "value": "100",
#             "inline": True,
#         },
#         {
#             "name": "Events Added",
#             "value": "80",
#             "inline": True,
#         },
#         {
#             "name": "Success Rate",
#             "value": "80%",
#             "inline": True,
#         },
#     ],
# }


def fire_discord_notif(values):
    webhook = DiscordWebhook(url=DISCORD_WEB_HOOK)

    title = values["title"]
    description = values["description"]
    color = values["color"]
    fields = values["fields"]

    # create embed object for webhook
    # you can set the color as a decimal (color=242424) or hex (color="03b2f8") number
    embed = DiscordEmbed(title=title, description=description, color=color)
    embed.set_timestamp()

    for f in fields:
        name = f["name"] if "name" in f else ""
        value = f["value"] if "value" in f else ""
        inline = f["inline"] if "inline" in f else False
        embed.add_embed_field(name=name, value=value, inline=inline)

    # add embed object to webhook
    webhook.add_embed(embed)

    response = webhook.execute()

import os
import discord
import datetime
from dotenv import load_dotenv
from discord.ext import tasks
import requests
from pymongo import MongoClient


def getDailyFracs():
    ID_URL = os.getenv('FRACS_ID_URL')
    achievement_URL = os.getenv('ACHIEVEMENTS_URL')

    dailyFracs = requests.get(url = ID_URL)

    dailyFracsID_JSON = dailyFracs.json()['achievements']
    dailyFracsID_List = list()

    for frac in dailyFracsID_JSON:
        dailyFracsID_List.append(str(frac['id']))

    dailyFracListParams = {'ids': ','.join(dailyFracsID_List)}
    getDailyFracList = requests.get(url = achievement_URL, params = dailyFracListParams)

    dailyFracData = getDailyFracList.json()

    dailyFracNameList = list()

    for frac in dailyFracData:
        dailyFracNameList.append(frac['name'])

    dailyFracNameList.sort()

    return dailyFracNameList

def createDailyFracsEmbed():
    rec_fracs_emoji = client.get_emoji(1283656710493437993)
    t1_fracs_emoji = client.get_emoji(1283656743192363028)
    t2_fracs_emoji = client.get_emoji(1283656796237729876)
    t3_fracs_emoji = client.get_emoji(1283656632932368427)
    t4_fracs_emoji = client.get_emoji(1283656775295565906)

    dailyFracNameList = getDailyFracs()

    fracs_embed_dict = {
        "title": "Daily Fractals",
        "color": 6042258
    }

    fracs_embed = discord.Embed.from_dict(fracs_embed_dict)
    fracs_embed.add_field(name="Recommended Fractals", value=f"{rec_fracs_emoji} {dailyFracNameList[0]}\n{rec_fracs_emoji} {dailyFracNameList[1]}\n{rec_fracs_emoji} {dailyFracNameList[2]}")
    fracs_embed.add_field(name="Tier 1 Fractals", value=f"{t1_fracs_emoji} {dailyFracNameList[3]}\n{t1_fracs_emoji} {dailyFracNameList[4]}\n{t1_fracs_emoji} {dailyFracNameList[5]}")
    fracs_embed.add_field(name="Tier 2 Fractals", value=f"{t2_fracs_emoji} {dailyFracNameList[6]}\n{t2_fracs_emoji} {dailyFracNameList[7]}\n{t2_fracs_emoji} {dailyFracNameList[8]}")
    fracs_embed.add_field(name="Tier 3 Fractals", value=f"{t3_fracs_emoji} {dailyFracNameList[9]}\n{t3_fracs_emoji} {dailyFracNameList[10]}\n{t3_fracs_emoji} {dailyFracNameList[11]}")
    fracs_embed.add_field(name="Tier 4 Fractals", value=f"{t4_fracs_emoji} {dailyFracNameList[12]}\n{t4_fracs_emoji} {dailyFracNameList[13]}\n{t4_fracs_emoji} {dailyFracNameList[14]}")

    return fracs_embed

def getDailyStrikes():
    ID_URL = os.getenv('STRIKES_ID_URL')
    achievement_URL = os.getenv('ACHIEVEMENTS_URL')

    dailyStrikes = requests.get(url = ID_URL)

    dailyStrikesID_JSON = dailyStrikes.json()['achievements']

    dailyStrikeID_List = list()

    for strike in dailyStrikesID_JSON:
        dailyStrikeID_List.append(str(strike['id']))

    dailyStrikeListParams = {'ids': ','.join(dailyStrikeID_List)}
    getDailyStrikeList = requests.get(url = achievement_URL, params = dailyStrikeListParams)

    dailyStrikeData = getDailyStrikeList.json()

    dailyStrikeNameList = list()

    for strike in dailyStrikeData:
        dailyStrikeNameList.append(strike['name'])

    dailyStrikeNameList.sort()

    return dailyStrikeNameList

def createDailyStrikesEmbed():
    IBS_strikes_emoji = client.get_emoji(1283718624166547496)
    EOD_strikes_emoji = client.get_emoji(1283718838059274283)
    SOTO_strikes_emoji = client.get_emoji(1283718871043538984)

    dailyStrikeNameList = getDailyStrikes()

    strikes_embed_dict = {
        "title" : "Daily Strikes",
        "color" : 3426448
    }

    strikes_embed = discord.Embed.from_dict(strikes_embed_dict)
    strikes_embed.add_field(name = "IBS Strike", value = f"{IBS_strikes_emoji} {dailyStrikeNameList[2]}")
    strikes_embed.add_field(name = "EOD Strike", value = f"{EOD_strikes_emoji} {dailyStrikeNameList[0]}")
    strikes_embed.add_field(name = "SOTO Strike", value = f"{SOTO_strikes_emoji} {dailyStrikeNameList[1]}")

    return strikes_embed

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
RESET_HOUR = int(os.getenv('RESET_HOUR'))
RESET_MINUTE = int(os.getenv('RESET_MINUTE'))
RESET_SECOND = int(os.getenv('RESET_SECOND'))

intents = discord.Intents.default()
client = discord.Client(intents = intents)

sendEmbedsTime = datetime.time(hour=RESET_HOUR, minute=RESET_MINUTE, second=RESET_SECOND, tzinfo=datetime.timezone.utc)

@tasks.loop(time=sendEmbedsTime)
async def sendEmbeds():
    channelList = list()

    for guild in client.guilds:
        for channel in guild.text_channels:
            if(channel.name == "gw2-daily"):
                channelList.append(channel)
                break
    
    fracs_embed = createDailyFracsEmbed()
    strikes_embed = createDailyStrikesEmbed()

    for channel in channelList:
        await channel.send(embed=fracs_embed)
        await channel.send(embed=strikes_embed)

@client.event
async def on_ready():
    if not sendEmbeds.is_running():
        sendEmbeds.start()

client.run(TOKEN)
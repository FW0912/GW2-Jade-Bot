import os
import discord
import datetime
from dotenv import load_dotenv
from discord.ext import commands, tasks
import requests
from database import insertKey, getKey, updateKey, deleteKey

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
RESET_HOUR = int(os.getenv('RESET_HOUR'))
RESET_MINUTE = int(os.getenv('RESET_MINUTE'))
RESET_SECOND = int(os.getenv('RESET_SECOND'))

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents = intents)

def getDailyFracs():
    ID_URL = os.getenv('FRACS_ID_URL')
    ACHIEVEMENTS_URL = os.getenv('ACHIEVEMENTS_URL')

    dailyFracs = requests.get(url = ID_URL)

    dailyFracsID_JSON = dailyFracs.json()['achievements']
    dailyFracsID_List = list()

    for frac in dailyFracsID_JSON:
        dailyFracsID_List.append(str(frac['id']))

    dailyFracListParams = {'ids': ','.join(dailyFracsID_List)}
    getDailyFracList = requests.get(url = ACHIEVEMENTS_URL, params = dailyFracListParams)

    dailyFracData = getDailyFracList.json()

    dailyFracNameList = list()

    for frac in dailyFracData:
        dailyFracNameList.append(frac['name'])

    dailyFracNameList.sort()

    return dailyFracNameList

def createDailyFracsEmbed():
    rec_fracs_emoji = bot.get_emoji(1283656710493437993)
    t1_fracs_emoji = bot.get_emoji(1283656743192363028)
    t2_fracs_emoji = bot.get_emoji(1283656796237729876)
    t3_fracs_emoji = bot.get_emoji(1283656632932368427)
    t4_fracs_emoji = bot.get_emoji(1283656775295565906)

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
    ACHIEVEMENTS_URL = os.getenv('ACHIEVEMENTS_URL')

    dailyStrikes = requests.get(url = ID_URL)

    dailyStrikesID_JSON = dailyStrikes.json()['achievements']

    dailyStrikeID_List = list()

    for strike in dailyStrikesID_JSON:
        dailyStrikeID_List.append(str(strike['id']))

    dailyStrikeListParams = {'ids': ','.join(dailyStrikeID_List)}
    getDailyStrikeList = requests.get(url = ACHIEVEMENTS_URL, params = dailyStrikeListParams)

    dailyStrikeData = getDailyStrikeList.json()

    dailyStrikeNameList = list()

    for strike in dailyStrikeData:
        dailyStrikeNameList.append(strike['name'])

    dailyStrikeNameList.sort()

    return dailyStrikeNameList

def createDailyStrikesEmbed():
    IBS_strikes_emoji = bot.get_emoji(1283718624166547496)
    EOD_strikes_emoji = bot.get_emoji(1283718838059274283)
    SOTO_strikes_emoji = bot.get_emoji(1283718871043538984)

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

async def validateKey(accountAchievements_JSON, interaction : discord.Interaction):
    if 'text' in accountAchievements_JSON:
        if(accountAchievements_JSON['text'] == 'Invalid access token'):
            await interaction.response.send_message("API key is invalid! Please try again.")
            return False

        if(accountAchievements_JSON['text'] == 'requires scope progression'):
            await interaction.response.send_message("API key requires 'progression' checked!")
            return False
    
    return 

sendDailyTime = datetime.time(hour=RESET_HOUR, minute=RESET_MINUTE, second=RESET_SECOND, tzinfo=datetime.timezone.utc)

@tasks.loop(time=sendDailyTime)
async def sendDaily():
    dailyChannelList = list()

    for guild in bot.guilds:
        for channel in guild.text_channels:
            if(channel.name == "gw2-daily"):
                dailyChannelList.append(channel)
                break
    
    fracs_embed = createDailyFracsEmbed()
    strikes_embed = createDailyStrikesEmbed()

    for channel in dailyChannelList:
        await channel.send(embed=fracs_embed)
        await channel.send(embed=strikes_embed)

@bot.tree.command(name = "upload-api-key", description = "Upload your GW2 API Key (requires 'progression')")
async def upload_key_command(interaction : discord.Interaction, api_key : str):
    if isinstance(interaction.channel, discord.channel.DMChannel):
        userID = interaction.user.id
        ACCOUNT_ACHIEVEMENTS_URL = os.getenv('ACCOUNT_ACHIEVEMENTS_URL')
        DUPLICATE_KEY_MESSAGE = "API key is already registered! If you would like to update or delete your API key, please use /update-api-key [new-api-key] or /delete-api-key."
        
        accountAchievementParams = {
            'access_token' : api_key
        }

        accountAchievements = requests.get(url = ACCOUNT_ACHIEVEMENTS_URL, params = accountAchievementParams)

        accountAchievements_JSON = accountAchievements.json()

        if(await validateKey(accountAchievements_JSON = accountAchievements_JSON, interaction = interaction) == False):
            return
            
        await interaction.response.defer()

        if(await getKey(userID = userID) != None):
            await interaction.followup.send(DUPLICATE_KEY_MESSAGE)
            return

        await insertKey(userID = userID, api_key = api_key)
        await interaction.followup.send("API key has been successfully registered.")

    else:
        await interaction.response.send_message("Upload your API key by direct message.")

@bot.tree.command(name = "update-api-key", description = "Update your registered GW2 API Key (requires 'progression')")
async def update_key_command(interaction : discord.Interaction, new_api_key : str):
    if isinstance(interaction.channel, discord.channel.DMChannel):
        userID = interaction.user.id
        ACCOUNT_ACHIEVEMENTS_URL = os.getenv('ACCOUNT_ACHIEVEMENTS_URL')
        NO_REGISTERED_KEY_MESSAGE = "There is no API key registered, please use the command /upload-api-key [api-key] to register your API key."

        accountAchievementParams = {
            'access_token' : new_api_key
        }

        accountAchievements = requests.get(url = ACCOUNT_ACHIEVEMENTS_URL, params = accountAchievementParams)

        accountAchievements_JSON = accountAchievements.json()

        if(await validateKey(accountAchievements_JSON = accountAchievements_JSON, interaction = interaction) == False):
            return
            
        await interaction.response.defer()

        if(await getKey(userID = userID) == None):
            await interaction.followup.send(NO_REGISTERED_KEY_MESSAGE)
            return

        await updateKey(userID = userID, new_api_key = new_api_key)
        await interaction.followup.send("API key has been successfully updated.")

    else:
        await interaction.response.send_message("Update your API key by direct message.")

@bot.tree.command(name = "delete-api-key", description = "Delete your registered GW2 API Key")
async def delete_key_command(interaction : discord.Interaction):
    def check(message):
        return message.author == interaction.user
    
    if isinstance(interaction.channel, discord.channel.DMChannel):
        userID = interaction.user.id
        
        if(await getKey(userID = userID) == None):
            await interaction.response.send_message("You have no registered API key!")
            return
        
        await interaction.response.send_message("Are you sure? (y/n)")

        try:
            response = await bot.wait_for('message', check = check, timeout = 30.0)
        except TimeoutError:
            return
        
        if(response.content != 'y' and response.content != 'n'):
            await interaction.followup.send("Unknown command, please use (y/n).")
            return

        if(response.content == 'n'):
            await interaction.followup.send("Deletion cancelled successfully.")
            return
        
        await deleteKey(userID = userID)
        await interaction.followup.send("Registered API key deleted successfully.")

    else:
        await interaction.response.send_message("Delete your API key by direct message.")

@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Commands synced")
    
    if not sendDaily.is_running():
        sendDaily.start()

bot.run(TOKEN)
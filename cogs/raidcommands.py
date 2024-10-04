import discord
import os
from dotenv import load_dotenv
import requests
from discord import app_commands
from discord.ext import commands
from database import insertKey, getKey, updateKey, deleteKey

class raidCommands(commands.Cog):
    def __init__(self, bot : commands.Bot):
        self.bot = bot
        load_dotenv()

    def getWings():
        RAIDS_URL = os.getenv('RAIDS_URL')

        raids = requests.get(url = RAIDS_URL)
        raidsID_JSON = raids.json()

        wingList = list()

        for raid in raidsID_JSON:
            raidDetails = requests.get(url = f"{RAIDS_URL}/{raid}")
            raidDetails_JSON = raidDetails.json()

            for wing in raidDetails_JSON['wings']:
                wingList.append(wing)

        return wingList
    
    def formatToEmbedOutput(id):
        return str(id).replace('_', ' ').title()

    def createWeeklyRaidsEmbed(self, accountRaids_JSON):
        wingList = raidCommands.getWings()
        
        raid_emoji = self.bot.get_emoji(1291838274997977188)
        cross_emoji = self.bot.get_emoji(1291819942521470996)
        cross_raid_emoji = self.bot.get_emoji(1291841383270977566)
        checkmark_emoji = self.bot.get_emoji(1291819916735021067)
        checkmark_raid_emoji = self.bot.get_emoji(1291840902612127786)

        raids_embed_dict = {
            "title" : f"Weekly Raid Clears {raid_emoji}",
            "color" : 7152162
        }

        raids_embed = discord.Embed.from_dict(raids_embed_dict)

        wingCount = 1

        for wing in wingList:
            fullClearFlag = True
            clearList = list()

            for event in wing['events']:
                if(event['id'] in accountRaids_JSON):
                    clearList.append(event['id'])
                else:
                    fullClearFlag = False

            embedValue = ""

            for event in wing['events']:
                if(event['id'] not in clearList):
                    embedValue = "{curr}{event_id} {cross_emoji}\n".format(curr = embedValue, event_id = raidCommands.formatToEmbedOutput(event['id']), cross_emoji = cross_emoji)
                else:
                    embedValue = "{curr}{event_id} {checkmark_emoji}\n".format(curr = embedValue, event_id = raidCommands.formatToEmbedOutput(event['id']), checkmark_emoji = checkmark_emoji)

            if(fullClearFlag == False):
                raids_embed.add_field(name = f"W{wingCount} : {raidCommands.formatToEmbedOutput(wing['id'])} {cross_raid_emoji}", value = embedValue, inline = False)
            else:
                raids_embed.add_field(name = f"W{wingCount} : {raidCommands.formatToEmbedOutput(wing['id'])} {checkmark_raid_emoji}", value = embedValue, inline = False)

            wingCount += 1

        return raids_embed

    @app_commands.command(name = "weekly-raids", description = "Check your weekly raid clears")
    async def checkWeeklyRaidsCommand(self, interaction : discord.Interaction):
        await interaction.response.defer()

        userID = interaction.user.id
        apiKey = await getKey(userID = userID)

        if(apiKey == None):
            await interaction.followup.send("You have no registered API key!")
            return

        ACCOUNT_RAIDS_URL = os.getenv('ACCOUNT_RAIDS_URL')

        accountRaids_params = {
            'access_token' : apiKey
        }

        accountRaids = requests.get(url = ACCOUNT_RAIDS_URL, params = accountRaids_params)
        accountRaids_JSON = accountRaids.json()

        raid_embed = raidCommands.createWeeklyRaidsEmbed(self = self, accountRaids_JSON = accountRaids_JSON)
        
        await interaction.followup.send(embed = raid_embed)
        
async def setup(bot : commands.Bot):
    await bot.add_cog(raidCommands(bot))
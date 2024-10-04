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

    @app_commands.command(name = "weekly-raids", description = "Check your weekly raid clears")
    async def checkWeeklyRaidsCommand(self, interaction : discord.Interaction):
        await interaction.response.defer()

        userID = interaction.user.id
        apiKey = await getKey(userID = userID)

        if(apiKey == None):
            await interaction.followup.send("You have no registered API key!")
            return

        RAIDS_URL = os.getenv('RAIDS_URL')

        raids_params = {
            'access_token' : apiKey
        }

        raids = requests.get(url = RAIDS_URL, params = raids_params)
        raids_JSON = raids.json()

        

        print(raids_JSON)


    
async def setup(bot : commands.Bot):
    await bot.add_cog(raidCommands(bot))
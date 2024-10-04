import discord
import os
from dotenv import load_dotenv
import requests
from discord import app_commands
from discord.ext import commands
from database import insertKey, getKey, updateKey, deleteKey

class apiKeyCommands(commands.Cog):
    def __init__(self, bot : commands.Bot):
        self.bot = bot
        load_dotenv()

    async def validateKey(accountAchievements_JSON, interaction : discord.Interaction):
        if 'text' in accountAchievements_JSON:
            if(accountAchievements_JSON['text'] == 'Invalid access token'):
                await interaction.response.send_message("API key is invalid! Please try again.")
                return False

            if(accountAchievements_JSON['text'] == 'requires scope progression'):
                await interaction.response.send_message("API key requires 'progression' checked!")
                return False
        
        return True

    async def checkRegisteredKey(userID, interaction : discord.Interaction):
        NO_REGISTERED_KEY_MESSAGE = "There is no API key registered, please use the command /upload-api-key [api-key] to register your API key."

        if(await getKey(userID = userID) == None):
            await interaction.response.send_message(NO_REGISTERED_KEY_MESSAGE)
            return False
        
        return True

    @app_commands.command(name="upload-api-key", description = "Upload your GW2 API Key (requires 'progression')")
    async def upload_key_command(self, interaction : discord.Interaction, api_key : str):
        if isinstance(interaction.channel, discord.channel.DMChannel):
            await interaction.response.defer()
            
            userID = interaction.user.id
            ACCOUNT_ACHIEVEMENTS_URL = os.getenv('ACCOUNT_ACHIEVEMENTS_URL')
            DUPLICATE_KEY_MESSAGE = "API key is already registered! If you would like to update or delete your API key, please use /update-api-key [new-api-key] or /delete-api-key."
            
            accountAchievementParams = {
                'access_token' : api_key
            }

            accountAchievements = requests.get(url = ACCOUNT_ACHIEVEMENTS_URL, params = accountAchievementParams)

            accountAchievements_JSON = accountAchievements.json()

            if(await apiKeyCommands.validateKey(accountAchievements_JSON = accountAchievements_JSON, interaction = interaction) == False):
                return

            if(await getKey(userID = userID) != None):
                await interaction.followup.send(DUPLICATE_KEY_MESSAGE)
                return

            await insertKey(userID = userID, api_key = api_key)
            await interaction.followup.send("API key has been successfully registered.")

        else:
            await interaction.response.send_message("Upload your API key by direct message.")

    @app_commands.command(name = "update-api-key", description = "Update your registered GW2 API Key (requires 'progression')")
    async def update_key_command(self, interaction : discord.Interaction, new_api_key : str):
        if isinstance(interaction.channel, discord.channel.DMChannel):
            await interaction.response.defer()

            userID = interaction.user.id
            ACCOUNT_ACHIEVEMENTS_URL = os.getenv('ACCOUNT_ACHIEVEMENTS_URL')

            accountAchievementParams = {
                'access_token' : new_api_key
            }

            accountAchievements = requests.get(url = ACCOUNT_ACHIEVEMENTS_URL, params = accountAchievementParams)

            accountAchievements_JSON = accountAchievements.json()

            if(await apiKeyCommands.validateKey(accountAchievements_JSON = accountAchievements_JSON, interaction = interaction) == False):
                return

            if(await apiKeyCommands.checkRegisteredKey(userID = userID, interaction = interaction) == False):
                return

            await updateKey(userID = userID, new_api_key = new_api_key)
            await interaction.followup.send("API key has been successfully updated.")

        else:
            await interaction.response.send_message("Update your API key by direct message.")

    @app_commands.command(name = "delete-api-key", description = "Delete your registered GW2 API Key")
    async def delete_key_command(self, interaction : discord.Interaction):
        def check(message):
            return message.author == interaction.user
        
        if isinstance(interaction.channel, discord.channel.DMChannel):
            userID = interaction.user.id
            
            if(await apiKeyCommands.checkRegisteredKey(userID = userID, interaction = interaction) == False):
                return
            
            await interaction.response.send_message("Are you sure? (y/n)")

            try:
                response = await apiKeyCommands.bot.wait_for('message', check = check, timeout = 30.0)
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

async def setup(bot : commands.Bot):
    await bot.add_cog(apiKeyCommands(bot))
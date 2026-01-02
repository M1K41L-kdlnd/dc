import discord
from discord.ext import commands
from google import genai
import os
from dotenv import load_dotenv

# Load your API keys from a .env file or environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Initialize the Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)

# Discord Bot Setup
intents = discord.Intents.default()
intents.message_content = True  # Required to read messages
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print("Logged in as {0.user}".format(bot))

@bot.event
async def on_message(message):
    # Don't let the bot respond to itself
    if message.author == bot.user:
        return

    # Check if the bot is mentioned or if it's a DM
    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        # Remove the mention from the prompt for cleaner input
        clean_content = message.content.replace("<@{0}>".format(bot.user.id), "").strip()
        
        if not clean_content:
            await message.reply("How can I help you today?")
            return

        async with message.channel.typing():
            try:
                # Generate response from Gemini
                response = client.models.generate_content(
                    model="models/gemini-1.5-flash", 
                    contents=clean_content
                )
                
                # Discord has a 2000 character limit per message
                ai_response = response.text
                if len(ai_response) > 2000:
                    ai_response = "{0}... (response truncated)".format(ai_response[:1950])
                
                await message.reply(ai_response)
            except Exception as e:
                await message.reply("Sorry, I ran into an error: {0}".format(e))

    await bot.process_commands(message)

bot.run(DISCORD_TOKEN)
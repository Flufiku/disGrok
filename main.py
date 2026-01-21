import discord
from openrouter import OpenRouter
from dotenv import load_dotenv
import os
import json
from helpers import split_send

load_dotenv()


with open("config.json", "r") as f:
    config = json.load(f)


openrouter_client = OpenRouter(
    api_key=os.getenv("HACKCLUB_AI_API_KEY"),
    server_url=config["server_url"],
)





intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith(f"<@{client.user.id}>"):
        
        content = message.content.split(f"<@{client.user.id}>",1)[1]
        
        messages = []
        if config.get("system_prompt"):
            messages.append({"role": "system", "content": config["system_prompt"]})
        messages.append({"role": "user", "content": content})
        
        response = openrouter_client.chat.send(
            model=config["model"],
            messages=messages
        )
        
        await split_send(message.channel, response.choices[0].message.content)
        return
    
    
if __name__ == '__main__':
    client.run(os.getenv("DISCORD_BOT_TOKEN"))
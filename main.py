import discord
from openrouter import OpenRouter
from dotenv import load_dotenv
import os

load_dotenv()

openrouter_client = OpenRouter(
    api_key=os.getenv("HACKCLUB_AI_API_KEY"),
    server_url="https://ai.hackclub.com/proxy/v1",
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
        
        content = message.content.split(f"<@{client.user.id}> ",1)[1]
        response = openrouter_client.chat.send(
            model="qwen/qwen3-32b",
            messages=[
                {"role": "user", "content": content}
            ]
        )
        
        await message.channel.send(response.choices[0].message.content[0:2000])
        return



if __name__ == '__main__':
    client.run(os.getenv("DISCORD_BOT_TOKEN"))
import discord
from dotenv import load_dotenv
import os
import json
import asyncio
from helpers import *
load_dotenv()


with open("config.json", "r") as f:
    config = json.load(f)


RESPONSES_URL = f"{config['server_url'].rstrip('/')}/responses"




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
        
        content = message.content.split(f"<@{client.user.id}>",1)[1].strip()
        
        msg_context_length = config.get("msg_context_length", 5)
        context = await fetch_context_messages(message.channel, msg_context_length, message.id)
        
        user_content = ""
        if context:
            user_content = f"Previous context in chronological order (newest last):\n{context}\n\n"
        
        user_content += f"User message:\n{message.author.name}:{content}\n\n"

        if message.reference and message.reference.message_id:
            try:
                replied = message.reference.resolved
                if replied is None:
                    replied = await message.fetch_reference()
                    
                user_content += f"Replied to message:\n{replied.author.name}:{replied.content}\n\n"
            
            except discord.NotFound:
                pass
        

        main_messages = []
        
        if config.get("main_system_prompt"):
            main_messages.append(make_user_message(config["main_system_prompt"]))
                    
        main_messages.append(make_user_message(user_content))
        
        
                
        web_messages = []
        
        if config.get("web_system_prompt"):
            web_messages.append(make_user_message(config["web_system_prompt"]))
            
        web_messages.append(make_user_message(user_content))

        
        image_results = []
        try:
            # Run synchronous API call in executor to avoid blocking event loop
            loop = asyncio.get_event_loop()
            web_response = await loop.run_in_executor(
                None,
                lambda: send_responses_request(
                    RESPONSES_URL,
                    os.getenv("HACKCLUB_AI_API_KEY"),
                    config["web_model"],
                    web_messages,
                )
            )
            
            web_response_content = parse_response_text(web_response)
            search_query, news_query, image_query = get_search_queries(web_response_content)
            
            all_search_results = ""
            if search_query:
                search_results = get_search_results(os.getenv("HACKCLUB_SEARCH_API_KEY"), search_query, num_results=5)
                if search_results != []:
                    all_search_results += "General Search Results:\n"
                    for idx, res in enumerate(search_results):
                        all_search_results += f"{idx+1}. {res}\n"
            
            if news_query:
                news_results = get_news_results(os.getenv("HACKCLUB_SEARCH_API_KEY"), news_query, num_results=5)
                if news_results != []:
                    all_search_results += "\nNews Search Results:\n"
                    for idx, res in enumerate(news_results):
                        all_search_results += f"{idx+1}. {res}\n"
        
            if image_query:
                image_results = get_image_results(os.getenv("HACKCLUB_SEARCH_API_KEY"), image_query, num_results=1)
            
            if all_search_results:
                main_messages.append(make_user_message(f"Web Search Results:\n{all_search_results}"))
        except Exception as e:
            print(f"Error during web search: {e}")
        
        try:
            # Run synchronous API call in executor to avoid blocking event loop
            loop = asyncio.get_event_loop()
            main_response = await loop.run_in_executor(
                None,
                lambda: send_responses_request(
                    RESPONSES_URL,
                    os.getenv("HACKCLUB_AI_API_KEY"),
                    config["main_model"],
                    main_messages,
                )
            )

            main_response_content = parse_response_text(main_response)
            if image_results != []:
                main_response_content += "\n\n"
                for idx, img_url in enumerate(image_results):
                    main_response_content += f"{img_url}\n"


            await split_send(message.channel, main_response_content)
        except Exception as e:
            print(f"Error during main response generation: {e}")
            
            await split_send(message.channel, ":x: Sorry, I encountered an error while trying to process your request. Please try again later.")
        return
    
    
if __name__ == '__main__':
    client.run(os.getenv("DISCORD_BOT_TOKEN"))
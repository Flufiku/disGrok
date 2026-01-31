import requests

async def split_send(channel, message):
    message_max_length = 2000
    
    messages = []
    
    while len(message) > message_max_length:
        
        snippet = message[0:message_max_length]
        split_snippet = snippet.split("\n")
        remaining = '\n'.join(split_snippet[0:-1]) if len(split_snippet) > 1 else snippet
        return_snippet = ''.join(split_snippet[-1:]) if len(split_snippet) > 1 else ''

        messages.append(remaining)
        message = return_snippet + message[message_max_length:]
        
    messages.append(message)

    for msg in messages:
        if msg:
            await channel.send(msg)



async def fetch_context_messages(channel, msg_context_length, exclude_message_id):
    context_messages = []
    
    async for msg in channel.history(limit=msg_context_length + 1):
        if msg.id != exclude_message_id:
            context_messages.insert(0, msg)
    
    # Build context string from messages
    context = ""
    for msg in context_messages:
        context += f"{msg.author.name}: {msg.content}\n"
    
    return context




def get_search_queries(web_response):
    lines = web_response.strip().split("\n")
    general_query = ""
    news_query = ""
    
    for line in lines:
        if line.startswith("General Query:"):
            general_query = line.replace("General Query:", "").strip()
            if general_query.lower() == "none":
                general_query = ""
        elif line.startswith("News Query:"):
            news_query = line.replace("News Query:", "").strip()
            if news_query.lower() == "none":
                news_query = ""
        elif line.startswith("Image Query:"):
            image_query = line.replace("Image Query:", "").strip()
            if image_query.lower() == "none":
                image_query = ""
    
    return general_query, news_query, image_query



def get_search_results(api_key, query, num_results=5, safesearch='off'):
    if not query:
        return []
    
    try:
        response = requests.get(
            'https://search.hackclub.com/res/v1/web/search',
            params={'q': query, 'count': num_results, 'safesearch': safesearch},
            headers={'Authorization': f'Bearer {api_key}'}
        )
        response.raise_for_status()
        data = response.json()
        
        results = []
        if 'web' in data and 'results' in data['web']:
            for result in data['web']['results']:
                title = result.get('title', 'No title')
                hostname = result.get('meta_url', {}).get('hostname', 'No URL')
                description = result.get('description', '')
                results.append(f"{title}\n{hostname}\n{description}")
        
        return results
    except Exception as e:
        print(f"Error fetching search results: {e}")
        return []
    

def get_news_results(api_key, query, num_results=5, safesearch='off'):
    if not query:
        return []
    
    try:
        response = requests.get(
            'https://search.hackclub.com/res/v1/news/search',
            params={'q': query, 'count': num_results, 'safesearch': safesearch},
            headers={'Authorization': f'Bearer {api_key}'}
        )
        response.raise_for_status()
        data = response.json()
        
        results = []
        if 'results' in data:
            for result in data['results']:
                title = result.get('title', 'No title')
                hostname = result.get('meta_url', {}).get('hostname', 'No URL')
                description = result.get('description', '')
                age = result.get('age', '')
                results.append(f"{title} ({age})\n{hostname}\n{description}")
        
        return results
    except Exception as e:
        print(f"Error fetching news results: {e}")
        return [] 
    
    
def get_image_results(api_key, query, num_results=1, safesearch='off'):
    if not query:
        return []
    
    try:
        response = requests.get(
            'https://search.hackclub.com/res/v1/images/search',
            params={'q': query, 'count': num_results, 'safesearch': safesearch},
            headers={'Authorization': f'Bearer {api_key}'}
        )
        response.raise_for_status()
        data = response.json()
        
        results = []
        if 'results' in data:
            for result in data['results']:
                image_url = result.get('properties', {}).get('url', '')
                if image_url:
                    results.append(image_url)
        
        return results
    except Exception as e:
        print(f"Error fetching image results: {e}")
        return []
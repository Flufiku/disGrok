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
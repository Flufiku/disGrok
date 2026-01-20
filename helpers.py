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
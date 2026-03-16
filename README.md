# disGrok

**IMPORTANT: This version is made for an online demo on a cheap VPS. Since AI Voice generation runs locally and takes significant resources, it has been limited to 140 characters per prompt, and 3 prompts per user per day.**


A Discord Bot that acts like the Grok Twitter Bot and can answer questions based on recent messages. It can also search the web for information, provide summaries, and send voice messages.



## How to use the Bot:

Image Generation: 
* Use the `/gen_image` command and write your prompt into the `Prompt`-Field

Voice Generations: 
* Use the `/tts` command, choose from the available voices in the `Voice`-Field and write your prompt into the `Prompt`-Field
* Use the `/voice_clone` command, upload a voice sample in the `audio_sample`-Field and and write your prompt into the `Prompt`-Field

Text Generation:
* Just @ mention the bot. It will reply to your message.



## Install Guide

### 0. Create a Discord Bot
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications) and create a new application.
2. Navigate to the "Bot" tab and click "Add Bot".
3. Copy the bot token and save it for later.
4. Under "OAuth2" > "URL Generator", select these scopes:
	- `bot`
	- `applications.commands`
5. In the same "URL Generator" section, select these Bot Permissions:
	- View Channels
	- Send Messages
	- Read Message History
6. In the "Bot" tab, enable the **Message Content Intent**.
7. Copy the generated URL and use it to invite the bot to your Discord server.


### 1. Install PyTorch with CUDA Support
If you have an NVIDIA GPU with CUDA support:
```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

### 2. Install Python Dependencies
```bash
pip3 install -r requirements.txt
```

### 3. Configuration
Create a `.env` file with your API keys:
* HACKCLUB_AI_API_KEY
* HACKCLUB_SEARCH_API_KEY
* DISCORD_BOT_TOKEN

### 4. Run the Bot
```bash
python3 main.py
```
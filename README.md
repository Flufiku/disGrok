# disGrok
A Discord Bot that acts like the Grok Twitter Bot and can answer questions based on recent messages.




## Install Guide

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
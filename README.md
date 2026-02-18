# disGrok
A Discord Bot that acts like the Grok Twitter Bot and can answer questions based on recent messages.




## Install Guide

### 1. Install PyTorch with CUDA Support
If you have an NVIDIA GPU with CUDA support:
```bash
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
```

### 2. Install Flash Attention 2 (Optional but Recommended)
For faster inference on NVIDIA GPUs:

**Windows:**
```bash
pip3 install flash-attn --no-build-isolation
```

If you have limited RAM (< 96GB) and many CPU cores:
```bash
set MAX_JOBS=4
pip3 install flash-attn --no-build-isolation
```

**Note:** Flash Attention requires:
- NVIDIA GPU with compute capability ≥ 8.0 (Ampere or newer: RTX 30xx, RTX 40xx, A100, etc.)
- CUDA Toolkit installed
- Visual Studio Build Tools (Windows) or GCC (Linux)

If installation fails, the bot will fall back to regular PyTorch attention (slower but functional).

### 3. Install SoX (Optional)
SoX is used for audio processing. If not installed, you may see a warning but the bot will still work.

**Windows:**
- Download from: http://sox.sourceforge.net/
- Install and add to PATH environment variable

**Linux:**
```bash
sudo apt-get install sox libsox-fmt-all
```

### 4. Install Python Dependencies
```bash
pip3 install -r requirements.txt
```

### 5. Configuration
Create a `.env` file with your API keys:
* HACKCLUB_AI_API_KEY
* HACKCLUB_SEARCH_API_KEY
* DISCORD_BOT_TOKEN
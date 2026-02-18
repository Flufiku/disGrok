import asyncio
import base64
import io
import os
import requests
import discord
from discord import app_commands


def _send_image_generation_request(chat_url, api_key, model, prompt, aspect_ratio=None):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "modalities": ["image", "text"],
        "stream": False,
    }
    if aspect_ratio:
        payload["image_config"] = {"aspect_ratio": aspect_ratio}

    response = requests.post(chat_url, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def _parse_image_response(data):
    choices = data.get("choices", [])
    if not choices:
        return None, ""

    message = choices[0].get("message", {})
    content = message.get("content", "")
    images = message.get("images", [])
    if not images:
        return None, content

    image_url = images[0].get("image_url", {}).get("url", "")
    return image_url or None, content


def _data_url_to_bytes(data_url):
    if not data_url.startswith("data:"):
        raise ValueError("Image URL is not a data URL")

    header, encoded = data_url.split(",", 1)
    if ";base64" not in header:
        raise ValueError("Image data URL is not base64 encoded")

    return base64.b64decode(encoded)


def setup_image_commands(tree, config):
    chat_url = f"{config['server_url'].rstrip('/')}/chat/completions"
    model = config.get("image_gen_model", "google/gemini-2.5-flash-image")
    aspect_ratio = config.get("image_gen_aspect_ratio", "1:1")

    @tree.command(name="gen_image", description="Generate an image from a prompt")
    @app_commands.describe(prompt="What you want the image to show")
    async def gen_image(interaction: discord.Interaction, prompt: str):
        await interaction.response.defer(thinking=True)

        loop = asyncio.get_event_loop()
        try:
            response = await loop.run_in_executor(
                None,
                lambda: _send_image_generation_request(
                    chat_url,
                    os.getenv("HACKCLUB_AI_API_KEY"),
                    model,
                    prompt,
                    aspect_ratio=aspect_ratio,
                ),
            )
            image_url, content = _parse_image_response(response)
            if not image_url:
                await interaction.followup.send(
                    ":x: Sorry, I couldn't generate an image for that prompt.",
                    ephemeral=False,
                )
                return

            image_bytes = _data_url_to_bytes(image_url)
            image_file = discord.File(io.BytesIO(image_bytes), filename="generated.png")
            message_text = content or f"Prompt: {prompt}"

            await interaction.followup.send(message_text, file=image_file, ephemeral=False)
        except Exception as e:
            await interaction.followup.send(
                ":x: Sorry, I encountered an error while generating the image.",
                ephemeral=False,
            )
            print(f"Error during image generation for prompt '{prompt}':", e)

    return gen_image

import asyncio
import io
import traceback

import discord
from discord import app_commands
import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel


SUPPORTED_VOICES = [
	"Vivian",
	"Serena",
	"Uncle_Fu",
	"Dylan",
	"Eric",
	"Ryan",
	"Aiden",
	"Ono_Anna",
	"Sohee",
]

_tts_model = None
_tts_model_lock = asyncio.Lock()
_tts_generation_lock = asyncio.Lock()


def _resolve_voice(voice):
	if not voice:
		return None

	voice_lower = voice.lower()
	for name in SUPPORTED_VOICES:
		if name.lower() == voice_lower:
			return name
	return None


def _load_tts_model(model_name):
	device_map = "cuda:0" if torch.cuda.is_available() else "cpu"
	dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
	attn_impl = "flash_attention_2" if torch.cuda.is_available() else "eager"
	
	try:
		return Qwen3TTSModel.from_pretrained(
			model_name,
			device_map=device_map,
			dtype=dtype,
			attn_implementation=attn_impl,
		)
	except Exception as e:
		print(f"Failed to load with flash_attention_2, falling back to eager: {e}")
		return Qwen3TTSModel.from_pretrained(
			model_name,
			device_map=device_map,
			dtype=dtype,
			attn_implementation="eager",
		)


async def _get_tts_model(config):
	global _tts_model
	if _tts_model is not None:
		return _tts_model

	async with _tts_model_lock:
		if _tts_model is not None:
			return _tts_model

		model_name = config.get("tts_model", "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice")
		loop = asyncio.get_event_loop()
		_tts_model = await loop.run_in_executor(
			None,
			lambda: _load_tts_model(model_name),
		)
		return _tts_model


def _synthesize_wav(model, text, voice):
	wavs, sr = model.generate_custom_voice(
		text=text,
		language="Auto",
		speaker=voice,
	)
	buffer = io.BytesIO()
	sf.write(buffer, wavs[0], sr, format="WAV")
	buffer.seek(0)
	return buffer


def setup_audio_commands(tree, config):
	voice_choices = [
		app_commands.Choice(name="Vivian", value="Vivian"),
		app_commands.Choice(name="Serena", value="Serena"),
		app_commands.Choice(name="Uncle_Fu", value="Uncle_Fu"),
		app_commands.Choice(name="Dylan", value="Dylan"),
		app_commands.Choice(name="Eric", value="Eric"),
		app_commands.Choice(name="Ryan", value="Ryan"),
		app_commands.Choice(name="Aiden", value="Aiden"),
		app_commands.Choice(name="Ono_Anna", value="Ono_Anna"),
		app_commands.Choice(name="Sohee", value="Sohee"),
	]

	@tree.command(name="tts", description="Speak text with a selected voice")
	@app_commands.describe(voice="Voice to use", prompt="Text to speak")
	@app_commands.choices(voice=voice_choices)
	async def tts(interaction: discord.Interaction, voice: str, prompt: str):
		await interaction.response.defer(thinking=True)

		resolved_voice = _resolve_voice(voice)
		if not resolved_voice:
			await interaction.followup.send(
				":x: Unknown voice. Please pick one of the provided choices.",
				ephemeral=True,
			)
			return

		try:
			model = await _get_tts_model(config)
			loop = asyncio.get_event_loop()

			async with _tts_generation_lock:
				audio_buffer = await loop.run_in_executor(
					None,
					lambda: _synthesize_wav(model, prompt, resolved_voice),
				)

			audio_file = discord.File(audio_buffer, filename=f"tts_{resolved_voice}.wav")
			await interaction.followup.send(
				"",
				file=audio_file,
				ephemeral=False,
			)
		except Exception as e:
			await interaction.followup.send(
				":x: Sorry, I encountered an error while generating the audio.",
				ephemeral=False,
			)
			print(f"Error during TTS for voice '{resolved_voice}': {e}")
			traceback.print_exc()

	return tts

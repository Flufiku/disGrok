import asyncio
import io
import traceback
from pathlib import Path
import tempfile

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
_voice_clone_model = None
_voice_clone_model_lock = asyncio.Lock()
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


async def _get_voice_clone_model(config):
	global _voice_clone_model
	if _voice_clone_model is not None:
		return _voice_clone_model

	async with _voice_clone_model_lock:
		if _voice_clone_model is not None:
			return _voice_clone_model

		model_name = config.get("voice_clone_model", "Qwen/Qwen3-TTS-12Hz-1.7B-Base")
		loop = asyncio.get_event_loop()
		_voice_clone_model = await loop.run_in_executor(
			None,
			lambda: _load_tts_model(model_name),
		)
		return _voice_clone_model


def _synthesize_voice_clone(model, text, ref_audio_path, ref_text=None, language="Auto"):
	"""
	Synthesize audio using voice cloning.
	
	Args:
		model: The Qwen3-TTS model
		text: Text to synthesize
		ref_audio_path: Path to reference audio file
		ref_text: Transcription of the reference audio (optional, uses x_vector_only_mode if not provided)
		language: Language for synthesis
	"""
	# Use x_vector_only_mode if no reference text is provided
	if ref_text is None:
		wavs, sr = model.generate_voice_clone(
			text=text,
			language=language,
			ref_audio=ref_audio_path,
			x_vector_only_mode=True,
		)
	else:
		wavs, sr = model.generate_voice_clone(
			text=text,
			language=language,
			ref_audio=ref_audio_path,
			ref_text=ref_text,
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

	@tree.command(name="voice_clone", description="Speak text using a voice from an audio sample")
	@app_commands.describe(
		audio_sample="Audio file to clone the voice from",
		prompt="Text to speak",
		ref_text="Optional: transcription of the audio sample (for better quality)"
	)
	async def voice_clone(
		interaction: discord.Interaction,
		audio_sample: discord.Attachment,
		prompt: str,
		ref_text: str = None,
	):
		await interaction.response.defer(thinking=True)

		# Validate audio file
		if not audio_sample.content_type or "audio" not in audio_sample.content_type:
			await interaction.followup.send(
				":x: Please upload a valid audio file (WAV, MP3, OGG, etc.)",
				ephemeral=True,
			)
			return

		try:
			model = await _get_voice_clone_model(config)
			loop = asyncio.get_event_loop()

			# Download the audio file to a temporary location
			with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio_sample.filename).suffix) as tmp_file:
				await audio_sample.save(tmp_file.name)
				temp_audio_path = tmp_file.name

			try:
				async with _tts_generation_lock:
					audio_buffer = await loop.run_in_executor(
						None,
						lambda: _synthesize_voice_clone(
							model,
							prompt,
							temp_audio_path,
							ref_text=ref_text,
							language="Auto",
						),
					)

				audio_file = discord.File(audio_buffer, filename="voice_clone.wav")
				await interaction.followup.send(
					"",
					file=audio_file,
					ephemeral=False,
				)
			finally:
				# Clean up temporary file
				Path(temp_audio_path).unlink(missing_ok=True)

		except Exception as e:
			await interaction.followup.send(
				":x: Sorry, I encountered an error while cloning the voice.",
				ephemeral=False,
			)
			print(f"Error during voice cloning: {e}")
			traceback.print_exc()

	return tts, voice_clone
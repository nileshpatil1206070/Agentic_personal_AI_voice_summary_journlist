import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

# Initialize the client
client = ElevenLabs(
    api_key=os.getenv("ELEVEN_API_KEY")
)

print("Connecting to ElevenLabs...")

# Request the audio stream
audio_stream = client.text_to_speech.convert(
    voice_id="JBFqnCBsd6RMkjVDRZzb",  # George (pre-made voice)
    text="Hello Nilesh. Your AI news agent is working successfully.",
    model_id="eleven_multilingual_v2"
)

# Collect all binary chunks from the generator into a single byte string
audio_data = b"".join(audio_stream)

# Save the full byte string to your MP3 file
with open("test.mp3", "wb") as f:
    f.write(audio_data)

print("Saved successfully! Check your VS Code file tree for test.mp3")

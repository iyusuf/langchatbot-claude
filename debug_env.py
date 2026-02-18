# debug_env.py — temporary, delete after
from dotenv import load_dotenv
import os

load_dotenv()
key = os.getenv("OPENROUTER_API_KEY")
print(f"Key loaded: {key is not None}")
print(f"Key starts with: {key[:8] if key else 'NONE'}...")
print(f"Key length: {len(key) if key else 0}")
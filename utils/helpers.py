# utils/helpers.py
import os
from dotenv import load_dotenv

load_dotenv()

def get_bot_token():
    return os.getenv('DISCORD_TOKEN')

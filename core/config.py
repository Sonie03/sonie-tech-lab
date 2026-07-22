import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "theme": "dark",
    "avatar_path": "",
    "github_token": "",
    "github_username": "",
    "voice_enabled": True,
    "voice_volume": 0.8
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_CONFIG

def save_config(config_data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)

config = load_config()

import json
import os

CONFIG_FILE = "config.json"
PRESETS_FILE = "presets.json"

DEFAULT_CONFIG = {
    "interval": 30,
    "sleep_start": "23:00",
    "sleep_end": "07:00",
    "ringtone": "DEFAULT"
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def load_presets():
    if not os.path.exists(PRESETS_FILE):
        return []
    with open(PRESETS_FILE, "r") as f:
        return json.load(f)

def save_presets(presets):
    with open(PRESETS_FILE, "w") as f:
        json.dump(presets, f, indent=4)

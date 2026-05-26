import json
import uuid
import os

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")


def _default_config():
    return {"groups": []}


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return _default_config()
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def new_id():
    return str(uuid.uuid4())[:8]

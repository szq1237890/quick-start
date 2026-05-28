import json
import uuid
import sys
import os


def _get_config_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(__file__))


CONFIG_FILE = os.path.join(_get_config_dir(), "config.json")


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

# utils/checkpoint.py
import json

CHECKPOINT_FILE = "scraper_checkpoint.json"

def save_keys_checkpoint(keys):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(sorted(list(keys)), f)

def load_keys_checkpoint():
    try:
        with open(CHECKPOINT_FILE, "r") as f:
            return set(tuple(x) for x in json.load(f))
    except FileNotFoundError:
        return set()
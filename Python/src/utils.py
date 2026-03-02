import sys
import json
import pathlib

_CONFIG_PATH = pathlib.Path(__file__).parent / "config.json"

# ══════════════ UTILITÀ ══════════════
def clear_once():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

def save_config(updates: dict):
    """Merge *updates* into config.json and write back."""
    with open(_CONFIG_PATH) as f:
        cfg = json.load(f)
    cfg.update(updates)
    with open(_CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)
    return cfg

def load_config() -> dict:
    with open(_CONFIG_PATH) as f:
        return json.load(f)
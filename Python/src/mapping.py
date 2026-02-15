import json
from config import MAPPING_FILE

# ══════════════ MAPPING ══════════════
def load_mapping() -> dict | None:
    if MAPPING_FILE.exists():
        try:
            with open(MAPPING_FILE) as f:
                return json.load(f)
        except Exception:
            print(f"  Impossibile leggere {MAPPING_FILE.name}: file JSON malformato")
    return None

def save_mapping(data: dict):
    with open(MAPPING_FILE, "w") as f:
        json.dump(data, f, indent=2)
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


# ══════════════ AXIS HELPERS ══════════════
# Supportano sia il vecchio formato (int) sia il nuovo (dict con idx/rest/peak).

def get_axis_idx(assi: dict, name: str, default: int = 0) -> int:
    """Restituisce l'indice di un asse dal mapping."""
    val = assi.get(name, default)
    if isinstance(val, dict):
        return val.get("idx", default)
    return int(val) if val is not None else default


def get_axis_calibration(assi: dict, name: str) -> tuple[float, float]:
    """Restituisce (rest, peak) di un asse.  Fallback: (-1.0, 1.0)."""
    val = assi.get(name)
    if isinstance(val, dict):
        return val.get("rest", -1.0), val.get("peak", 1.0)
    return -1.0, 1.0


def norm_pedal(raw: float, rest: float, peak: float) -> float:
    """Normalizza un valore pedale: 0.0 (riposo) → 1.0 (premuto a fondo)."""
    span = peak - rest
    if abs(span) < 0.01:
        return 0.0
    return max(0.0, min(1.0, (raw - rest) / span))


def norm_steer(raw: float, rest: float, peak: float) -> float:
    """Normalizza lo sterzo: -1.0 … 0.0 (centro) … +1.0."""
    span = abs(peak - rest)
    if span < 0.01:
        return 0.0
    return max(-1.0, min(1.0, (raw - rest) / span))
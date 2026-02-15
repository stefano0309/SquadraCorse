import sys

# ══════════════ UTILITÀ ══════════════
def clear_once():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()
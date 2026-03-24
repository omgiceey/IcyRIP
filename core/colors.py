"""Cores usadas pelo projeto (fallbacks inclusos)."""

CYAN = "\033[96m"
RED = "\033[91m"
ORANGE = "\033[38;5;208m"
RESET = "\033[0m"
GREEN = "\033[92m"

# fallback
try:
    # terminal may not support 256 colors; use yellow as fallback for orange
    if not ORANGE:
        ORANGE = "\033[33m"
except Exception:
    ORANGE = "\033[33m"


import os
import re
from typing import Tuple, Dict

RESET = "\033[0m"
BOLD  = "\033[1m"
DIM   = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"


def supports_truecolor() -> bool:
    ct = os.environ.get("COLORTERM", "").lower()
    return "truecolor" in ct or "24bit" in ct


def hex_to_rgb(h: str) -> Tuple[int, int, int]:
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        raise ValueError(f"Invalid hex color: #{h}")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgb_to_ansi_truecolor(rgb: Tuple[int, int, int]) -> str:
    r, g, b = rgb
    return f"\033[38;2;{r};{g};{b}m"


def rgb_to_ansi_256(rgb: Tuple[int, int, int]) -> str:
    r, g, b = rgb
    r6 = round((r / 255) * 5)
    g6 = round((g / 255) * 5)
    b6 = round((b / 255) * 5)
    return f"\033[38;5;{16 + 36 * r6 + 6 * g6 + b6}m"


def rgb_to_ansi_bg(rgb: Tuple[int, int, int]) -> str:
    r, g, b = rgb
    return f"\033[48;2;{r};{g};{b}m"


def to_ansi(value: str) -> str:
    if not value:
        return ""
    if value.startswith("\033["):
        return value
    try:
        rgb = hex_to_rgb(value.strip())
        return rgb_to_ansi_truecolor(rgb) if supports_truecolor() else rgb_to_ansi_256(rgb)
    except Exception:
        return value


def colored(text: str, hex_color: str) -> str:
    return f"{to_ansi(hex_color)}{text}{RESET}"


def bg_colored(text: str, fg_hex: str, bg_hex: str) -> str:
    try:
        bg = rgb_to_ansi_bg(hex_to_rgb(bg_hex))
    except Exception:
        bg = ""
    return f"{bg}{to_ansi(fg_hex)}{text}{RESET}"


def gradient_text(text: str, start_hex: str, end_hex: str) -> str:
    try:
        sr, sg, sb = hex_to_rgb(start_hex)
        er, eg, eb = hex_to_rgb(end_hex)
    except Exception:
        return text

    chars = [c for c in text if c not in (" ", "\n")]
    n = max(1, len(chars) - 1)
    out = []
    ci = 0
    for ch in text:
        if ch in (" ", "\n"):
            out.append(ch)
            continue
        t = ci / n
        r = int(sr + (er - sr) * t)
        g = int(sg + (eg - sg) * t)
        b = int(sb + (eb - sb) * t)
        if supports_truecolor():
            out.append(f"\033[38;2;{r};{g};{b}m{ch}{RESET}")
        else:
            out.append(f"{rgb_to_ansi_256((r, g, b))}{ch}{RESET}")
        ci += 1
    return "".join(out)


def gradient_line(width: int, start_hex: str, end_hex: str, char: str = "─") -> str:
    return gradient_text(char * width, start_hex, end_hex)


DEFAULT_THEME: Dict[str, str] = {
    "HEADER":   "#00BCD4",
    "ACCENT":   "#ff6a00",
    "INFO":     "#7fdbff",
    "SUCCESS":  "#2ecc71",
    "WARN":     "#f1c40f",
    "ERROR":    "#e74c3c",
    "PROGRESS": "#ff4d4d",
    "CYAN":     "#00BCD4",
    "RED":      "#e53935",
    "ORANGE":   "#ff6a00",
}


PRESETS: Dict[str, Dict[str, str]] = {
    "default": {
        "HEADER": "#00BCD4", "ACCENT": "#ff6a00", "INFO": "#7fdbff",
        "SUCCESS": "#2ecc71", "WARN": "#f1c40f", "ERROR": "#e74c3c",
        "PROGRESS": "#ff4d4d", "CYAN": "#00BCD4", "RED": "#e53935", "ORANGE": "#ff6a00",
        "_banner_start": "#00BCD4", "_banner_end": "#ff6a00",
        "_desc": "Padrão  (ciano + laranja)",
    },
    "cyberpunk": {
        "HEADER": "#ff00ff", "ACCENT": "#00ffff", "INFO": "#ff80ff",
        "SUCCESS": "#00ff9f", "WARN": "#ffff00", "ERROR": "#ff003c",
        "PROGRESS": "#ff00cc", "CYAN": "#00ffff", "RED": "#ff003c", "ORANGE": "#ff8800",
        "_banner_start": "#ff00ff", "_banner_end": "#00ffff",
        "_desc": "Cyberpunk  (magenta + ciano)",
    },
    "dracula": {
        "HEADER": "#bd93f9", "ACCENT": "#ff79c6", "INFO": "#8be9fd",
        "SUCCESS": "#50fa7b", "WARN": "#f1fa8c", "ERROR": "#ff5555",
        "PROGRESS": "#ff79c6", "CYAN": "#8be9fd", "RED": "#ff5555", "ORANGE": "#ffb86c",
        "_banner_start": "#bd93f9", "_banner_end": "#ff79c6",
        "_desc": "Dracula  (roxo + rosa)",
    },
    "monokai": {
        "HEADER": "#a6e22e", "ACCENT": "#f92672", "INFO": "#66d9e8",
        "SUCCESS": "#a6e22e", "WARN": "#e6db74", "ERROR": "#f92672",
        "PROGRESS": "#fd971f", "CYAN": "#66d9e8", "RED": "#f92672", "ORANGE": "#fd971f",
        "_banner_start": "#a6e22e", "_banner_end": "#f92672",
        "_desc": "Monokai  (verde + rosa)",
    },
    "ocean": {
        "HEADER": "#0099cc", "ACCENT": "#00ccff", "INFO": "#66e0ff",
        "SUCCESS": "#00e5b0", "WARN": "#ffe066", "ERROR": "#ff4466",
        "PROGRESS": "#00ccff", "CYAN": "#00ccff", "RED": "#ff4466", "ORANGE": "#ff9933",
        "_banner_start": "#0099cc", "_banner_end": "#00e5b0",
        "_desc": "Ocean  (azul profundo + verde-água)",
    },
    "forest": {
        "HEADER": "#4caf50", "ACCENT": "#8bc34a", "INFO": "#a5d6a7",
        "SUCCESS": "#66bb6a", "WARN": "#ffee58", "ERROR": "#ef5350",
        "PROGRESS": "#81c784", "CYAN": "#4dd0e1", "RED": "#ef5350", "ORANGE": "#ffa726",
        "_banner_start": "#4caf50", "_banner_end": "#8bc34a",
        "_desc": "Forest  (verde escuro + verde claro)",
    },
    "rose": {
        "HEADER": "#f48fb1", "ACCENT": "#f06292", "INFO": "#f8bbd0",
        "SUCCESS": "#a5d6a7", "WARN": "#fff176", "ERROR": "#e57373",
        "PROGRESS": "#f06292", "CYAN": "#80deea", "RED": "#e57373", "ORANGE": "#ffb74d",
        "_banner_start": "#f48fb1", "_banner_end": "#f06292",
        "_desc": "Rose  (rosa claro + rosa escuro)",
    },
    "midnight": {
        "HEADER": "#7c4dff", "ACCENT": "#448aff", "INFO": "#82b1ff",
        "SUCCESS": "#69f0ae", "WARN": "#ffd740", "ERROR": "#ff5252",
        "PROGRESS": "#448aff", "CYAN": "#84ffff", "RED": "#ff5252", "ORANGE": "#ffab40",
        "_banner_start": "#7c4dff", "_banner_end": "#448aff",
        "_desc": "Midnight  (violeta + azul elétrico)",
    },
    "aurora": {
        "HEADER": "#00e5ff", "ACCENT": "#76ff03", "INFO": "#b2ff59",
        "SUCCESS": "#69f0ae", "WARN": "#ffff00", "ERROR": "#ff1744",
        "PROGRESS": "#00e5ff", "CYAN": "#00e5ff", "RED": "#ff1744", "ORANGE": "#ff9100",
        "_banner_start": "#00e5ff", "_banner_end": "#76ff03",
        "_desc": "Aurora  (ciano brilhante + verde neon)",
    },
    "candy": {
        "HEADER": "#ff6ec7", "ACCENT": "#ffe66d", "INFO": "#a8edea",
        "SUCCESS": "#a8edea", "WARN": "#ffe66d", "ERROR": "#ff6b6b",
        "PROGRESS": "#ff6ec7", "CYAN": "#a8edea", "RED": "#ff6b6b", "ORANGE": "#ffa07a",
        "_banner_start": "#ff6ec7", "_banner_end": "#ffe66d",
        "_desc": "Candy  (rosa chiclete + amarelo)",
    },
    "blood": {
        "HEADER": "#ff1744", "ACCENT": "#d50000", "INFO": "#ff8a80",
        "SUCCESS": "#69f0ae", "WARN": "#ffd740", "ERROR": "#b71c1c",
        "PROGRESS": "#ff1744", "CYAN": "#ff8a80", "RED": "#ff1744", "ORANGE": "#ff6d00",
        "_banner_start": "#ff1744", "_banner_end": "#d50000",
        "_desc": "Blood  (vermelho intenso)",
    },
    "matrix": {
        "HEADER": "#00ff41", "ACCENT": "#008f11", "INFO": "#00ff41",
        "SUCCESS": "#00ff41", "WARN": "#ccff00", "ERROR": "#ff0000",
        "PROGRESS": "#00ff41", "CYAN": "#00ff41", "RED": "#ff0000", "ORANGE": "#ccff00",
        "_banner_start": "#00ff41", "_banner_end": "#008f11",
        "_desc": "Matrix  (verde terminal)",
    },
    "gold": {
        "HEADER": "#ffd700", "ACCENT": "#ffaa00", "INFO": "#ffe066",
        "SUCCESS": "#b5e853", "WARN": "#ffd700", "ERROR": "#ff4444",
        "PROGRESS": "#ffd700", "CYAN": "#ffe066", "RED": "#ff4444", "ORANGE": "#ffaa00",
        "_banner_start": "#ffd700", "_banner_end": "#ffaa00",
        "_desc": "Gold  (dourado + âmbar)",
    },
    "synthwave": {
        "HEADER": "#e040fb", "ACCENT": "#ff6d00", "INFO": "#ea80fc",
        "SUCCESS": "#69ff47", "WARN": "#ffde03", "ERROR": "#ff1744",
        "PROGRESS": "#e040fb", "CYAN": "#18ffff", "RED": "#ff1744", "ORANGE": "#ff6d00",
        "_banner_start": "#e040fb", "_banner_end": "#ff6d00",
        "_desc": "Synthwave  (roxo neon + laranja retrowave)",
    },
    "arctic": {
        "HEADER": "#80d8ff", "ACCENT": "#b3e5fc", "INFO": "#e1f5fe",
        "SUCCESS": "#b9f6ca", "WARN": "#fff9c4", "ERROR": "#ff8a80",
        "PROGRESS": "#80d8ff", "CYAN": "#80d8ff", "RED": "#ff8a80", "ORANGE": "#ffd180",
        "_banner_start": "#80d8ff", "_banner_end": "#b3e5fc",
        "_desc": "Arctic  (azul gelo + ciano pálido)",
    },
    "lava": {
        "HEADER": "#ff6e00", "ACCENT": "#ffcc00", "INFO": "#ffab40",
        "SUCCESS": "#ccff00", "WARN": "#ffcc00", "ERROR": "#b71c1c",
        "PROGRESS": "#ff6e00", "CYAN": "#ffab40", "RED": "#b71c1c", "ORANGE": "#ff6e00",
        "_banner_start": "#ff6e00", "_banner_end": "#ffcc00",
        "_desc": "Lava  (laranja queimado + amarelo incandescente)",
    },
    "sakura": {
        "HEADER": "#f8bbd0", "ACCENT": "#ce93d8", "INFO": "#fce4ec",
        "SUCCESS": "#c8e6c9", "WARN": "#fff9c4", "ERROR": "#ef9a9a",
        "PROGRESS": "#f48fb1", "CYAN": "#b2ebf2", "RED": "#ef9a9a", "ORANGE": "#ffccbc",
        "_banner_start": "#f8bbd0", "_banner_end": "#ce93d8",
        "_desc": "Sakura  (rosa suave + lilás)",
    },
    "slate": {
        "HEADER": "#546e7a", "ACCENT": "#4db6ac", "INFO": "#80cbc4",
        "SUCCESS": "#a5d6a7", "WARN": "#fff176", "ERROR": "#ef5350",
        "PROGRESS": "#4db6ac", "CYAN": "#80deea", "RED": "#ef5350", "ORANGE": "#ffb74d",
        "_banner_start": "#546e7a", "_banner_end": "#4db6ac",
        "_desc": "Slate  (cinza azulado + teal)",
    },
    "toxic": {
        "HEADER": "#b2ff59", "ACCENT": "#eeff41", "INFO": "#ccff90",
        "SUCCESS": "#b2ff59", "WARN": "#eeff41", "ERROR": "#ff1744",
        "PROGRESS": "#b2ff59", "CYAN": "#ccff90", "RED": "#ff1744", "ORANGE": "#ffab40",
        "_banner_start": "#b2ff59", "_banner_end": "#eeff41",
        "_desc": "Toxic  (verde limão + amarelo ácido)",
    },
}


def list_presets() -> Dict[str, str]:
    return {k: v.get("_desc", k) for k, v in PRESETS.items()}


def apply_preset(name: str, save: bool = True) -> bool:
    preset = PRESETS.get(name)
    if not preset:
        return False

    roles = [k for k in preset if not k.startswith("_")]
    for role in roles:
        setattr(_mod(), role, to_ansi(preset[role]))

    if save:
        try:
            from core import config as _cfg
            cfg = _cfg.load_config()
            cfg["preset"] = name
            all_preset_roles = {k for p in PRESETS.values() for k in p if not k.startswith("_")}
            existing = cfg.get("colors") or {}
            cfg["colors"] = {k: v for k, v in existing.items() if k not in all_preset_roles}
            current_style = cfg.get("ascii_style", "follow_theme")
            if not isinstance(current_style, dict):
                cfg["ascii_style"] = "follow_theme"
                cfg.pop("ascii_colors", None)
            _cfg.save_config(cfg)
        except Exception:
            pass
    return True


def resolve_theme(cfg: dict) -> dict:
    preset_name = cfg.get("preset")
    if preset_name and preset_name in PRESETS:
        base = {k: v for k, v in PRESETS[preset_name].items() if not k.startswith("_")}
    else:
        base = dict(DEFAULT_THEME)
    custom = cfg.get("colors") or {}
    return {**base, **custom}


def theme_color(cfg: dict, role: str) -> str:
    return resolve_theme(cfg).get(role, DEFAULT_THEME.get(role, ""))


def _mod():
    import sys
    return sys.modules[__name__]


def apply_theme_to_module(cfg: dict):
    preset_name = cfg.get("preset")
    base = {k: v for k, v in PRESETS[preset_name].items() if not k.startswith("_")} \
        if preset_name and preset_name in PRESETS else dict(DEFAULT_THEME)
    merged = {**base, **(cfg.get("colors") or {})}
    mod = _mod()
    for role, h in merged.items():
        if not role.startswith("_") and hasattr(mod, role):
            setattr(mod, role, to_ansi(h))


HEADER   = to_ansi(DEFAULT_THEME["HEADER"])
ACCENT   = to_ansi(DEFAULT_THEME["ACCENT"])
INFO     = to_ansi(DEFAULT_THEME["INFO"])
SUCCESS  = to_ansi(DEFAULT_THEME["SUCCESS"])
WARN     = to_ansi(DEFAULT_THEME["WARN"])
ERROR    = to_ansi(DEFAULT_THEME["ERROR"])
PROGRESS = to_ansi(DEFAULT_THEME["PROGRESS"])
CYAN     = to_ansi(DEFAULT_THEME["CYAN"])
RED      = to_ansi(DEFAULT_THEME["RED"])
ORANGE   = to_ansi(DEFAULT_THEME["ORANGE"])

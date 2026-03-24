import json
from pathlib import Path


def get_config_path() -> Path:
    # config file in workspace root
    return Path.cwd() / "config.json"


def default_config():
    return {
        "language": "pt",
        "theme": "default",  # 'default' or 'alternative'
        "playlist_warning_threshold": 50,
        # executables (paths) can be set by the HUB
        "yt_dlp_path": None,
        "ffmpeg_path": None,
        # allow startup language prompt only once
        "startup_language_asked": False,
        "use_system_language": False,
        # optional custom colors mapping (ANSI sequences)
        "colors": {}
    }


def load_config():
    p = get_config_path()
    if not p.exists():
        cfg = default_config()
        save_config(cfg)
        return cfg
    try:
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = default_config()
    # ensure defaults present
    base = default_config()
    base.update(data or {})
    return base


def save_config(cfg: dict):
    p = get_config_path()
    try:
        with p.open("w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

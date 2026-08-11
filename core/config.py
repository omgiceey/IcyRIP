import json
import shutil
from pathlib import Path


def get_xdg_config_path() -> Path:
    p = Path.home() / ".config" / "icyrip"
    p.mkdir(parents=True, exist_ok=True)
    return p / "config.json"


def get_config_path() -> Path:
    return get_xdg_config_path()


def default_config() -> dict:
    return {
        "language": "pt",
        "theme": "default",
        "preset": "default",
        "playlist_warning_threshold": 50,
        "yt_dlp_path": None,
        "ffmpeg_path": None,
        "startup_language_asked": False,
        "use_system_language": False,
        "colors": {},
        "ascii_style": "follow_theme",
        "ascii_colors": {},
        "save_paths": {},
        "verbose": False,
        "restrict_filenames": False,
        "audio_quality": "0",
        "cookies_browser": None,
        "profiles": {},
        "notifications": True,
        "applied_patches": [],
        "organizar_por_artista": False,
        "max_retries": 3,
        "retry_backoff": True,
        "verificar_integridade": True,
        "max_workers": 1,
        "color_mode": "follow_preset",
    }


def load_config() -> dict:
    p = get_config_path()
    xdg = get_xdg_config_path()

    cwd_cfg = Path.cwd() / "config.json"
    try:
        if cwd_cfg.exists() and not xdg.exists():
            shutil.copy2(cwd_cfg, xdg)
            shutil.copy2(cwd_cfg, cwd_cfg.with_suffix(".bak"))
    except Exception:
        pass

    if not p.exists():
        cfg = default_config()
        save_config(cfg)
        return cfg

    try:
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = {}

    base = default_config()
    for k, v in (data or {}).items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            base[k] = {**base[k], **v}
        else:
            base[k] = v
    return base


def save_config(cfg: dict) -> bool:
    try:
        p = get_xdg_config_path()
        with p.open("w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def reset_config() -> bool:
    return save_config(default_config())


def export_config(dest: str) -> bool:
    try:
        cfg = load_config()
        portable = {k: v for k, v in cfg.items() if k not in ("yt_dlp_path", "ffmpeg_path", "save_paths")}
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(portable, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def import_config(src: str) -> bool:
    try:
        with open(src, "r", encoding="utf-8") as f:
            data = json.load(f)
        base = default_config()
        for k, v in (data or {}).items():
            if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                base[k] = {**base[k], **v}
            else:
                base[k] = v
        return save_config(base)
    except Exception:
        return False

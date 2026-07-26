import sys
import importlib
import shutil
import subprocess
import os
import locale
import time
import re
import threading
import signal
from pathlib import Path

from core import colors
from core import utils
from core.utils import animate_banner_in, animate_exit
import core.config as cfgmod
from core.i18n import t


VERSION = "2.1"

ASCII = r"""
░▒▓█▓▒░░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░░▒▓█▓▒░▒▓███████▓▒░
░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░
░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░
░▒▓█▓▒░▒▓█▓▒░       ░▒▓██████▓▒░░▒▓███████▓▒░░▒▓█▓▒░▒▓███████▓▒░
░▒▓█▓▒░▒▓█▓▒░         ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░
░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░
░▒▓█▓▒░░▒▓██████▓▒░   ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░
"""

def _tw() -> int:
    try:
        return shutil.get_terminal_size((80, 20)).columns
    except (OSError, ValueError):
        return 80


def _box_w() -> int:
    return max(52, min(_tw() - 2, 90))


_NEEDS_REDRAW = threading.Event()

def _setup_resize_handler():
    def _on_resize(_sig, _frame):
        _NEEDS_REDRAW.set()
    try:
        signal.signal(signal.SIGWINCH, _on_resize)
    except (AttributeError, OSError):
        pass


def limpar_tela():
    try:
        if os.name == "nt":
            os.system("cls")
        else:
            sys.stdout.write("\033[2J\033[3J\033[H")
            sys.stdout.flush()
    except Exception:
        try:
            os.system("cls" if os.name == "nt" else "clear")
        except Exception:
            pass


def _pausar(cor=None):
    c = cor or colors.CYAN
    input(f"\n{c}  {t('press_enter')}{colors.RESET}")


def _confirmar(pergunta: str, cor=None) -> bool:
    c = cor or colors.CYAN
    return input(f"{c}{pergunta} {t('confirm_yn')}: {colors.RESET}").strip().lower().startswith(t('yes_key'))


def _transicao(label: str, cor=None):
    c = cor or colors.CYAN
    try:
        print(f"\n{c}  → {label}{colors.RESET}")
        time.sleep(0.15)
    except (IOError, OSError):
        pass


def _sep(char="─", width=None) -> str:
    w = (width or _tw()) - 4
    try:
        cfg = cfgmod.load_config()
        s = colors.theme_color(cfg, "HEADER")
        e = colors.theme_color(cfg, "ACCENT")
        return "  " + colors.gradient_line(w, s, e, char)
    except (OSError, KeyError, TypeError, ValueError):
        return f"  {colors.HEADER}{char * w}{colors.RESET}"


def _box_colors():
    try:
        cfg = cfgmod.load_config()
        s = colors.theme_color(cfg, "HEADER")
        e = colors.theme_color(cfg, "ACCENT")
        return colors.to_ansi(s), colors.to_ansi(e), s, e
    except (OSError, KeyError, TypeError, ValueError):
        return colors.HEADER, colors.ACCENT, colors.DEFAULT_THEME["HEADER"], colors.DEFAULT_THEME["ACCENT"]


def _box_top(width=None) -> str:
    w = (width or _box_w()) - 4
    hl, hr, s, e = _box_colors()
    line = colors.gradient_line(w - 2, s, e, "─")
    return f"  {hl}╭─{colors.RESET}{line}{hr}╮{colors.RESET}"


def _box_bot(width=None) -> str:
    w = (width or _box_w()) - 4
    hl, hr, s, e = _box_colors()
    line = colors.gradient_line(w - 2, s, e, "─")
    return f"  {hl}╰─{colors.RESET}{line}{hr}╯{colors.RESET}"


def _box_mid(width=None) -> str:
    w = (width or _box_w()) - 4
    hl, hr, s, e = _box_colors()
    line = colors.gradient_line(w - 2, s, e, "─")
    return f"  {hl}├─{colors.RESET}{line}{hr}┤{colors.RESET}"


_ANSI_RE = re.compile(r"\033\[[0-9;]*m")


def _strip_ansi(s: str) -> str:
    return _ANSI_RE.sub("", s or "")


def _emoji_width(s: str) -> int:
    import unicodedata
    w = 0
    for ch in _strip_ansi(s or ""):
        eaw = unicodedata.east_asian_width(ch)
        w += 2 if eaw in ('W', 'F') or ord(ch) > 0x1F000 else 1
    return w


def _clip_visual(s: str, width: int) -> str:
    if width <= 0 or _emoji_width(s) <= width:
        return s
    import unicodedata
    out = []
    used = 0
    limit = max(0, width - 1)
    for ch in s:
        eaw = unicodedata.east_asian_width(ch)
        cw = 2 if eaw in ('W', 'F') or ord(ch) > 0x1F000 else 1
        if used + cw > limit:
            break
        out.append(ch)
        used += cw
    return "".join(out) + "…"


def _pad_visual(s: str, width: int) -> str:
    return s + (" " * max(0, width - _emoji_width(s)))


def _center_visual(s: str, width: int) -> str:
    pad = max(0, width - _emoji_width(s))
    return (" " * (pad // 2)) + s + (" " * (pad - pad // 2))


def _compact_w() -> int:
    return max(42, min(_tw() - 4, 74))


def _compact_line(width: int, char: str = "─") -> str:
    try:
        cfg = cfgmod.load_config()
        s = colors.theme_color(cfg, "HEADER")
        e = colors.theme_color(cfg, "ACCENT")
        return "  " + colors.gradient_line(width, s, e, char)
    except (OSError, KeyError, TypeError, ValueError):
        return f"  {colors.DIM}{char * width}{colors.RESET}"


def _compact_header(title: str, subtitle: str = "", width: int | None = None):
    w = width or _compact_w()
    _, _, s, e = _box_colors()
    print(_compact_line(w))
    title_colored = colors.gradient_text(title, s, e)
    print(f"  {colors.BOLD}{title_colored}{colors.RESET}")
    if subtitle:
        print(f"  {colors.DIM}{_center_visual(subtitle, w)}{colors.RESET}")
    print(_compact_line(w))


def _compact_row(key: str, label: str, desc: str, key_color: str, width: int | None = None) -> str:
    w = width or _compact_w()
    label = _strip_ansi(label or "").strip()
    desc = _strip_ansi(desc or "").strip()
    key_s = f"[{key}]"

    if w < 58:
        label_w = max(10, w - 11)
        return (
            f"  {key_color}{key_s:<4}{colors.RESET} "
            f"{colors.BOLD}{_clip_visual(label, label_w)}{colors.RESET}"
        )

    label_w = 22
    desc_w = max(8, w - label_w - 12)
    return (
        f"  {key_color}{key_s:<5}{colors.RESET}"
        f"{colors.BOLD}{_pad_visual(_clip_visual(label, label_w), label_w)}{colors.RESET}"
        f"  {colors.DIM}{_clip_visual(desc, desc_w)}{colors.RESET}"
    )


def _compact_status(parts: list[tuple[str, str]], width: int | None = None):
    w = width or _compact_w()
    chunks = []
    for label, value in parts:
        chunks.append(f"{colors.DIM}{label}:{colors.RESET} {value}")
    line = f"  {colors.DIM}·{colors.RESET}  ".join(chunks)
    print(_compact_line(w, "─"))
    print(f"  {_clip_visual(line, w - 2)}")


def _resolve_ascii_colors(cfg: dict, module: str = "main"):
    cfg_colors = cfg.get("colors", {}) or {}
    raw = cfg.get("ascii_style", "follow_theme")
    style = raw.get(module, "follow_theme") if isinstance(raw, dict) else raw

    if style == "neon":
        return "#00ff99", "#8a2be2"
    if style == "default":
        return colors.DEFAULT_THEME["HEADER"], colors.DEFAULT_THEME["ACCENT"]
    if style == "custom":
        ac = (cfg.get("ascii_colors") or {}).get(module, {})
        return (
            ac.get("start", colors.theme_color(cfg, "HEADER")),
            ac.get("end",   colors.theme_color(cfg, "ACCENT")),
        )
    return (
        colors.theme_color(cfg, "HEADER"),
        colors.theme_color(cfg, "ACCENT"),
    )


def mostrar_banner(cfg: dict, animated: bool = False):
    s_hex, e_hex = _resolve_ascii_colors(cfg, "main")
    try:
        centered = utils.center_text(ASCII)
        if animated:
            animate_banner_in(centered, s_hex, e_hex)
        else:
            print(colors.gradient_text(centered, s_hex, e_hex))
    except (OSError, ValueError, KeyError, TypeError):
        print(f"{colors.HEADER}{ASCII}{colors.RESET}")
    print()


def apply_theme(_theme_name: str):
    try:
        cfg = cfgmod.load_config()
        custom = cfg.get("colors") or {}
        preset_name = cfg.get("preset")
    except (OSError, TypeError, KeyError):
        custom = {}
        preset_name = None

    if preset_name and preset_name in colors.PRESETS:
        base = {k: v for k, v in colors.PRESETS[preset_name].items() if not k.startswith("_")}
    else:
        base = dict(colors.DEFAULT_THEME)
    merged = {**base, **custom}
    for role, h in merged.items():
        if not role.startswith("_") and hasattr(colors, role):
            setattr(colors, role, colors.to_ansi(h))


def escolher_idioma() -> str:
    limpar_tela()
    try:
        cfg = cfgmod.load_config()
        s, e = _resolve_ascii_colors(cfg, "main")
        print(colors.gradient_text(ASCII, s, e))
    except (OSError, ValueError, KeyError, TypeError):
        print(f"{colors.CYAN}{ASCII}{colors.RESET}")
    print(f"{colors.HEADER}  ICYRIP — Selecione o idioma / Select language{colors.RESET}")
    print(_sep())
    print(f"{colors.CYAN}  [1]{colors.RESET}  {t('lang_pt')}")
    print(f"{colors.CYAN}  [2]{colors.RESET}  {t('lang_en')}")
    print(_sep())
    return "pt" if input(f"{colors.CYAN}  {t('lang_prompt')}: {colors.RESET}").strip() == "1" else "en"


def prompt_startup_language_choice() -> str:
    cfg = cfgmod.load_config()
    if cfg.get("startup_language_asked"):
        return cfg.get("language", "pt")

    limpar_tela()
    try:
        s, e = _resolve_ascii_colors(cfg, "main")
        print(colors.gradient_text(ASCII, s, e))
    except (OSError, ValueError, KeyError, TypeError):
        print(f"{colors.CYAN}{ASCII}{colors.RESET}")
    print(f"{colors.HEADER}  {t('lang_system')}{colors.RESET}")
    print(_sep())
    if input(f"{colors.CYAN}  {t('lang_yes_no')}: {colors.RESET}").strip().lower().startswith(t('yes_key')):
        syslang = locale.getlocale()[0] or "pt"
        cfg["language"] = "pt" if syslang.lower().startswith("pt") else "en"
        cfg["use_system_language"] = True
    else:
        cfg["language"] = escolher_idioma()
        cfg["use_system_language"] = False

    cfg["startup_language_asked"] = True
    cfgmod.save_config(cfg)
    from core.i18n import _invalidate_lang_cache
    _invalidate_lang_cache()
    return cfg["language"]


def menu_presets():
    C, R = colors.CYAN, colors.RESET
    preset_list = list(colors.PRESETS.items())

    while True:
        cfg = cfgmod.load_config()
        limpar_tela()
        mostrar_banner(cfg)
        current = cfg.get("preset", "default")

        print(f"\n{C}  ◈ Presets de Cores  {colors.DIM}(atual: {current}){R}\n")

        for i, (name, data) in enumerate(preset_list, 1):
            s = data["_banner_start"]
            e = data["_banner_end"]
            swatch = colors.gradient_text("██████████", s, e)
            desc = data.get("_desc", name)
            marker = f"{colors.SUCCESS}✔{R} " if name == current else "  "
            print(f"  {marker}{C}[{i:2}]{R}  {swatch}  {desc}")

        print(f"\n  {C}[ 0]{R}  Voltar sem alterar")
        print(_sep())

        try:
            escolha = input(f"\n{C}  Número do preset: {R}").strip()
            if escolha == "0" or not escolha:
                break
            idx = int(escolha) - 1
            if not 0 <= idx < len(preset_list):
                raise ValueError()
        except (ValueError, IndexError):
            print(f"{colors.WARN}  Opção inválida.{R}")
            time.sleep(0.8)
            continue

        name, data = preset_list[idx]

        limpar_tela()
        s = data["_banner_start"]
        e = data["_banner_end"]
        print(colors.gradient_text(utils.center_text(ASCII), s, e))
        print(f"  {colors.BOLD}Preview: {name}  —  {data.get('_desc', name)}{R}")
        swatch_line = (f"  {colors.to_ansi(data['HEADER'])}HEADER{R}  "
                       f"{colors.to_ansi(data['ACCENT'])}ACCENT{R}  "
                       f"{colors.to_ansi(data['SUCCESS'])}SUCCESS{R}  "
                       f"{colors.to_ansi(data['WARN'])}WARN{R}  "
                       f"{colors.to_ansi(data['ERROR'])}ERROR{R}  "
                       f"{colors.to_ansi(data['INFO'])}INFO{R}  "
                       f"{colors.to_ansi(data['CYAN'])}CYAN{R}  "
                       f"{colors.to_ansi(data['RED'])}RED{R}  "
                       f"{colors.to_ansi(data['ORANGE'])}ORANGE{R}")
        print(swatch_line)
        print()

        if _confirmar(f"  Aplicar preset '{name}'?"):
            colors.apply_preset(name, save=True)
            cfg = cfgmod.load_config()
            apply_theme(cfg.get("theme", "default"))
            print(f"{colors.SUCCESS}  ✔ Preset '{name}' aplicado!{R}")
            time.sleep(1)
            break


def _verificar_update():
    C, R = colors.CYAN, colors.RESET
    cfg = cfgmod.load_config()
    limpar_tela()
    mostrar_banner(cfg)

    from core.utils import with_spinner, get_update_info
    import urllib.request, json as _json, shutil as _sh

    w = _compact_w()
    _compact_header(f"🔄  {t('opt_update').strip()}", f"v{VERSION}", w)
    print(_compact_row("1", f"🔍  {t('update_checking').strip()}", "github releases", C, w))
    print(_compact_row("s", f"💬  {t('update_support')}", t('update_support_url'), C, w))
    print(_compact_row("0", f"←   {t('opt_back').strip()}", "hub", colors.DIM, w))
    print(_compact_line(w))

    opc = input(f"\n{C}  ❥ {R}").strip().lower()
    if opc == "s":
        print(f"\n  {C}{t('update_support_msg')}{R}")
        print(f"  {colors.HEADER}{t('update_support_url')}{R}")
        _pausar()
        return
    if opc != "1":
        return

    print(f"\n{C}  {t('update_checking')}{R}")

    info = {}
    def _fetch():
        try:
            url = "https://api.github.com/repos/omgiceey/IcyRIP/releases/latest"
            req = urllib.request.Request(url, headers={"User-Agent": "ICYRIP"})
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = _json.loads(resp.read())
            info["latest"] = data.get("tag_name", "").lstrip("v")
            info["url"]    = data.get("html_url", "")
        except Exception as e:
            info["error"] = str(e)

    with_spinner(t('update_checking'), _fetch, C)

    if info.get("error") or not info.get("latest"):
        print(f"{colors.ERROR}  {t('update_fail')}{R}")
        if info.get("error"):
            print(f"{colors.DIM}  {info['error']}{R}")
        _pausar()
        return

    latest = info["latest"]
    current_c = colors.DIM
    latest_c  = colors.SUCCESS if latest != VERSION else colors.SUCCESS
    arrow     = f"{colors.DIM}→{colors.RESET}"
    if latest == VERSION:
        print(f"\n  {current_c}v{VERSION}{colors.RESET}  {arrow}  {colors.SUCCESS}v{latest}  ✔  {t('update_none')}{colors.RESET}")
        _pausar()
        return

    print(f"\n  {colors.DIM}v{VERSION}{colors.RESET}  {arrow}  {colors.SUCCESS}v{latest}  ⚠  {t('update_found', version=latest)}{colors.RESET}")
    print(f"  {colors.DIM}{info['url']}{colors.RESET}")

    if not _confirmar(t('update_confirm', version=latest)):
        _pausar()
        return

    if not _sh.which("git"):
        print(f"{colors.ERROR}  {t('update_no_git')}{R}")
        _pausar()
        return

    print(f"\n{C}  {t('update_applying')}{R}")
    result = {}
    def _pull():
        import subprocess as _sp
        r = _sp.run(["git", "pull", "origin", "main"],
                    stdout=_sp.PIPE, stderr=_sp.STDOUT, text=True)
        result["ok"] = r.returncode == 0
        result["out"] = r.stdout.strip()

    with_spinner(t('update_applying'), _pull, C)

    if result.get("ok"):
        print(f"{colors.SUCCESS}  {t('update_ok', version=latest)}{R}")
        time.sleep(1)
        print(f"{C}  Reiniciando...{R}")
        time.sleep(0.8)
        os.execv(sys.executable, [sys.executable] + sys.argv)
    else:
        print(f"{colors.ERROR}  {t('update_err', err=result.get('out', '?'))}{R}")
    _pausar()


def configure_dependencies_hub():
    cfg = cfgmod.load_config()
    limpar_tela()
    mostrar_banner(cfg)

    found_yt = shutil.which("yt-dlp") or shutil.which(cfg.get("yt_dlp_path") or "")
    found_ff = shutil.which("ffmpeg") or shutil.which(cfg.get("ffmpeg_path") or "")
    if not found_yt and cfg.get("yt_dlp_path"):
        p = Path(cfg["yt_dlp_path"]).expanduser()
        found_yt = str(p) if p.is_file() else None
    if not found_ff and cfg.get("ffmpeg_path"):
        p = Path(cfg["ffmpeg_path"]).expanduser()
        found_ff = str(p) if p.is_file() else None

    def _ver(cmd):
        try:
            r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            line = (r.stdout or r.stderr or "").splitlines()
            return line[0].strip() if line else "ok"
        except (OSError, ValueError, IndexError):
            return "?"

    yt_ver = _ver([found_yt, "--version"]) if found_yt else None
    ff_ver = _ver([found_ff, "-version"]) if found_ff else None

    C, R = colors.CYAN, colors.RESET
    yt_c = colors.SUCCESS if found_yt else colors.ERROR
    ff_c = colors.SUCCESS if found_ff else colors.ERROR
    w = _compact_w()
    _compact_header("DEPENDENCIAS", "yt-dlp / ffmpeg / cookies", w)
    print(f"  {yt_c}yt-dlp{R} {colors.DIM}{found_yt or t('deps_not_found')}{R}")
    if yt_ver:
        print(f"  {colors.DIM}{_clip_visual(yt_ver, w)}{R}")
    print(f"  {ff_c}ffmpeg{R} {colors.DIM}{found_ff or t('deps_not_found')}{R}")
    if ff_ver:
        print(f"  {colors.DIM}{_clip_visual(ff_ver, w)}{R}")
    print(_compact_line(w))
    print(_compact_row("1", t('deps_path_ytdlp'), "caminho manual do executavel", C, w))
    print(_compact_row("2", t('deps_path_ffmpeg'), "caminho manual do executavel", C, w))
    print(_compact_row("3", t('deps_add_path'), "persistente no shell", C, w))
    print(_compact_row("4", t('deps_update_ytdlp'), "yt-dlp -U", C, w))
    cookies_atual = cfg.get("cookies_browser")
    cookies_label = cookies_atual if cookies_atual else t('deps_cookies_off')
    print(_compact_row("5", t('deps_cookies'), f"{cookies_label} / {t('deps_cookies_desc')}", C, w))
    restrict_atual = cfg.get("restrict_filenames", False)
    restrict_label = "ON" if restrict_atual else "off"
    print(_compact_row("6", t('deps_restrict'), f"{restrict_label} / {t('deps_restrict_desc')}", C, w))
    print(_compact_row("0", t('opt_back'), "hub", colors.DIM, w))
    print(_compact_line(w))

    opt = input(f"{C}  {t('prompt_choice')}: {R}").strip()
    if opt == "1":
        p = input(f"{C}  {t('deps_ytdlp_prompt')}: {R}").strip()
        if p:
            cfg["yt_dlp_path"] = p
            cfgmod.save_config(cfg)
            print(f"{colors.SUCCESS}  {t('deps_ytdlp_saved')}{R}")
    elif opt == "2":
        p = input(f"{C}  {t('deps_ffmpeg_prompt')}: {R}").strip()
        if p:
            cfg["ffmpeg_path"] = p
            cfgmod.save_config(cfg)
            print(f"{colors.SUCCESS}  {t('deps_ffmpeg_saved')}{R}")
    elif opt == "3":
        shell = os.environ.get("SHELL", "")
        rc = "~/.zshrc" if "zsh" in shell else "~/.bashrc"
        dirp = input(f"{C}  {t('deps_dir_prompt')}: {R}").strip()
        if dirp:
            rcfile = Path(rc).expanduser()
            try:
                with rcfile.open("a", encoding="utf-8") as f:
                    f.write(f'\n# ICYRIP\nexport PATH="$PATH:{dirp}"\n')
                print(f"{colors.SUCCESS}  {t('deps_path_added', rc=rcfile)}{R}")
            except Exception as e:
                print(f"{colors.ERROR}  {t('deps_path_fail', err=e)}{R}")
    elif opt == "4":
        ytdlp_bin = found_yt or "yt-dlp"
        print(f"\n{C}  {t('deps_updating')}{R}")
        try:
            r = subprocess.run([ytdlp_bin, "-U"],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            output = r.stdout.strip()
            if r.returncode == 0:
                print(f"{colors.SUCCESS}  {t('deps_update_ok', msg=output or 'yt-dlp atualizado.')}{R}")
            else:
                print(f"{colors.ERROR}  {t('deps_update_fail', msg=output or 'Falha ao atualizar.')}{R}")
        except Exception as e:
            print(f"{colors.ERROR}  {t('deps_update_err', err=e)}{R}")
    elif opt == "5":
        browsers = ["chrome", "firefox", "brave", "edge", "opera", "vivaldi", "chromium"]
        print(f"\n{C}  {t('deps_browsers')}{R}  " + "  ".join(browsers))
        b = input(f"{C}  {t('deps_browser_prompt')}: {R}").strip().lower()
        cfg["cookies_browser"] = b if b in browsers else None
        cfgmod.save_config(cfg)
        estado = f"{colors.SUCCESS}{cfg['cookies_browser']}{R}" if cfg["cookies_browser"] else f"{colors.DIM}{t('deps_cookies_off')}{R}"
        print(f"{colors.SUCCESS}  {t('deps_cookies_saved', state=estado)}{R}")
    elif opt == "6":
        cfg["restrict_filenames"] = not restrict_atual
        cfgmod.save_config(cfg)
        estado = f"{colors.SUCCESS}ON{R}" if cfg["restrict_filenames"] else f"{colors.DIM}off{R}"
        print(f"{colors.SUCCESS}  {t('deps_restrict_saved', state=estado)}{R}")
    _pausar()


def customizar_cores():
    cfg = cfgmod.load_config()
    apply_theme(cfg.get("theme", "default"))
    limpar_tela()
    mostrar_banner(cfg)
    C, R = colors.CYAN, colors.RESET

    roles = [
        ("HEADER",   "Cabeçalho / Hub banner"),
        ("ACCENT",   "Destaque / botões"),
        ("PROGRESS", "Barra de progresso"),
        ("INFO",     "Mensagens informativas"),
        ("SUCCESS",  "Sucesso"),
        ("WARN",     "Aviso"),
        ("ERROR",    "Erro"),
        ("RED",      "Vermelho"),
        ("ORANGE",   "Laranja"),
        ("CYAN",     "Ciano"),
    ]

    print(f"\n{C}  Customizar Cores{R}")
    print(_sep())
    for i, (k, desc) in enumerate(roles, 1):
        attr = getattr(colors, k, colors.CYAN)
        swatch = f"{attr}██{colors.RESET}"
        print(f"  {C}[{i:2}]{R}  {swatch}  {k:<10}  {colors.DIM}{desc}{R}")
    print(f"  {C}[ 0]{R}  Voltar")
    print(_sep())

    try:
        idx = int(input(f"\n{C}  Número: {R}").strip()) - 1
        if not 0 <= idx < len(roles):
            return
    except ValueError:
        return

    target = roles[idx][0]

    print(f"\n{C}  [{target}]{R}")
    print(_sep())
    print(f"{C}  [1]{R}  Inserir HEX  (ex: #1abc9c)")
    print(f"{C}  [2]{R}  Resetar para padrão do preset/tema")
    print(f"{C}  [0]{R}  Voltar")
    print(_sep())
    op = input(f"{C}  Escolha: {R}").strip()

    cfg_colors = cfg.get("colors", {}) or {}

    if op == "1":
        hx = input(f"{C}  HEX: {R}").strip()
        try:
            colors.hex_to_rgb(hx)
        except ValueError:
            print(f"{colors.ERROR}  HEX inválido.{R}")
            _pausar()
            return
        chosen = hx
    elif op == "2":
        cfg_colors.pop(target, None)
        cfg["colors"] = cfg_colors
        cfgmod.save_config(cfg)
        apply_theme(cfg.get("theme", "default"))
        print(f"{colors.SUCCESS}  ✔ {target} resetado.{R}")
        _pausar()
        return
    else:
        return

    ansi = colors.to_ansi(chosen)
    print(f"\n  Preview: {ansi}{'█' * 40}{colors.RESET}")
    print(f"  {ansi}Texto de exemplo — {target}{colors.RESET}")
    if not _confirmar(f"  Salvar {chosen} para {target}?"):
        return

    cfg_colors[target] = chosen
    cfg["colors"] = cfg_colors
    cfgmod.save_config(cfg)
    apply_theme(cfg.get("theme", "default"))
    print(f"{colors.SUCCESS}  ✔ {target} atualizado.{R}")
    _pausar()


def _customizar_ascii_banner(cfg: dict):
    C, R = colors.CYAN, colors.RESET
    limpar_tela()
    mostrar_banner(cfg)
    print(f"\n{C}  Banner ASCII — módulo:{R}")
    print(_sep())
    print(f"{C}  [1]{R}  Hub  [2] YouTube  [3] SoundCloud  [4] Spotify  [0] Voltar")
    print(_sep())
    sel = input(f"{C}  Escolha: {R}").strip()
    key_map = {"1": "main", "2": "ytb", "3": "sound", "4": "spotify"}
    modkey = key_map.get(sel)
    if not modkey:
        return

    print(f"\n{C}  [1]{R}  HEX manual  [2] Preset de gradiente  [3] Resetar  [0] Voltar")
    op = input(f"{C}  Escolha: {R}").strip()

    ascii_colors = cfg.get("ascii_colors", {}) or {}
    ascii_style = cfg.get("ascii_style", {}) if isinstance(cfg.get("ascii_style"), dict) else {}

    if op == "1":
        vals = input(f"{C}  START END (ex: #00bcd4 #ff6a00): {R}").strip().split()
        if len(vals) < 2:
            print(f"{colors.ERROR}  Entrada inválida.{R}")
            _pausar()
            return
        try:
            colors.hex_to_rgb(vals[0])
            colors.hex_to_rgb(vals[1])
        except ValueError:
            print(f"{colors.ERROR}  HEX inválido.{R}")
            _pausar()
            return
        print("\n  Preview: " + colors.gradient_text("█" * 40, vals[0], vals[1]))
        if not _confirmar("  Aplicar?"):
            return
        ascii_colors[modkey] = {"start": vals[0], "end": vals[1]}
        ascii_style[modkey] = "custom"
    if op == "2":
        preset_list = list(colors.PRESETS.items())
        print()
        for i, (name, data) in enumerate(preset_list, 1):
            s, e = data.get("_banner_start"), data.get("_banner_end")
            if s and e:
                swatch = colors.gradient_text("██████████", s, e)
                print(f"  {C}[{i:2}]{R}  {swatch}  {data.get('_desc', name)}")
        try:
            pidx = int(input(f"\n{C}  Número: {R}").strip()) - 1
            name, data = preset_list[pidx]
        except (ValueError, IndexError):
            print(f"{colors.ERROR}  Inválido.{R}")
            _pausar()
            return
        ascii_colors[modkey] = {"start": data["_banner_start"], "end": data["_banner_end"]}
        ascii_style[modkey] = "custom"
    elif op == "3":
        ascii_colors.pop(modkey, None)
        ascii_style[modkey] = "follow_theme"
    else:
        return

    cfg["ascii_colors"] = ascii_colors
    cfg["ascii_style"] = ascii_style
    cfgmod.save_config(cfg)
    print(f"{colors.SUCCESS}  ✔ Banner ASCII ({modkey}) atualizado.{R}")
    _pausar()


def _mostrar_historico():
    from core.utils import load_history
    C, R = colors.CYAN, colors.RESET
    limpar_tela()
    cfg = cfgmod.load_config()
    mostrar_banner(cfg)
    entries = load_history(50)
    print(_box_top())
    hl2, *_ = _box_colors()
    print(f"  {hl2}│{R}  {colors.HEADER}{t('history_title')}  {colors.DIM}({t('history_last', n=len(entries))}){R}  {hl2}│{R}")
    print(_box_mid())
    if not entries:
        print(f"  {hl2}│{R}  {colors.DIM}{t('history_empty')}{R}  {hl2}│{R}")
    else:
        for i, e in enumerate(entries, 1):
            mod_color = colors.RED if e["mod"] in ("musica", "playlist / álbum", "álbum") else colors.ORANGE
            print(f"  {hl2}│{R}  {colors.DIM}{i:2}. {e['ts']}{R}  {mod_color}{e['mod']:<10}{R}  {e['name'][:40]:<40}  {hl2}│{R}")
    print(_box_bot())

    if not entries:
        _pausar(); return

    print(f"\n  {C}[r]{R} Re-baixar entrada   {C}[p]{R} Abrir pasta   {C}[Enter]{R} Voltar")
    op = input(f"\n{C}  ❯ {R}").strip().lower()

    if op == "p":
        raw = input(f"{C}  Número da entrada: {R}").strip()
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(entries):
                pasta = entries[idx]["path"]
                try:
                    import platform as _pl
                    pasta_real = str(Path(pasta).resolve())
                    plat = _pl.system()
                    if plat == "Linux":
                        subprocess.Popen(["xdg-open", pasta_real])
                    elif plat == "Darwin":
                        subprocess.Popen(["open", pasta_real])
                    elif plat == "Windows":
                        subprocess.Popen(["explorer", pasta_real])
                    print(f"{colors.SUCCESS}  ✔ Abrindo {pasta_real}{R}")
                except Exception as ex:
                    print(f"{colors.ERROR}  Erro: {ex}{R}")
        _pausar()

    elif op == "r":
        raw = input(f"{C}  Número da entrada: {R}").strip()
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(entries):
                e = entries[idx]
                from core.utils import configurar_dependencias
                yt, ff = configurar_dependencias()
                if yt and ff:
                    from core import downloader as _dl
                    mod = e["mod"]
                    cor = colors.RED if mod in ("musica", "álbum") else colors.ORANGE
                    if mod == "musica":
                        _dl.baixar_musica(e["path"], yt, ff, cor)
                    elif mod in ("playlist", "playlist / álbum"):
                        _dl.baixar_playlist(e["path"], yt, ff, cor)
                    elif mod == "álbum":
                        _dl.baixar_album(e["path"], yt, ff, cor)
                    elif mod == "video":
                        _dl.baixar_video(e["path"], yt, ff, cor)
                    else:
                        print(f"{colors.WARN}  Re-download não suportado para '{mod}'.{R}")
                        _pausar()
        else:
            _pausar()
    else:
        pass


def _mostrar_estatisticas():
    from core.utils import compute_stats
    C, R = colors.CYAN, colors.RESET
    limpar_tela()
    cfg = cfgmod.load_config()
    mostrar_banner(cfg)
    stats = compute_stats()

    print(_box_top())
    hl2, *_ = _box_colors()
    print(f"  {hl2}│{R}  {colors.HEADER}📊  Estatísticas de Downloads{R}  {hl2}│{R}")
    print(_box_mid())

    if not stats:
        print(f"  {hl2}│{R}  {colors.DIM}Nenhum download registrado ainda.{R}  {hl2}│{R}")
        print(_box_bot())
        _pausar(); return

    w = _box_w() - 10

    def _linha(label, value):
        print(f"  {hl2}│{R}  {colors.DIM}{label:<22}{R}  {colors.BOLD}{value}{R}  {hl2}│{R}")

    _linha("Total baixado",    str(stats["total"]))
    _linha("Primeiro download", stats["primeiro"])
    _linha("Último download",   stats["ultimo"])
    _linha("Dias ativos",       str(stats["dias_ativos"]))
    _linha("Média por dia",     f"{stats['media_por_dia']} downloads")
    print(_box_mid())

    mod_icons = {
        "musica":           "🎵",
        "álbum":             "💿",
        "playlist":         "📝",
        "playlist / álbum": "📝",
        "video":            "🎥",
    }
    for mod, cnt in stats["por_modulo"].items():
        icon = mod_icons.get(mod, "•")
        bar_w = min(20, int((cnt / stats["total"]) * 20))
        bar = f"{colors.SUCCESS}{'█' * bar_w}{colors.DIM}{'░' * (20 - bar_w)}{R}"
        _linha(f"{icon}  {mod}", f"{cnt:>4}  {bar}")

    if stats.get("top_pastas"):
        print(_box_mid())
        print(f"  {hl2}│{R}  {colors.DIM}Top pastas:{R}  {hl2}│{R}")
        for path, cnt in stats["top_pastas"]:
            short = path[-45:] if isinstance(path, str) and len(path) > 45 else str(path or "")
            print(f"  {hl2}│{R}  {colors.DIM}{cnt:>4}x{R}  {short}  {hl2}│{R}")

    print(_box_bot())
    _pausar()


def menu_configuracoes():
    global _NEEDS_REDRAW
    C, R = colors.CYAN, colors.RESET
    while True:
        cfg = cfgmod.load_config()
        _NEEDS_REDRAW.clear()

        limpar_tela()
        mostrar_banner(cfg)

        preset_atual = cfg.get("preset", "—")
        lang_atual   = cfg.get("language", "pt")
        thresh       = cfg.get("playlist_warning_threshold", 50)
        verbose_atual = cfg.get("verbose", False)
        verbose_label = f"{colors.SUCCESS}ON{R}" if verbose_atual else f"{colors.DIM}off{R}"
        notif_atual   = cfg.get("notifications", True)
        notif_label   = f"{colors.SUCCESS}ON{R}" if notif_atual else f"{colors.DIM}off{R}"
        archive_atual = cfg.get("use_archive", True)
        archive_label = f"{colors.SUCCESS}ON{R}" if archive_atual else f"{colors.DIM}off{R}"

        w = _compact_w()

        _compact_header(
            f"⚙  {t('cfg_title').upper()}",
            f"{t('cfg_lang')}: {lang_atual}  ·  preset: {preset_atual}  ·  limit: {thresh}",
            w,
        )

        print(_compact_row("1", f"🌍  {t('opt_language')}",      "pt-BR / English",                      C, w))
        print(_compact_row("2", f"🎨  {t('opt_presets')}",       t('desc_presets'),                      C, w))
        print(_compact_row("3", f"🖥   {t('opt_custom_color')}", t('desc_custom_color'),                 C, w))
        print(_compact_row("4", f"🔤  {t('opt_ascii')}",         t('desc_ascii'),                        C, w))
        print(_compact_line(w))

        print(_compact_row("5", f"📊  {t('opt_pl_limit')}",      f"{t('cfg_limit')}: {thresh}",           C, w))
        print(_compact_row("6", f"🔎  {t('opt_verbose')}",       f"{t('desc_verbose')} [{verbose_label}]", C, w))
        print(_compact_row("n", f"🔔  Notificações",             f"notific. de conclusão [{notif_label}]", C, w))
        print(_compact_row("a", f"🗃   Retomar downloads",       f"download-archive [{archive_label}]",    C, w))
        print(_compact_row("p", f"💾  Perfis",                   "gerenciar perfis de download",          C, w))
        print(_compact_line(w))

        print(_compact_row("q", f"📌  Fila",                     "fila persistente de downloads",        C, w))
        print(_compact_row("s", f"📊  Estatísticas",             "resumo de todos os downloads",         C, w))
        print(_compact_line(w))

        print(_compact_row("7", f"📤  {t('opt_export')}",        "backup portavel",                     C, w))
        print(_compact_row("8", f"📥  {t('opt_import')}",        "restaurar config",                    C, w))
        print(_compact_row("9", f"⚠   {t('opt_reset')}",        t('desc_reset'),                       colors.WARN, w))
        print(_compact_row("h", f"📜  {t('opt_history')}",       t('desc_history'),                     C, w))
        print(_compact_line(w))

        print(_compact_row("0", f"←   {t('opt_back')}",         "hub",                                 colors.DIM, w))
        print(_compact_line(w))

        if _NEEDS_REDRAW.is_set():
            continue

        c = input(f"\n{C}  ❯ {R}").strip()

        if _NEEDS_REDRAW.is_set():
            continue

        if c == "1":
            cfg["language"] = escolher_idioma()
            cfgmod.save_config(cfg)
            from core.i18n import _invalidate_lang_cache
            _invalidate_lang_cache()
            print(f"{colors.SUCCESS}  {t('lang_saved', lang=cfg['language'])}{R}")
            _pausar()

        elif c == "2":
            menu_presets()
        elif c == "3":
            customizar_cores()
        elif c == "4":
            _customizar_ascii_banner(cfgmod.load_config())
        elif c == "5":
            val = input(f"{C}  {t('pl_limit_prompt', cur=thresh)}: {R}").strip()
            if val:
                try:
                    cfg["playlist_warning_threshold"] = max(1, int(val))
                    cfgmod.save_config(cfg)
                    print(f"{colors.SUCCESS}  {t('pl_limit_saved', val=cfg['playlist_warning_threshold'])}{R}")
                except ValueError:
                    print(f"{colors.ERROR}  {t('pl_limit_invalid')}{R}")
            _pausar()

        elif c == "6":
            cfg["verbose"] = not cfg.get("verbose", False)
            cfgmod.save_config(cfg)
            import core.utils as _utils
            _utils.VERBOSE = cfg["verbose"]
            estado = f"{colors.SUCCESS}ON{R}" if cfg["verbose"] else f"{colors.DIM}off{R}"
            print(f"{colors.SUCCESS}  {t('verbose_saved', state=estado)}{R}")
            _pausar()

        elif c == "n":
            cfg["notifications"] = not cfg.get("notifications", True)
            cfgmod.save_config(cfg)
            estado = f"{colors.SUCCESS}ON{R}" if cfg["notifications"] else f"{colors.DIM}off{R}"
            print(f"{colors.SUCCESS}  ✔ Notificações: {estado}{R}")
            _pausar()

        elif c == "a":
            cfg["use_archive"] = not cfg.get("use_archive", True)
            cfgmod.save_config(cfg)
            estado = f"{colors.SUCCESS}ON{R}" if cfg["use_archive"] else f"{colors.DIM}off{R}"
            print(f"{colors.SUCCESS}  ✔ Retomar downloads: {estado}{R}")
            _pausar()

        elif c == "p":
            from core.downloader import menu_perfis
            menu_perfis(C)

        elif c == "q":
            from core.utils import configurar_dependencias
            from core.downloader import menu_fila, get_pasta_salva
            yt, ff = configurar_dependencias()
            if yt and ff:
                sp = get_pasta_salva("ytb", "Músicas")
                menu_fila(yt, ff, C, sp, "musica")

        elif c == "s":
            _mostrar_estatisticas()

        elif c == "7":
            dest = input(f"{C}  {t('export_dest')}: {R}").strip()
            if dest:
                ok = cfgmod.export_config(str(Path(dest).expanduser()))
                print(f"{colors.SUCCESS if ok else colors.ERROR}  {t('export_ok') if ok else t('export_fail')}{R}")
            _pausar()

        elif c == "8":
            src = input(f"{C}  {t('import_src')}: {R}").strip()
            if src:
                ok = cfgmod.import_config(str(Path(src).expanduser()))
                if ok:
                    apply_theme(cfgmod.load_config().get("theme", "default"))
                print(f"{colors.SUCCESS if ok else colors.ERROR}  {t('import_ok') if ok else t('import_fail')}{R}")
            _pausar()

        elif c == "9":
            if _confirmar(t('reset_confirm')):
                cfgmod.reset_config()
                apply_theme("default")
                print(f"{colors.SUCCESS}  {t('reset_ok')}{R}")
            _pausar()

        elif c == "h":
            _mostrar_historico()

        elif c == "0":
            break

        else:
            print(f"{colors.WARN}  {t('invalid_option')}{R}")
            time.sleep(0.7)


def _hub_loop():
    global _NEEDS_REDRAW
    while True:
        cfg = cfgmod.load_config()
        apply_theme(cfg.get("theme", "default"))
        _NEEDS_REDRAW.clear()
        limpar_tela()
        mostrar_banner(cfg)

        C, R = colors.CYAN, colors.RESET
        hub_color = colors.HEADER
        preset_atual = cfg.get("preset", "default")
        yt_ok = bool(shutil.which("yt-dlp") or cfg.get("yt_dlp_path"))
        ff_ok = bool(shutil.which("ffmpeg") or cfg.get("ffmpeg_path"))

        from core.utils import get_update_info
        _upd = get_update_info()
        _upd_str = f"  ⚠ v{_upd['latest']} disponível" if _upd.get("has_update") else ""

        w = _compact_w()
        dep_text = "deps ok" if (yt_ok and ff_ok) else "deps faltando"

        _compact_header(
            f"✦  ICYRIP v{VERSION}  ·  HUB  ✦",
            f"by Icey  ·  preset: {preset_atual}{_upd_str}",
            w,
        )
        print(_compact_row("1", f"🎵  {t('opt_youtube')}",    t('desc_youtube'),    colors.RED,    w))
        print(_compact_row("2", f"🔊  {t('opt_soundcloud')}", t('desc_soundcloud'), colors.ORANGE, w))
        print(_compact_row("3", f"🟢  {t('opt_spotify')}",          t('desc_spotify'),   colors.to_ansi("#1DB954"), w))
        print(_compact_line(w))
        print(_compact_row("4", f"⚙️   {t('opt_settings')}",  t('desc_settings'),   C,             w))
        print(_compact_row("5", f"🔧  {t('opt_deps')}",       t('desc_deps'),       C,             w))
        print(_compact_row("6", f"🔄  {t('opt_update')}",     t('desc_update'),     C,             w))
        print(_compact_line(w))
        print(_compact_row("0", f"✕   {t('opt_exit')}",       t('opt_exit').strip(), colors.DIM,   w))


        _compact_status([
            ("ver",    VERSION),
            ("preset", f"{hub_color}{preset_atual}{colors.RESET}"),
            ("deps",   f"{colors.SUCCESS if (yt_ok and ff_ok) else colors.ERROR}{dep_text}{colors.RESET}"),
        ], w)

        if _NEEDS_REDRAW.is_set():
            continue

        opc = input(f"\n{hub_color}  ❯ {colors.RESET}").strip()

        if _NEEDS_REDRAW.is_set():
            continue

        if opc == "1":
            from core.utils import configurar_dependencias
            yt, ff = configurar_dependencias()
            if yt and ff:
                _transicao("YouTube", colors.RED)
                try:
                    import ytb
                    ytb.menu(yt, ff)
                except ImportError as e:
                    print(f"{colors.ERROR}  Erro ao importar módulo YouTube: {e}{R}")
                    _pausar()
        elif opc == "2":
            from core.utils import configurar_dependencias
            yt, ff = configurar_dependencias()
            if yt and ff:
                _transicao("SoundCloud", colors.ORANGE)
                try:
                    import sound
                    sound.menu(yt, ff)
                except ImportError as e:
                    print(f"{colors.ERROR}  Erro ao importar módulo SoundCloud: {e}{R}")
                    _pausar()
        elif opc == "3":
            from core.utils import configurar_dependencias
            yt, ff = configurar_dependencias()
            if yt and ff:
                _transicao("Spotify", colors.to_ansi("#1DB954"))
                try:
                    import spotify
                    spotify.menu(yt, ff)
                except ImportError as e:
                    print(f"{colors.ERROR}  Erro ao importar módulo Spotify: {e}{R}")
                    _pausar()
        elif opc == "4":
            menu_configuracoes()
        elif opc == "5":
            configure_dependencies_hub()
        elif opc == "6":
            _verificar_update()
        elif opc == "0":
            limpar_tela()
            cfg = cfgmod.load_config()
            mostrar_banner(cfg, animated=True)
            animate_exit(t('bye'), colors.HEADER)
            break
        else:
            print(f"{colors.WARN}  {t('invalid_option')}{R}")
            time.sleep(0.7)


def main_menu():
    global _NEEDS_REDRAW
    _setup_resize_handler()
    cfg = cfgmod.load_config()
    apply_theme(cfg.get("theme", "default"))
    prompt_startup_language_choice()

    import core.utils as _utils
    _utils.VERBOSE = cfg.get("verbose", False)

    from core.utils import check_update_async
    check_update_async(VERSION, "omgiceey/IcyRIP")

    limpar_tela()
    cfg = cfgmod.load_config()
    mostrar_banner(cfg, animated=True)
    w = min(47, _tw() - 4)
    print(f"{colors.DIM}  {'─' * w}{colors.RESET}")
    print(f"{colors.HEADER}  {t('welcome')}{VERSION}{colors.RESET}")

    yt_ok = bool(shutil.which("yt-dlp") or cfg.get("yt_dlp_path"))
    ff_ok = bool(shutil.which("ffmpeg") or cfg.get("ffmpeg_path"))
    if not yt_ok or not ff_ok:
        faltando = ", ".join((["yt-dlp"] if not yt_ok else []) + (["ffmpeg"] if not ff_ok else []))
        print(f"{colors.WARN}  {t('deps_warn', deps=faltando)}{colors.RESET}")
        print(f"{colors.DIM}  {t('deps_hint')}{colors.RESET}")

    print(f"{colors.DIM}  {'─' * w}{colors.RESET}")
    time.sleep(0.5)

    try:
        _hub_loop()
    except KeyboardInterrupt:
        print(f"\n{colors.CYAN}  {t('closing')}{colors.RESET}\n")


if __name__ == "__main__":
    main_menu()

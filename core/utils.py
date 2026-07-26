import os
import re
import sys
import json
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List, cast, Callable

VERBOSE = False


def _tw() -> int:
    try:
        return shutil.get_terminal_size((80, 20)).columns
    except Exception:
        return 80


def _ansi_rgb(r: int, g: int, b: int) -> str:
    return f"\033[38;2;{r};{g};{b}m"

def _hex_to_rgb(h: str) -> Tuple[int, int, int]:
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

def _lerp_color(t: float, sr: int, sg: int, sb: int, er: int, eg: int, eb: int) -> str:
    r = int(sr + (er - sr) * t)
    g = int(sg + (eg - sg) * t)
    b = int(sb + (eb - sb) * t)
    return _ansi_rgb(r, g, b)

RST = "\033[0m"
BOLD = "\033[1m"
DIM  = "\033[2m"

def _norm_title(s: str) -> str:
    return re.sub(r"\W+", " ", s or "").strip().lower()

_BAR_COLORS = [
    (0.0,  (0x00, 0xe5, 0x76)),
    (0.5,  (0xff, 0xd7, 0x00)),
    (1.0,  (0xff, 0x33, 0x33)),
]

def _bar_color(t: float) -> str:
    for i in range(len(_BAR_COLORS) - 1):
        t0, c0 = _BAR_COLORS[i]
        t1, c1 = _BAR_COLORS[i + 1]
        if t <= t1:
            local = (t - t0) / (t1 - t0) if t1 > t0 else 0
            return _lerp_color(local, *c0, *c1)
    return _ansi_rgb(*_BAR_COLORS[-1][1])


def parse_progress(line: str) -> Optional[Dict[str, str]]:
    m = re.search(
        r"(?P<pct>\d{1,3}(?:\.\d+)?)%.*?of\s+(?P<total>[\d\.]+[KMGT]?i?B).*?at\s+"
        r"(?P<speed>[\d\.]+[KMGT]?i?B/s).*?ETA\s+(?P<eta>\S+)", line
    )
    if m:
        return m.groupdict()
    m = re.search(
        r"(?P<pct>\d{1,3}(?:\.\d+)?)%.*?at\s+(?P<speed>[\d\.]+[KMGT]?i?B/s).*?ETA\s+(?P<eta>\S+)", line
    )
    if m:
        return {"pct": m.group("pct"), "speed": m.group("speed"),
                "eta": m.group("eta")}
    m = re.search(
        r"time=(?P<time>\S+).*?bitrate=\s*(?P<bitrate>\S+).*?speed=\s*(?P<speed>\S+)",
        line)
    if m:
        return {"time": m.group("time"), "bitrate": m.group("bitrate"), "speed": m.group("speed")}
    return None


def _parse_time_to_sec(t: str) -> Optional[float]:
    try:
        parts = t.split(":")
        if len(parts) == 3:
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        if len(parts) == 2:
            return float(parts[0]) * 60 + float(parts[1])
        return float(parts[0])
    except Exception:
        return None


def render_progress_line(pct, speed=None, eta=None, color="", width=None) -> str:
    bar_w = (width or min(40, _tw() - 30))
    try:
        p = float(pct)
    except Exception:
        return f"{color}{pct}{RST}"

    t = p / 100.0
    filled = int(t * bar_w)
    empty  = bar_w - filled

    bar_filled = ""
    for i in range(filled):
        bt = i / max(1, bar_w - 1)
        bar_filled += f"{_bar_color(bt)}█"
    bar_empty = f"{DIM}\033[38;2;60;60;60m{'░' * empty}{RST}"

    bar = bar_filled + bar_empty

    pct_color = _bar_color(t)
    pct_str   = f"{pct_color}{BOLD}{p:5.1f}%{RST}"

    parts = [pct_str]
    if speed:
        parts.append(f"{DIM}⚡ {speed}{RST}")
    if eta and eta not in ("N/A", "Unknown", "--:--"):
        parts.append(f"{DIM}⏱ {eta}{RST}")

    info = "  ".join(parts)
    return f"  [{bar}{RST}]  {info}"


def render_ffmpeg_line(current_sec: float, duration_sec: Optional[float],
                       speed: str = "", bitrate: str = "", width=None) -> str:
    bar_w = (width or min(40, _tw() - 30))

    if duration_sec and duration_sec > 0:
        t = min(1.0, current_sec / duration_sec)
        filled = int(t * bar_w)
        empty  = bar_w - filled

        bar_filled = ""
        for i in range(filled):
            bt = i / max(1, bar_w - 1)
            r = 0x00
            g = int(0x99 + (0xe5 - 0x99) * bt)
            b = 0xff
            bar_filled += f"{_ansi_rgb(r, g, b)}█"
        bar_empty = f"{DIM}\033[38;2;60;60;60m{'░' * empty}{RST}"
        bar = bar_filled + bar_empty

        pct = t * 100
        pct_str = f"\033[38;2;0;200;255m{BOLD}{pct:5.1f}%{RST}"
    else:
        bar = f"\033[38;2;0;200;255m{'█' * (bar_w // 2)}{'░' * (bar_w - bar_w // 2)}{RST}"
        pct_str = f"\033[38;2;0;200;255m{BOLD}  ...{RST}"

    def _fmt_sec(s: float) -> str:
        m, sc = divmod(int(s), 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}:{sc:02d}" if h else f"{m:02d}:{sc:02d}"

    time_str = _fmt_sec(current_sec)
    dur_str  = f"/ {_fmt_sec(duration_sec)}" if duration_sec else ""

    parts = [pct_str, f"{DIM}⏱ {time_str} {dur_str}{RST}"]
    if speed and speed not in ("N/A", "0x"):
        parts.append(f"{DIM}⚡ {speed}{RST}")
    if bitrate and bitrate not in ("N/A",):
        parts.append(f"{DIM}♪ {bitrate}{RST}")

    return f"  [{bar}{RST}]  {'  '.join(parts)}"


_SPINNER = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

class _Spinner:
    def __init__(self, label: str, color: str = "\033[38;2;0;200;255m"):
        self._label = label
        self._color = color
        self._stop  = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        i = 0
        while not self._stop.is_set():
            frame = _SPINNER[i % len(_SPINNER)]
            sys.stdout.write(f"\r  {self._color}{frame}{RST}  {self._label}")
            sys.stdout.flush()
            time.sleep(0.08)
            i += 1

    def start(self):
        self._thread.start()

    def stop(self, success: bool = True):
        self._stop.set()
        self._thread.join()
        icon = f"\033[38;2;0;230;118m✔{RST}" if success else f"\033[38;2;255;50;50m✗{RST}"
        sys.stdout.write(f"\r  {icon}  {self._label}\n")
        sys.stdout.flush()


def resolver_ffmpeg_location(ffmpeg_path: str) -> str:
    if not ffmpeg_path:
        return ffmpeg_path
    if os.path.isdir(ffmpeg_path):
        return ffmpeg_path
    if os.path.isabs(ffmpeg_path) or os.path.sep in ffmpeg_path:
        d = os.path.dirname(ffmpeg_path)
        return d if d else ffmpeg_path
    found = shutil.which(ffmpeg_path)
    if found:
        return os.path.dirname(found)
    return ffmpeg_path


def localizar_executavel(user_input: Optional[str], default_name: str) -> Optional[str]:
    if user_input:
        p = Path(user_input).expanduser()
        if p.is_file() and os.access(str(p), os.X_OK):
            return str(p)
        if p.is_dir():
            cand = p / default_name
            if cand.is_file() and os.access(str(cand), os.X_OK):
                return str(cand)
    return shutil.which(default_name)


def safe_join(base: str, *parts: str) -> str:
    base_path = Path(base).resolve()
    joined    = base_path.joinpath(*parts).resolve()
    if not str(joined).startswith(str(base_path) + os.sep) and joined != base_path:
        raise ValueError(f"Caminho inválido: {joined}")
    return str(joined)


def sanitize_folder(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|]+', "-", name).strip()


def get_playlist_info(yt_dlp_path: str, url: str) -> Dict[str, Any]:
    try:
        proc = subprocess.run(
            [yt_dlp_path, "--dump-single-json", "--flat-playlist", url],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60
        )
        if proc.returncode != 0:
            return {}
        obj = json.loads(proc.stdout)
        entries = obj.get("entries") or []
        titles  = [e.get("title") or e.get("id") for e in entries]
        title   = obj.get("title") or obj.get("playlist_title")
        return {"title": title, "entries": titles}
    except Exception:
        return {}


def get_playlist_entries(yt_dlp_path: str, url: str) -> List[str]:
    try:
        proc = subprocess.run(
            [yt_dlp_path, "--flat-playlist", "--dump-json", url],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60
        )
        if proc.returncode != 0:
            return []
        titles = []
        for line in proc.stdout.splitlines():
            try:
                obj = json.loads(line)
            except Exception:
                continue
            titles.append(obj.get("title") or obj.get("fulltitle") or obj.get("id"))
        return titles
    except Exception:
        return []


def get_playlist_title(yt_dlp_path: str, url: str) -> Optional[str]:
    try:
        proc = subprocess.run(
            [yt_dlp_path, "--dump-single-json", "--flat-playlist", url],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=60
        )
        if proc.returncode != 0:
            return None
        obj = json.loads(proc.stdout)
        return obj.get("title") or obj.get("playlist_title")
    except Exception:
        return None


def get_playlist_stats(yt_dlp_path: str, url: str) -> Dict[str, Any]:
    empty = {"count": None, "total_duration": None, "total_size": None}
    try:
        proc = subprocess.run(
            [yt_dlp_path, "--dump-json", url],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=120
        )
        if proc.returncode != 0:
            return empty

        total_duration = total_size = count = 0
        any_dur = any_size = False

        for line in proc.stdout.splitlines():
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            count += 1
            dur = obj.get("duration")
            if isinstance(dur, (int, float)):
                total_duration += int(dur)
                any_dur = True
            size = obj.get("filesize") or obj.get("filesize_approx")
            if isinstance(size, (int, float)):
                total_size += int(size)
                any_size = True
            else:
                best = max(
                    (f.get("filesize") or f.get("filesize_approx") or 0
                     for f in (obj.get("formats") or [])),
                    default=0
                )
                if best:
                    total_size += int(best)
                    any_size = True

        return {
            "count": count or None,
            "total_duration": total_duration if any_dur else None,
            "total_size": total_size if any_size else None,
        }
    except Exception:
        return empty


def _format_bytes(n: Optional[int]) -> Optional[str]:
    if n is None:
        return None
    n_float = float(n)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n_float < 1024.0:
            return f"{n_float:.1f} {unit}"
        n_float /= 1024.0
    return f"{n_float:.1f} PB"


def _format_duration(s: Optional[int]) -> Optional[str]:
    if s is None:
        return None
    m, sec = divmod(int(s), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m}m {sec}s"
    if m:
        return f"{m}m {sec}s"
    return f"{sec}s"


def validar_dependencia(comando: List[str], nome: str) -> bool:
    try:
        proc = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, timeout=10)
        if proc.returncode == 0:
            return True
        print(f"  {nome} falhou. Saída: {proc.stderr.strip()}")
    except FileNotFoundError:
        print(f"  {nome} não encontrado. Instale ou configure o caminho.")
    except Exception as e:
        print(f"  Erro ao validar {nome}: {e}")
    return False


def configurar_dependencias() -> Tuple[Optional[str], Optional[str]]:
    try:
        from core import config as _cfg
        cfg = _cfg.load_config()
    except Exception:
        cfg = {}

    yt_dlp_path = cfg.get("yt_dlp_path") or shutil.which("yt-dlp")
    ffmpeg_path = cfg.get("ffmpeg_path") or shutil.which("ffmpeg")

    faltando = []
    if not yt_dlp_path or not validar_dependencia([yt_dlp_path, "--version"], "yt-dlp"):
        faltando.append("yt-dlp")
    if not ffmpeg_path or not validar_dependencia([ffmpeg_path, "-version"], "ffmpeg"):
        faltando.append("ffmpeg")

    if faltando:
        nomes = ", ".join(faltando)
        print(f"\n  \033[38;2;255;80;80m✗{RST}  Dependência(s) não encontrada(s): {BOLD}{nomes}{RST}")
        print(f"  {DIM}Configure em HUB → [4] Dependências antes de baixar.{RST}")
        return None, None

    return yt_dlp_path, ffmpeg_path


def _print_track_header(title: str, idx: Optional[int], total: Optional[int]):
    w = _tw()
    sys.stdout.write(f"\n  {DIM}{'·' * min(50, w - 4)}{RST}\n")
    prefix = f"\033[38;2;150;150;150m[{idx}/{total}]{RST}  " if idx and total else ""
    name = os.path.splitext(title)[0]
    max_len = w - 12
    if len(name) > max_len:
        name = name[:max_len - 1] + "…"
    sys.stdout.write(f"  {prefix}\033[38;2;220;220;220m{BOLD}{name}{RST}\n")
    sys.stdout.flush()


def executar_comando(
    comando: List[str],
    mensagem_erro: str,
    entries_list: Optional[List[str]] = None,
) -> Tuple[bool, Optional[str]]:
    try:
        p = subprocess.Popen(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert p.stdout is not None

        pct          = None
        current_title = None
        printed_title = False
        idx = total   = None
        other_lines: List[str] = []
        _start_time   = time.time()
        _completed    = 0
        _errors       = 0

        ffmpeg_duration: Optional[float] = None
        in_ffmpeg_phase  = False
        ffmpeg_label     = ""
        spinner: Optional[_Spinner] = None
        last_ffmpeg_line = ""

        for line in p.stdout:
            line = line.rstrip("\n")

            m_idx = re.search(
                r"Downloading (?:video|playlist item) (?P<idx>\d+) of (?P<total>\d+)", line
            )
            if m_idx:
                try:
                    idx   = int(m_idx.group("idx"))
                    total = int(m_idx.group("total"))
                except Exception:
                    idx = total = None

            m_dest = re.search(r"\[download\] Destination: (?P<path>.+)$", line) or \
                     re.search(r"Destination: (?P<path>.+)$", line)
            if m_dest:
                current_title = os.path.basename(m_dest.group("path").strip())
                printed_title = False
                in_ffmpeg_phase = False
                ffmpeg_duration = None

                if entries_list and not idx:
                    cur = _norm_title(os.path.splitext(current_title)[0])
                    for i, e in enumerate(entries_list):
                        if e and (cur in _norm_title(e) or _norm_title(e) in cur):
                            idx   = i + 1
                            total = len(entries_list)
                            break

            m_ffmpeg_start = re.search(
                r"\[ffmpeg\].*?(?:Destination|Converting|Merging|Embedding)", line, re.IGNORECASE
            )
            if m_ffmpeg_start:
                in_ffmpeg_phase = True
                if pct is not None:
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    pct = None

                fname = current_title or ""
                name  = os.path.splitext(fname)[0]
                ffmpeg_label = f"Convertendo  {DIM}{name}{RST}"
                sys.stdout.write(f"\n  \033[38;2;0;200;255m⚙{RST}  {ffmpeg_label}\n")
                sys.stdout.flush()
                continue

            m_dur = re.search(r"Duration:\s*(\d+:\d+:\d+(?:\.\d+)?)", line)
            if m_dur and in_ffmpeg_phase:
                ffmpeg_duration = _parse_time_to_sec(m_dur.group(1))

            prog = parse_progress(line)

            if prog and "time" in prog:
                in_ffmpeg_phase = True
                cur_sec = _parse_time_to_sec(prog["time"]) or 0
                speed   = prog.get("speed", "")
                bitrate = prog.get("bitrate", "")
                bar_line = render_ffmpeg_line(cur_sec, ffmpeg_duration, speed, bitrate)
                sys.stdout.write(f"\r{bar_line}   ")
                sys.stdout.flush()
                last_ffmpeg_line = bar_line
                continue

            if prog and "pct" in prog:
                in_ffmpeg_phase = False
                pct   = prog.get("pct")
                speed = prog.get("speed")
                eta   = prog.get("eta")

                if current_title and not printed_title:
                    _print_track_header(current_title, idx, total)
                    printed_title = True
                    sys.stdout.write(render_progress_line(pct, speed=speed, eta=eta))
                else:
                    sys.stdout.write("\r" + render_progress_line(pct, speed=speed, eta=eta))
                sys.stdout.flush()
                continue

            if VERBOSE:
                print(line)
            else:
                other_lines.append(line)

            if "[download] 100%" in line or "has already been downloaded" in line:
                if current_title:
                    _completed += 1
                    current_title = None
            if "has already been downloaded" in line and not VERBOSE:
                fname = re.search(r"\[download\] (.+) has already been downloaded", line)
                label = fname.group(1) if fname else "arquivo"
                name  = os.path.splitext(os.path.basename(label))[0]
                sys.stdout.write(f"  \033[38;2;255;215;0m⏭  Pulado (já existe): {DIM}{name}{RST}\n")
                sys.stdout.flush()
            if "ERROR:" in line or ("error" in line.lower() and "[download]" in line):
                _errors += 1
                if not VERBOSE:
                    _hints = [
                        ("unable to extract",         "Faixa não encontrada no YouTube Music."),
                        ("no video formats found",    "Faixa não encontrada no YouTube Music."),
                        ("this video is unavailable", "Vídeo indisponível no YouTube Music."),
                        ("video unavailable",         "Vídeo indisponível no YouTube Music."),
                        ("sign in to confirm",        "Bloqueado por verificação de idade — configure cookies no HUB → Dependências."),
                        ("private video",             "Vídeo privado — não é possível baixar."),
                        ("members-only",              "Conteúdo exclusivo para membros."),
                    ]
                    for pattern, hint in _hints:
                        if pattern in line.lower():
                            sys.stdout.write(f"  \033[38;2;255;80;80m✗{RST}  {hint}\n")
                            sys.stdout.flush()
                            break

        p.wait()

        if pct is not None or last_ffmpeg_line:
            sys.stdout.write("\n")
            sys.stdout.flush()

        elapsed = time.time() - _start_time

        if p.returncode == 0:
            if entries_list and len(entries_list) > 1:
                real_total = _completed if _completed > 0 else len(entries_list)
                print_download_summary(real_total, _errors, elapsed)
            return True, current_title

        print(f"\n  \033[38;2;255;50;50m✗{RST}  {mensagem_erro}")
        if other_lines and VERBOSE:
            print("\n".join(other_lines[-10:]))
        return False, None

    except FileNotFoundError:
        print(f"  Comando não encontrado: {comando[0]}")
        return False, None
    except Exception as e:
        print(f"  Erro ao executar comando: {e}")
        return False, None


def executar_ffmpeg_conversao(
    comando: List[str],
    mensagem_erro: str,
    label: str = "Convertendo...",
) -> bool:
    duration_sec: Optional[float] = None
    try:
        input_file = None
        for i, arg in enumerate(comando):
            if arg == "-i" and i + 1 < len(comando):
                input_file = comando[i + 1]
                break
        if input_file:
            probe = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", input_file],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if probe.returncode == 0:
                duration_sec = float(probe.stdout.strip())
    except Exception:
        pass

    sys.stdout.write(f"\n  \033[38;2;0;200;255m⚙{RST}  {label}\n")
    sys.stdout.flush()

    last_line = ""
    spinner: Optional[_Spinner] = None

    if duration_sec is None:
        spinner = _Spinner(label)
        spinner.start()

    try:
        p = subprocess.Popen(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert p.stdout is not None

        for line in p.stdout:
            line = line.rstrip("\n")

            if duration_sec is None:
                m_dur = re.search(r"Duration:\s*(\d+:\d+:\d+(?:\.\d+)?)", line)
                if m_dur:
                    duration_sec = _parse_time_to_sec(m_dur.group(1))
                    if duration_sec and spinner:
                        spinner.stop(success=True)
                        spinner = None
                        sys.stdout.write(f"\n  \033[38;2;0;200;255m⚙{RST}  {label}\n")
                        sys.stdout.flush()

            prog = parse_progress(line)
            if prog and "time" in prog:
                if spinner:
                    continue
                cur_sec = _parse_time_to_sec(prog["time"]) or 0
                speed   = prog.get("speed", "")
                bitrate = prog.get("bitrate", "")
                bar_line = render_ffmpeg_line(cur_sec, duration_sec, speed, bitrate)
                sys.stdout.write(f"\r{bar_line}   ")
                sys.stdout.flush()
                last_line = bar_line

        p.wait()

        if spinner:
            spinner.stop(success=(p.returncode == 0))
        elif last_line:
            sys.stdout.write("\n")
            sys.stdout.flush()

        if p.returncode == 0:
            return True
        print(f"\n  \033[38;2;255;50;50m✗{RST}  {mensagem_erro}")
        return False

    except FileNotFoundError:
        if spinner:
            spinner.stop(success=False)
        print(f"  ffmpeg não encontrado: {comando[0]}")
        return False
    except Exception as e:
        if spinner:
            spinner.stop(success=False)
        print(f"  Erro: {e}")
        return False


def center_text(text: str) -> str:
    try:
        width = shutil.get_terminal_size((80, 20)).columns
    except Exception:
        width = 80
    lines = text.splitlines()
    max_len = max((len(l) for l in lines), default=0)
    pad = max(0, (width - max_len) // 2)
    return "\n".join(" " * pad + line for line in lines)


def prompt_input(label: str, color: str = "", icon: str = "▶") -> str:
    C = color or "\033[38;2;150;150;150m"
    print(f"  {C}╭─ {label}{RST}")
    val = input(f"  {C}╰{icon} {RST}")
    return val.strip()


def with_spinner(label: str, fn: Callable, color: str = "\033[38;2;0;200;255m") -> Any:
    result: list = [None]
    error: list = [None]

    def _run():
        try:
            result[0] = fn()
        except BaseException as e:
            error[0] = e

    t = threading.Thread(target=_run, daemon=True)
    t.start()

    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    i = 0
    while t.is_alive():
        sys.stdout.write(f"\r  {color}{frames[i % len(frames)]}{RST}  {label}")
        sys.stdout.flush()
        time.sleep(0.08)
        i += 1

    t.join()
    icon = f"{RST}" if error[0] else f"{color}✔{RST}"
    sys.stdout.write(f"\r  {icon}  {label}\n")
    sys.stdout.flush()

    if error[0] is not None:
        raise error[0]
    return result[0]


def animate_banner_in(banner: str, start_hex: str, end_hex: str, delay: float = 0.018):
    try:
        from core.colors import hex_to_rgb, RESET as _RST
        sr, sg, sb = hex_to_rgb(start_hex)
        er, eg, eb = hex_to_rgb(end_hex)
    except Exception:
        print(banner)
        return

    lines = banner.splitlines()
    total = max(1, len(lines) - 1)
    for i, line in enumerate(lines):
        t = i / total
        r = int(sr + (er - sr) * t)
        g = int(sg + (eg - sg) * t)
        b = int(sb + (eb - sb) * t)
        colored_line = f"\033[38;2;{r};{g};{b}m{line}{_RST}"
        print(colored_line)
        sys.stdout.flush()
        time.sleep(delay)


def animate_exit(message: str = "Bye!", color: str = "\033[38;2;0;200;255m"):
    sys.stdout.write(f"\n  {color}")
    for ch in message:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(0.045)
    sys.stdout.write(f"  ✦{RST}\n\n")
    sys.stdout.flush()
    time.sleep(0.3)


def _box_colors_from_cfg(start_hex: str, end_hex: str):
    try:
        from core.colors import to_ansi
        return to_ansi(start_hex), to_ansi(end_hex)
    except Exception:
        return "", ""


def box_top(start_hex: str, end_hex: str, width: int = 0) -> str:
    w = (width or min(_tw(), 72)) - 4
    hl, hr = _box_colors_from_cfg(start_hex, end_hex)
    try:
        from core.colors import gradient_line
        line = gradient_line(w - 2, start_hex, end_hex, "─")
    except Exception:
        line = "─" * (w - 2)
    return f"  {hl}╭─{RST}{line}{hr}╮{RST}"


def box_bot(start_hex: str, end_hex: str, width: int = 0) -> str:
    w = (width or min(_tw(), 72)) - 4
    hl, hr = _box_colors_from_cfg(start_hex, end_hex)
    try:
        from core.colors import gradient_line
        line = gradient_line(w - 2, start_hex, end_hex, "─")
    except Exception:
        line = "─" * (w - 2)
    return f"  {hl}╰─{RST}{line}{hr}╯{RST}"


def box_mid(start_hex: str, end_hex: str, width: int = 0) -> str:
    w = (width or min(_tw(), 72)) - 4
    hl, hr = _box_colors_from_cfg(start_hex, end_hex)
    try:
        from core.colors import gradient_line
        line = gradient_line(w - 2, start_hex, end_hex, "─")
    except Exception:
        line = "─" * (w - 2)
    return f"  {hl}├─{RST}{line}{hr}┤{RST}"


def _vis_len(s: str) -> int:
    import unicodedata
    w = 0
    for ch in s:
        eaw = unicodedata.east_asian_width(ch)
        w += 2 if eaw in ('W', 'F') or ord(ch) > 0x1F000 else 1
    return w


def _strip_ansi(s: str) -> str:
    return re.sub(r"\033\[[0-9;]*m", "", s or "")


def _clip_visual(s: str, width: int) -> str:
    if width <= 0 or _vis_len(s) <= width:
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
    return s + (" " * max(0, width - _vis_len(s)))


def _center_visual(s: str, width: int) -> str:
    pad = max(0, width - _vis_len(s))
    return (" " * (pad // 2)) + s + (" " * (pad - pad // 2))


def compact_width() -> int:
    return max(42, min(_tw() - 4, 74))


def compact_line(width: int = 0, char: str = "─") -> str:
    w = width or compact_width()
    try:
        from core import config as _cfg
        from core.colors import gradient_line as _gl, theme_color as _tc
        cfg = _cfg.load_config()
        s = _tc(cfg, "HEADER")
        e = _tc(cfg, "ACCENT")
        return "  " + _gl(w, s, e, char)
    except Exception:
        return f"  {DIM}{char * w}{RST}"


def compact_header(title: str, subtitle: str = "", color: str = "", width: int = 0):
    w = width or compact_width()
    c = color or ""
    print(compact_line(w))
    try:
        from core import config as _cfg
        from core.colors import gradient_text as _gt, theme_color as _tc
        cfg = _cfg.load_config()
        s = _tc(cfg, "HEADER")
        e = _tc(cfg, "ACCENT")
        title_line = f"  {BOLD}{_gt(title, s, e)}{RST}"
    except Exception:
        title_line = f"  {c}{BOLD}{title}{RST}"
    print(title_line)
    if subtitle:
        print(f"  {DIM}{_center_visual(subtitle, w)}{RST}")
    print(compact_line(w))


def compact_row(key: str, label: str, desc: str, key_color: str, width: int = 0) -> str:
    w = width or compact_width()
    label = _strip_ansi(label or "").strip()
    desc = _strip_ansi(desc or "").strip()
    key_s = f"[{key}]"
    if w < 58:
        return f"  {key_color}{key_s:<4}{RST} {BOLD}{_clip_visual(label, w - 11)}{RST}"
    label_w = 26
    desc_w = max(8, w - label_w - 12)
    return (
        f"  {key_color}{key_s:<5}{RST}"
        f"{BOLD}{_pad_visual(_clip_visual(label, label_w), label_w)}{RST}"
        f"  {DIM}{_clip_visual(desc, desc_w)}{RST}"
    )


def box_row(key: str, label: str, desc: str, key_color: str,
            start_hex: str, end_hex: str, width: int = 0) -> str:
    hl, _ = _box_colors_from_cfg(start_hex, end_hex)
    bw = (width or min(_tw(), 72)) - 4
    usable = max(20, bw - 15)
    label_col = max(16, int(usable * 0.38))
    desc_col  = max(0,  usable - label_col - 2)

    label_vis = _vis_len(label)
    pad = max(0, label_col - label_vis)
    desc_trunc = desc[:desc_col] if _vis_len(desc) > desc_col else desc
    desc_pad = max(0, desc_col - _vis_len(desc_trunc))

    return (
        f"  {hl}│{RST}  "
        f"{key_color}{key:<3}{RST}  "
        f"{label}{' ' * pad}  "
        f"{DIM}{desc_trunc}{RST}"
        f"{' ' * desc_pad}  {hl}│{RST}"
    )


def _queue_path():
    p = Path.home() / ".config" / "icyrip"
    p.mkdir(parents=True, exist_ok=True)
    return p / "queue.json"


def load_queue() -> list:
    try:
        import json as _j
        data = _j.loads(_queue_path().read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def save_queue(queue: list):
    try:
        import json as _j
        _queue_path().write_text(_j.dumps(queue, indent=2, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


def enqueue(item: dict):
    q = load_queue()
    q.append(item)
    save_queue(q)


def dequeue() -> Optional[dict]:
    q = load_queue()
    if not q:
        return None
    item = q.pop(0)
    save_queue(q)
    return item


def remove_from_queue(idx: int):
    q = load_queue()
    if 0 <= idx < len(q):
        q.pop(idx)
        save_queue(q)


def clear_queue():
    save_queue([])


def compute_stats() -> dict:
    try:
        lines = _history_path().read_text(encoding="utf-8").splitlines()
    except Exception:
        return {}

    from collections import Counter
    import datetime

    total      = 0
    por_modulo: Counter = Counter()
    pastas:     Counter = Counter()
    datas:      list    = []

    for line in lines:
        parts = line.split("\t", 4)
        if len(parts) != 5:
            continue
        ts, mod, _, path, _ = parts
        total += 1
        por_modulo[mod] += 1
        pastas[path]    += 1
        try:
            datas.append(datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M"))
        except Exception:
            pass

    if not total:
        return {}

    datas.sort()
    dias_unicos = len({d.date() for d in datas})
    return {
        "total":        total,
        "por_modulo":   dict(por_modulo.most_common()),
        "top_pastas":   pastas.most_common(3),
        "primeiro":     datas[0].strftime("%Y-%m-%d") if datas else "—",
        "ultimo":       datas[-1].strftime("%Y-%m-%d") if datas else "—",
        "dias_ativos":  dias_unicos,
        "media_por_dia": round(total / dias_unicos, 1) if dias_unicos else 0,
    }


def _history_path() -> Path:
    p = Path.home() / ".config" / "icyrip"
    p.mkdir(parents=True, exist_ok=True)
    return p / "history.txt"


def record_download(url: str, title: Optional[str], save_path: str, modulo: str):
    try:
        import datetime
        ts   = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        name = (title or url)[:80]
        with _history_path().open("a", encoding="utf-8") as f:
            f.write(f"{ts}\t{modulo}\t{name}\t{save_path}\t{url}\n")
    except Exception:
        pass


def load_history(limit: int = 50) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    try:
        lines = _history_path().read_text(encoding="utf-8").splitlines()
        for line in reversed(lines[-limit:]):
            parts = line.split("\t", 4)
            if len(parts) == 5:
                ts, mod, name, path, _ = parts
                out.append({"ts": ts, "mod": mod, "name": name, "path": path})
    except Exception:
        pass
    return out


def notify(title: str, body: str = ""):
    try:
        from core import config as _cfg
        if not _cfg.load_config().get("notifications", True):
            return
    except Exception:
        return
    import platform
    def _send():
        try:
            s = platform.system()
            if s == "Linux":
                subprocess.run(["notify-send", title, body],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif s == "Darwin":
                safe_title = title.replace('"', '\\"')
                safe_body  = body.replace('"', '\\"')
                script = f'display notification "{safe_body}" with title "{safe_title}"'
                subprocess.run(["osascript", "-e", script],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif s == "Windows":
                try:
                    import importlib
                    winotify = importlib.import_module('winotify')
                    Notification = getattr(winotify, 'Notification', None)
                    if Notification:
                        n = Notification(app_id="ICYRIP", title=title, msg=body)
                        n.show()
                except Exception:
                    pass
        except Exception:
            pass
    threading.Thread(target=_send, daemon=True).start()


_UPDATE_CACHE: dict = {}
_UPDATE_LOCK = threading.Lock()

def check_update_async(current_version: str, repo: str = "icey/icyrip"):
    def _check():
        try:
            import urllib.request, json as _json
            url = f"https://api.github.com/repos/{repo}/releases/latest"
            req = urllib.request.Request(url, headers={"User-Agent": "ICYRIP"})
            with urllib.request.urlopen(req, timeout=4) as r:
                data = _json.loads(r.read())
            latest = data.get("tag_name", "").lstrip("v")
            with _UPDATE_LOCK:
                _UPDATE_CACHE["latest"] = latest
                _UPDATE_CACHE["has_update"] = latest != current_version and bool(latest)
                _UPDATE_CACHE["url"] = data.get("html_url", "")
        except Exception:
            pass
    threading.Thread(target=_check, daemon=True).start()


def get_update_info() -> dict:
    with _UPDATE_LOCK:
        return _UPDATE_CACHE.copy()


def fetch_url_preview(yt_dlp_path: str, url: str) -> dict:
    try:
        proc = subprocess.run(
            [yt_dlp_path, "--dump-single-json", "--no-playlist", url],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15
        )
        if proc.returncode != 0:
            return {}
        import json as _json
        obj = _json.loads(proc.stdout)
        dur = obj.get("duration")
        m, s = divmod(int(dur), 60) if dur else (0, 0)
        h, m = divmod(m, 60)
        dur_str = (f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}") if dur else "—"
        return {
            "title":    obj.get("title") or obj.get("fulltitle") or "—",
            "uploader": obj.get("uploader") or obj.get("channel") or "—",
            "duration": dur_str,
            "views":    obj.get("view_count"),
        }
    except Exception:
        return {}


def get_archive_path(save_path: str) -> str:
    return os.path.join(save_path, ".icyrip_archive")


def print_download_summary(total: int, errors: int, elapsed: float, color: str = ""):
    ok = total - errors
    ok_c  = "\033[38;2;0;230;118m"
    err_c = "\033[38;2;255;80;80m"
    dim_c = DIM

    m, s = divmod(int(elapsed), 60)
    h, m = divmod(m, 60)
    time_str = (f"{h}h {m}m {s}s" if h else
                (f"{m}m {s}s" if m else f"{s}s"))

    w = min(50, _tw() - 4)
    sep = f"  {dim_c}{'─' * w}{RST}"
    print(f"\n{sep}")
    print(f"  {ok_c}✔  {ok} concluído{'s' if ok != 1 else ''}{RST}", end="")
    if errors:
        print(f"   {err_c}✗  {errors} erro{'s' if errors != 1 else ''}{RST}", end="")
    print(f"   {dim_c}⏱  {time_str}{RST}")
    print(sep)

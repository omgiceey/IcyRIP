
import os
import platform
import re
import shutil
import sys
import time
from pathlib import Path

import core.colors as colors
import core.config as cfgmod
from core.i18n import t, tl
from core.utils import (
    resolver_ffmpeg_location,
    get_playlist_info,
    get_playlist_entries,
    get_playlist_stats,
    get_playlist_title,
    safe_join,
    sanitize_folder,
    _format_bytes,
    _format_duration,
    configurar_dependencias,
    executar_comando,
    executar_ffmpeg_conversao,
    prompt_input,
    with_spinner,
    record_download,
    notify,
    fetch_url_preview,
    get_archive_path,
    enqueue,
    load_queue,
    dequeue,
    remove_from_queue,
    clear_queue,
)

FORMATOS_AUDIO  = ["mp3", "wav", "flac", "ogg", "opus", "aac", "m4a"]
FORMATOS_VIDEO  = ["mp4", "mkv", "webm"]
QUALIDADE_AUDIO = [
    ("1", "Melhor (VBR 0 ~320k)",  "0"),
    ("2", "Alta   (VBR 2 ~190k)",  "2"),
    ("3", "Média  (VBR 4 ~165k)",  "4"),
    ("4", "128 kbps",              "128K"),
    ("5", "96 kbps",               "96K"),
]


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


def _tw() -> int:
    try:
        return shutil.get_terminal_size((80, 20)).columns
    except Exception:
        return 80


def sep(color_start: str, color_end: str) -> str:
    try:
        w = _tw() - 4
        return "  " + colors.gradient_line(w, color_start, color_end)
    except Exception:
        return f"  {color_start}{'─' * 45}{colors.RESET}"


def pausar(cor: str):
    input(f"\n{cor}  Pressione Enter para continuar...{colors.RESET}")


def confirmar(pergunta: str, cor: str) -> bool:
    from core.i18n import t
    return input(f"{cor}{pergunta} {t('confirm_yn_dl')}: {colors.RESET}").strip().lower().startswith(t('yes_key_dl'))


def _validar_url(url: str) -> bool:
    if not url.startswith(("http://", "https://")) or "." not in url:
        print(f"{colors.ERROR}  ⚠  URL inválida. Use um link completo (https://...).{colors.RESET}")
        return False
    return True


def _validar_tempo(t: str) -> bool:
    return bool(re.fullmatch(r"(\d{1,2}:)?\d{1,2}:\d{2}", t.strip()))


def configurar_pasta(modulo: str, cor: str, pasta_padrao_nome: str = "Músicas") -> str:
    cfg = cfgmod.load_config()
    pastas = cfg.get("save_paths", {}) or {}
    atual = pastas.get(modulo)

    if not atual:
        sistema = platform.system()
        base = Path.home() / ("Downloads" if sistema == "Windows" else "")
        atual = str((base / pasta_padrao_nome).resolve()).replace("//", "/")

    print(f"\n{cor}  Pasta atual: {colors.DIM}{atual}{colors.RESET}")
    novo = prompt_input("Novo caminho  (Enter = manter atual)", cor)

    save_dir = Path(novo).expanduser().resolve() if novo else Path(atual)
    save_dir.mkdir(parents=True, exist_ok=True)

    pastas[modulo] = str(save_dir)
    cfg["save_paths"] = pastas
    cfgmod.save_config(cfg)

    print(f"{colors.SUCCESS}  ✔ Pasta: {save_dir}{colors.RESET}")
    return str(save_dir)


def get_pasta_salva(modulo: str, pasta_padrao_nome: str = "Músicas") -> str:
    cfg = cfgmod.load_config()
    pastas = cfg.get("save_paths", {}) or {}
    if modulo in pastas:
        pasta = pastas[modulo]
        Path(pasta).mkdir(parents=True, exist_ok=True)
        return pasta
    sistema = platform.system()
    base = Path.home() / ("Downloads" if sistema == "Windows" else "")
    return str((base / pasta_padrao_nome).resolve()).replace("//", "/")


def build_postproc(embutir: bool) -> list:
    pp = ["--add-metadata"]
    if embutir:
        pp.append("--embed-thumbnail")
    return pp


def _get_cookies_args() -> list:
    try:
        cfg = cfgmod.load_config()
        browser = cfg.get("cookies_browser")
        if browser:
            return ["--cookies-from-browser", browser]
    except Exception:
        pass
    return []


def _get_archive_args(save_path: str) -> list:
    try:
        if cfgmod.load_config().get("use_archive", True):
            return ["--download-archive", get_archive_path(save_path)]
    except Exception:
        pass
    return []


def listar_perfis() -> dict:
    try:
        return cfgmod.load_config().get("profiles", {}) or {}
    except Exception:
        return {}


def salvar_perfil(nome: str, dados: dict):
    cfg = cfgmod.load_config()
    perfis = cfg.get("profiles", {}) or {}
    perfis[nome] = dados
    cfg["profiles"] = perfis
    cfgmod.save_config(cfg)


def deletar_perfil(nome: str):
    cfg = cfgmod.load_config()
    perfis = cfg.get("profiles", {}) or {}
    perfis.pop(nome, None)
    cfg["profiles"] = perfis
    cfgmod.save_config(cfg)


def escolher_perfil(cor: str) -> dict | None:
    perfis = listar_perfis()
    if not perfis:
        return None
    _s = _theme_sep()
    print(f"\n{_s}")
    print(f"  {cor}Perfis salvos:{colors.RESET}")
    nomes = list(perfis.keys())
    for i, nome in enumerate(nomes, 1):
        p = perfis[nome]
        desc = f"{p.get('formato','?').upper()} · {p.get('qualidade_label','?')} · capa={'sim' if p.get('embutir') else 'não'}"
        print(f"  {cor}[{i}]{colors.RESET} {nome:<20} {colors.DIM}{desc}{colors.RESET}")
    print(f"  {cor}[0]{colors.RESET} Novo perfil / pular")
    print(_s)
    raw = prompt_input("Perfil (número ou Enter = novo)", cor)
    if raw.isdigit() and 1 <= int(raw) <= len(nomes):
        return perfis[nomes[int(raw) - 1]]
    return None


def menu_perfis(cor: str):
    while True:
        perfis = listar_perfis()
        _s = _theme_sep()
        print(f"\n{_s}")
        print(f"  {cor}Gerenciar Perfis{colors.RESET}")
        print(_s)
        if not perfis:
            print(f"  {colors.DIM}Nenhum perfil salvo.{colors.RESET}")
        else:
            for i, (nome, p) in enumerate(perfis.items(), 1):
                desc = f"{p.get('formato','?').upper()} · {p.get('qualidade_label','?')} · capa={'sim' if p.get('embutir') else 'não'}"
                print(f"  {cor}[{i}]{colors.RESET} {nome:<20} {colors.DIM}{desc}{colors.RESET}")
        print(_s)
        print(f"  {cor}[n]{colors.RESET} Novo perfil")
        print(f"  {cor}[d]{colors.RESET} Deletar perfil")
        print(f"  {cor}[0]{colors.RESET} Voltar")
        print(_s)
        op = prompt_input("Opção", cor)
        if op == "0":
            break
        elif op == "n":
            nome = prompt_input("Nome do perfil", cor)
            if not nome:
                continue
            formato   = escolher_formato_audio(cor)
            qualidade = escolher_qualidade_audio(cor)
            ql = next((l for _, l, v in QUALIDADE_AUDIO if v == qualidade), qualidade)
            embutir   = perguntar_embutir_capa(cor)
            salvar_perfil(nome, {"formato": formato, "qualidade": qualidade,
                                  "qualidade_label": ql, "embutir": embutir})
            print(f"{colors.SUCCESS}  ✔ Perfil '{nome}' salvo.{colors.RESET}")
        elif op == "d":
            nomes = list(perfis.keys())
            raw = prompt_input("Número do perfil para deletar", cor)
            if raw.isdigit() and 1 <= int(raw) <= len(nomes):
                deletar_perfil(nomes[int(raw) - 1])
                print(f"{colors.SUCCESS}  ✔ Deletado.{colors.RESET}")


def build_cmd_audio(yt_dlp_path, ffmpeg_path, formato, postproc, out_template, url,
                    quality="0", restrict=False, save_path=""):
    cmd = [
        yt_dlp_path,
        "--extract-audio",
        "--audio-format", formato,
        "--audio-quality", quality,
        "--ffmpeg-location", resolver_ffmpeg_location(ffmpeg_path),
    ]
    if restrict:
        cmd.append("--restrict-filenames")
    cmd += postproc + [
        "--concurrent-fragments", "4",
        "--no-part", "--no-cache-dir",
        "--retries", "10",
        "--fragment-retries", "10",
        "--ignore-errors",
        "--no-overwrites",
    ] + _get_cookies_args()
    if save_path:
        cmd += _get_archive_args(save_path)
    cmd += ["-o", out_template, url]
    return cmd


def build_cmd_video(yt_dlp_path, ffmpeg_path, formato, fmt_sel, out, url, restrict=False, save_path=""):
    cmd = [
        yt_dlp_path,
        "-f", fmt_sel,
        "--merge-output-format", formato,
        "--ffmpeg-location", resolver_ffmpeg_location(ffmpeg_path),
        "--add-metadata", "--embed-thumbnail",
        "--concurrent-fragments", "4",
        "--no-part", "--no-cache-dir",
        "--retries", "10", "--no-overwrites",
    ]
    if restrict:
        cmd.append("--restrict-filenames")
    cmd += _get_cookies_args()
    if save_path:
        cmd += _get_archive_args(save_path)
    cmd += ["-o", out, url]
    return cmd


def escolher_qualidade_audio(cor: str) -> str:
    try:
        saved = cfgmod.load_config().get("audio_quality", "0")
    except Exception:
        saved = "0"
    try:
        cfg = cfgmod.load_config()
        s = colors.theme_color(cfg, "HEADER")
        e = colors.theme_color(cfg, "ACCENT")
    except Exception:
        s, e = colors.DEFAULT_THEME["HEADER"], colors.DEFAULT_THEME["ACCENT"]
    _s = sep(s, e)
    print(f"\n{_s}")
    for k, label, val in QUALIDADE_AUDIO:
        marker = f"{colors.SUCCESS}✔{colors.RESET} " if val == saved else "  "
        print(f"  {marker}{cor}[{k}]{colors.RESET} {label}")
    print(_s)
    raw = prompt_input(f"Qualidade  (Enter = manter atual)", cor)
    chosen = next((val for k, _, val in QUALIDADE_AUDIO if k == raw), saved)
    try:
        cfg = cfgmod.load_config()
        cfg["audio_quality"] = chosen
        cfgmod.save_config(cfg)
    except Exception:
        pass
    return chosen


def _theme_sep() -> str:
    try:
        cfg = cfgmod.load_config()
        s = colors.theme_color(cfg, "HEADER")
        e = colors.theme_color(cfg, "ACCENT")
    except Exception:
        s, e = colors.DEFAULT_THEME["HEADER"], colors.DEFAULT_THEME["ACCENT"]
    return sep(s, e)


def escolher_formato_audio(cor: str, default="mp3") -> str:
    _s = _theme_sep()
    print(f"\n{_s}")
    for i, f in enumerate(FORMATOS_AUDIO, 1):
        marker = f"{colors.SUCCESS}✔{colors.RESET} " if f == default else "  "
        print(f"  {marker}{cor}[{i}]{colors.RESET} {f.upper()}")
    print(_s)
    raw = prompt_input(f"Formato  (número ou nome, Enter = {default.upper()})", cor)
    if not raw:
        return default
    if raw.isdigit():
        idx = int(raw) - 1
        if 0 <= idx < len(FORMATOS_AUDIO):
            return FORMATOS_AUDIO[idx]
    if raw in FORMATOS_AUDIO:
        return raw
    print(f"{colors.WARN}  Formato inválido. Usando {default.upper()}.{colors.RESET}")
    return default


def escolher_formato_video(cor: str, default="mp4") -> str:
    _s = _theme_sep()
    print(f"\n{_s}")
    for i, f in enumerate(FORMATOS_VIDEO, 1):
        marker = f"{colors.SUCCESS}✔{colors.RESET} " if f == default else "  "
        print(f"  {marker}{cor}[{i}]{colors.RESET} {f.upper()}")
    print(_s)
    raw = prompt_input(f"Formato de vídeo  (número ou nome, Enter = {default.upper()})", cor)
    if not raw:
        return default
    if raw.isdigit():
        idx = int(raw) - 1
        if 0 <= idx < len(FORMATOS_VIDEO):
            return FORMATOS_VIDEO[idx]
    if raw in FORMATOS_VIDEO:
        return raw
    print(f"{colors.WARN}  Formato inválido. Usando {default.upper()}.{colors.RESET}")
    return default


QUALITY_OPTS = [
    ("1", "Melhor disponível",  "bestvideo+bestaudio/best"),
    ("2", "1080p",              "bestvideo[height<=1080]+bestaudio/best[height<=1080]"),
    ("3", "720p",               "bestvideo[height<=720]+bestaudio/best[height<=720]"),
    ("4", "480p",               "bestvideo[height<=480]+bestaudio/best[height<=480]"),
]


def escolher_qualidade_video(cor: str) -> str:
    _s = _theme_sep()
    print(f"\n{_s}")
    for k, label, _ in QUALITY_OPTS:
        marker = f"{colors.SUCCESS}✔{colors.RESET} " if k == "1" else "  "
        print(f"  {marker}{cor}[{k}]{colors.RESET} {label}")
    print(_s)
    q = prompt_input("Qualidade  (Enter = melhor)", cor)
    return next((v for k, _, v in QUALITY_OPTS if k == q), "bestvideo+bestaudio/best")


def perguntar_embutir_capa(cor: str, default=True) -> bool:
    from core.i18n import t
    pad = t('yes_key_dl') if default else "n"
    resp = input(f"{cor}  {t('embed_cover').format(default=pad)}: {colors.RESET}").strip().lower()
    return resp.startswith(t('yes_key_dl')) if resp else default


def playlist_warning(yt_dlp_path, url, entries, cor: str, label="playlist") -> bool:
    try:
        thresh = cfgmod.load_config().get("playlist_warning_threshold", 50)
    except Exception:
        thresh = 50

    print(f"\n{colors.INFO}  ◈ {label.capitalize()} detectada: {len(entries)} itens{colors.RESET}")

    if len(entries) > 1 and not confirmar(f"  Baixar todos os {len(entries)} itens?", cor):
        print(f"{colors.WARN}  Operação cancelada.{colors.RESET}")
        return False

    if len(entries) > thresh:
        stats = get_playlist_stats(yt_dlp_path, url)
        dur   = _format_duration(stats.get("total_duration"))
        size  = _format_bytes(stats.get("total_size"))
        extras = []
        if dur:  extras.append(f"duração ~{dur}")
        if size: extras.append(f"tamanho ~{size}")
        extra_txt = "  (" + " · ".join(extras) + ")" if extras else ""
        print(f"{colors.WARN}  ⚠  {label.capitalize()} grande ({len(entries)} itens){extra_txt}{colors.RESET}")
        if not confirmar("  Isso pode demorar bastante. Continuar mesmo assim?", cor):
            print(f"{colors.WARN}  Operação cancelada.{colors.RESET}")
            return False

    return True


def _resolver_pasta_de_info(info: dict, save_path: str, cor: str, label: str) -> str:
    template = "%(playlist_index)s - %(title)s.%(ext)s"
    title = (info or {}).get("title")
    if title:
        safe = sanitize_folder(title)
        if confirmar(f"  Salvar em subpasta '{safe}'?", cor):
            try:
                pasta = safe_join(save_path, safe)
                Path(pasta).mkdir(parents=True, exist_ok=True)
                print(f"{colors.SUCCESS}  ✔ Pasta criada: {pasta}{colors.RESET}")
                return os.path.join(pasta, template)
            except ValueError:
                print(f"{colors.WARN}  Caminho inválido. Usando pasta padrão.{colors.RESET}")
    return os.path.join(save_path, template)


def resolver_pasta_playlist(yt_dlp_path, url, save_path, cor: str, label="playlist"):
    title    = get_playlist_title(yt_dlp_path, url)
    template = "%(playlist_index)s - %(title)s.%(ext)s"

    if title:
        safe = sanitize_folder(title)
        if confirmar(f"  Salvar em subpasta '{safe}'?", cor):
            try:
                pasta = safe_join(save_path, safe)
                Path(pasta).mkdir(parents=True, exist_ok=True)
                print(f"{colors.SUCCESS}  ✔ Pasta criada: {pasta}{colors.RESET}")
                return os.path.join(pasta, template)
            except ValueError:
                print(f"{colors.WARN}  Caminho inválido. Usando pasta padrão.{colors.RESET}")

    return os.path.join(save_path, template)


def _cfg_download():
    try:
        cfg = cfgmod.load_config()
        return cfg.get("audio_quality", "0"), cfg.get("restrict_filenames", False)
    except Exception:
        return "0", False


def _tempo_para_sec(t: str) -> float:
    partes = t.strip().split(":")
    try:
        if len(partes) == 3:
            return int(partes[0]) * 3600 + int(partes[1]) * 60 + float(partes[2])
        return int(partes[0]) * 60 + float(partes[1])
    except Exception:
        return 0.0


def _mostrar_preview(yt_dlp_path: str, url: str, cor: str):
    info = with_spinner("Buscando informações...", lambda: fetch_url_preview(yt_dlp_path, url), cor)
    if not info:
        return
    _s = _theme_sep()
    print(_s)
    print(f"  {colors.BOLD}{info['title']}{colors.RESET}")
    print(f"  {colors.DIM}{info['uploader']}  ·  {info['duration']}", end="")
    if info.get("views"):
        print(f"  ·  {info['views']:,} views", end="")
    print(colors.RESET)
    print(_s)


def _ler_urls_batch(cor: str) -> list[str]:
    _s = _theme_sep()
    print(f"\n{_s}")
    print(f"  {cor}URLs (cole várias separadas por espaço, ou caminho de .txt):{colors.RESET}")
    print(f"  {colors.DIM}Linha em branco = fim da entrada{colors.RESET}")
    print(_s)
    linhas = []
    while True:
        linha = input(f"  {cor}❯ {colors.RESET}").strip()
        if not linha:
            break
        linhas.append(linha)
    raw = " ".join(linhas).strip()
    if not raw:
        return []
    p = Path(raw.strip()).expanduser()
    if p.suffix == ".txt" and p.is_file():
        urls = [l.strip() for l in p.read_text(encoding="utf-8").splitlines()
                if l.strip() and not l.strip().startswith("#")]
        print(f"{colors.SUCCESS}  ✔ {len(urls)} URLs carregadas de {p.name}{colors.RESET}")
        return urls
    return [u for u in re.split(r"[\s,]+", raw) if u.startswith("http")]


def baixar_musica(save_path, yt_dlp_path, ffmpeg_path, cor: str, validar_url=None):
    perfil = escolher_perfil(cor)
    if perfil:
        formato   = perfil["formato"]
        qualidade = perfil["qualidade"]
        embutir   = perfil["embutir"]
    else:
        formato   = escolher_formato_audio(cor)
        qualidade = escolher_qualidade_audio(cor)
        embutir   = perguntar_embutir_capa(cor)
        nome_perfil = prompt_input("Salvar como perfil? (nome ou Enter = não)", cor)
        if nome_perfil:
            ql = next((l for _, l, v in QUALIDADE_AUDIO if v == qualidade), qualidade)
            salvar_perfil(nome_perfil, {"formato": formato, "qualidade": qualidade,
                                        "qualidade_label": ql, "embutir": embutir})
            print(f"{colors.SUCCESS}  ✔ Perfil '{nome_perfil}' salvo.{colors.RESET}")

    postproc = build_postproc(embutir)
    _, restrict = _cfg_download()

    urls = _ler_urls_batch(cor)
    if not urls:
        print(f"{colors.ERROR}  Nenhum link informado.{colors.RESET}"); pausar(cor); return

    total_ok = 0
    total_urls = [u for u in urls if _validar_url(u) and (not validar_url or validar_url(u))]
    for i, url in enumerate(total_urls, 1):
        if len(total_urls) > 1:
            print(f"\n{cor}  [{i}/{len(total_urls)}]{colors.RESET}")
        _mostrar_preview(yt_dlp_path, url, cor)
        if len(total_urls) > 1 and not confirmar(f"  Baixar este item?", cor):
            continue
        try:
            out = safe_join(save_path, "%(title)s.%(ext)s")
        except ValueError:
            print(f"{colors.ERROR}  Caminho inválido.{colors.RESET}"); continue
        cmd = build_cmd_audio(yt_dlp_path, ffmpeg_path, formato, postproc, out, url,
                              quality=qualidade, restrict=restrict, save_path=save_path)
        print(f"\n{cor}  ⬇  Baixando música...{colors.RESET}")
        success, title = executar_comando(cmd, "Falha ao baixar música.", None)
        if success:
            total_ok += 1
            record_download(url, title, save_path, "musica")
            print(f"{colors.SUCCESS}  ✔ Salvo em: {save_path}{colors.RESET}")

    if total_ok:
        notify("ICYRIP — Download concluído",
               f"{total_ok} música{'s' if total_ok > 1 else ''} salva{'s' if total_ok > 1 else ''} em {save_path}")
    pausar(cor)


def baixar_playlist(save_path, yt_dlp_path, ffmpeg_path, cor: str,
                    label="playlist", validar_url=None):
    url = prompt_input(f"URL da {label}", cor)
    if not url:
        print(f"{colors.ERROR}  Nenhum link informado.{colors.RESET}"); pausar(cor); return
    if not _validar_url(url):
        pausar(cor); return
    if validar_url and not validar_url(url):
        pausar(cor); return

    perfil = escolher_perfil(cor)
    if perfil:
        formato   = perfil["formato"]
        qualidade = perfil["qualidade"]
        embutir   = perfil["embutir"]
    else:
        formato   = escolher_formato_audio(cor)
        qualidade = escolher_qualidade_audio(cor)
        embutir   = perguntar_embutir_capa(cor)

    postproc = build_postproc(embutir)
    _, restrict = _cfg_download()

    info = with_spinner(
        f"Buscando informações da {label}...",
        lambda: get_playlist_info(yt_dlp_path, url), cor
    )
    entries = info.get("entries", []) if info else []
    if entries and not playlist_warning(yt_dlp_path, url, entries, cor, label):
        pausar(cor); return

    out_template = _resolver_pasta_de_info(info, save_path, cor, label)
    cmd = build_cmd_audio(yt_dlp_path, ffmpeg_path, formato, postproc, out_template, url,
                          quality=qualidade, restrict=restrict, save_path=save_path)
    print(f"\n{cor}  ⬇  Baixando {label}...{colors.RESET}")
    success, _ = executar_comando(cmd, f"Falha ao baixar {label}.", entries)
    if success:
        record_download(url, info.get("title"), save_path, label)
        print(f"{colors.SUCCESS}  ✔ {label.capitalize()} salva em: {save_path}{colors.RESET}")
        notify(f"ICYRIP — {label.capitalize()} concluída", f"{info.get('title', '')} → {save_path}")
    pausar(cor)


def baixar_album(save_path, yt_dlp_path, ffmpeg_path, cor: str):
    url = prompt_input("URL do álbum / playlist", cor)
    if not url:
        print(f"{colors.ERROR}  Nenhum link informado.{colors.RESET}"); pausar(cor); return
    if not _validar_url(url):
        pausar(cor); return

    perfil = escolher_perfil(cor)
    if perfil:
        formato   = perfil["formato"]
        qualidade = perfil["qualidade"]
        embutir   = perfil["embutir"]
    else:
        formato   = escolher_formato_audio(cor)
        qualidade = escolher_qualidade_audio(cor)
        embutir   = perguntar_embutir_capa(cor)

    postproc = build_postproc(embutir)
    _, restrict = _cfg_download()

    info = with_spinner(
        "Buscando informações do álbum...",
        lambda: get_playlist_info(yt_dlp_path, url), cor
    )
    entries = info.get("entries", []) if info else []
    if entries and not playlist_warning(yt_dlp_path, url, entries, cor, "álbum"):
        pausar(cor); return

    title = info.get("title") if info else None
    if title:
        safe = sanitize_folder(title)
        try:
            pasta = safe_join(save_path, safe)
            Path(pasta).mkdir(parents=True, exist_ok=True)
            out_template = os.path.join(pasta, "%(playlist_index)s - %(title)s.%(ext)s")
        except ValueError:
            out_template = os.path.join(save_path, "%(playlist_index)s - %(title)s.%(ext)s")
    else:
        out_template = os.path.join(save_path, "%(playlist_index)s - %(title)s.%(ext)s")

    cmd = build_cmd_audio(yt_dlp_path, ffmpeg_path, formato, postproc, out_template, url,
                          quality=qualidade, restrict=restrict, save_path=save_path)
    print(f"\n{cor}  ⬇  Baixando álbum...{colors.RESET}")
    success, _ = executar_comando(cmd, "Falha ao baixar álbum.", entries)
    if success:
        record_download(url, title, save_path, "álbum")
        print(f"{colors.SUCCESS}  ✔ Álbum salvo em: {save_path}{colors.RESET}")
        notify("ICYRIP — Álbum concluído", f"{title or ''} → {save_path}")
    pausar(cor)


def baixar_video(save_path, yt_dlp_path, ffmpeg_path, cor: str):
    urls = _ler_urls_batch(cor)
    if not urls:
        print(f"{colors.ERROR}  Nenhum link informado.{colors.RESET}"); pausar(cor); return

    formato = escolher_formato_video(cor)
    fmt_sel = escolher_qualidade_video(cor)
    _, restrict = _cfg_download()

    total_ok = 0
    total_urls = [u for u in urls if _validar_url(u)]
    for i, url in enumerate(total_urls, 1):
        if len(total_urls) > 1:
            print(f"\n{cor}  [{i}/{len(total_urls)}]{colors.RESET}")
        _mostrar_preview(yt_dlp_path, url, cor)
        if len(total_urls) > 1 and not confirmar("  Baixar este item?", cor):
            continue
        try:
            out = safe_join(save_path, "%(title)s.%(ext)s")
        except ValueError:
            print(f"{colors.ERROR}  Caminho inválido.{colors.RESET}"); continue
        cmd = build_cmd_video(yt_dlp_path, ffmpeg_path, formato, fmt_sel, out, url,
                              restrict=restrict, save_path=save_path)
        print(f"\n{cor}  ⬇  Baixando vídeo...{colors.RESET}")
        success, title = executar_comando(cmd, "Falha ao baixar vídeo.", None)
        if success:
            total_ok += 1
            record_download(url, title, save_path, "video")
            print(f"{colors.SUCCESS}  ✔ Vídeo salvo em: {save_path}{colors.RESET}")

    if total_ok:
        notify("ICYRIP — Vídeo concluído",
               f"{total_ok} vídeo{'s' if total_ok > 1 else ''} salvo{'s' if total_ok > 1 else ''} em {save_path}")
    pausar(cor)


def baixar_clipe(save_path, yt_dlp_path, ffmpeg_path, cor: str,
                 permitir_video=True, validar_url=None):
    url = prompt_input("URL do vídeo/faixa", cor)
    if not url:
        print(f"{colors.ERROR}  Nenhum link informado.{colors.RESET}"); pausar(cor); return
    if not _validar_url(url):
        pausar(cor); return
    if validar_url and not validar_url(url):
        pausar(cor); return

    inicio = prompt_input("Tempo de início  (ex: 00:01:30)", cor)
    fim    = prompt_input("Tempo de fim     (ex: 00:03:00)", cor)
    if not inicio or not fim:
        print(f"{colors.ERROR}  Tempos inválidos.{colors.RESET}"); pausar(cor); return
    if not _validar_tempo(inicio) or not _validar_tempo(fim):
        print(f"{colors.ERROR}  Formato inválido. Use HH:MM:SS ou MM:SS (ex: 00:01:30).{colors.RESET}")
        pausar(cor); return
    if _tempo_para_sec(inicio) >= _tempo_para_sec(fim):
        print(f"{colors.ERROR}  Tempo de início deve ser menor que o tempo de fim.{colors.RESET}")
        pausar(cor); return

    try:
        out = safe_join(save_path, "%(title)s_clipe.%(ext)s")
    except ValueError:
        print(f"{colors.ERROR}  Caminho inválido.{colors.RESET}"); pausar(cor); return

    tipo = "1"
    if permitir_video:
        s = sep(colors.DEFAULT_THEME["HEADER"], colors.DEFAULT_THEME["ACCENT"])
        print(f"\n{s}")
        print(f"  {cor}[1]{colors.RESET} Áudio")
        print(f"  {cor}[2]{colors.RESET} Vídeo")
        print(s)
        tipo = prompt_input("Tipo  (Enter = áudio)", cor) or "1"

    if tipo == "2" and permitir_video:
        formato = escolher_formato_video(cor)
        _, restrict = _cfg_download()
        cmd = [
            yt_dlp_path,
            "--download-sections", f"*{inicio}-{fim}",
            "--force-keyframes-at-cuts",
            "-f", "bestvideo+bestaudio/best",
            "--merge-output-format", formato,
            "--ffmpeg-location", resolver_ffmpeg_location(ffmpeg_path),
            "--no-part", "--no-cache-dir", "--retries", "10",
        ] + (["--restrict-filenames"] if restrict else []) + _get_cookies_args() + [
            "-o", out, url,
        ]
    else:
        formato = escolher_formato_audio(cor)
        _, restrict = _cfg_download()
        cookies = _get_cookies_args()
        cmd = [
            yt_dlp_path,
            "--download-sections", f"*{inicio}-{fim}",
            "--force-keyframes-at-cuts",
            "--extract-audio", "--audio-format", formato, "--audio-quality", "0",
            "--ffmpeg-location", resolver_ffmpeg_location(ffmpeg_path),
            "--add-metadata", "--no-part", "--no-cache-dir", "--retries", "10",
        ] + ([ "--restrict-filenames"] if restrict else []) + cookies + ["-o", out, url]

    print(f"\n{cor}  ✂  Baixando clipe {inicio} → {fim}...{colors.RESET}")
    success, _ = executar_comando(cmd, "Falha ao baixar clipe.", None)
    if success:
        print(f"{colors.SUCCESS}  ✔ Clipe salvo em: {save_path}{colors.RESET}")
    pausar(cor)


def converter_para_audio(save_path, ffmpeg_path, cor: str):
    arquivo = prompt_input("Caminho ou nome do arquivo  (com extensão)", cor)
    if not arquivo or "." not in arquivo:
        print(f"{colors.ERROR}  Arquivo inválido.{colors.RESET}"); pausar(cor); return

    p = Path(arquivo).expanduser()
    if p.is_absolute():
        entrada = str(p)
    else:
        try:
            entrada = safe_join(save_path, arquivo)
        except ValueError:
            print(f"{colors.ERROR}  Caminho inválido.{colors.RESET}"); pausar(cor); return

    if not os.path.isfile(entrada):
        print(f"{colors.ERROR}  Arquivo não encontrado: {entrada}{colors.RESET}"); pausar(cor); return

    formato = escolher_formato_audio(cor)
    nome    = Path(entrada).stem
    saida   = os.path.join(os.path.dirname(entrada), f"{nome}.{formato}")
    label   = f"Convertendo  {colors.DIM}{nome}{colors.RESET}  →  {colors.BOLD}{formato.upper()}{colors.RESET}"

    ffmpeg_bin = resolver_ffmpeg_location(ffmpeg_path)
    import shutil as _sh
    resolved = _sh.which("ffmpeg", path=ffmpeg_bin) or ffmpeg_path
    cmd = [resolved, "-y", "-i", entrada, saida]
    success = executar_ffmpeg_conversao(cmd, f"Falha ao converter para {formato}.", label)
    if success:
        print(f"{colors.SUCCESS}  ✔ Convertido: {saida}{colors.RESET}")
    pausar(cor)


def _enfileirar_url(cor: str, modulo: str, save_path: str):
    urls = _ler_urls_batch(cor)
    if not urls:
        print(f"{colors.ERROR}  Nenhuma URL informada.{colors.RESET}")
        return

    perfil = escolher_perfil(cor)
    if perfil:
        formato   = perfil["formato"]
        qualidade = perfil["qualidade"]
        embutir   = perfil["embutir"]
    else:
        formato   = escolher_formato_audio(cor)
        qualidade = escolher_qualidade_audio(cor)
        embutir   = perguntar_embutir_capa(cor)

    for url in urls:
        if not _validar_url(url):
            continue
        enqueue({
            "url":       url,
            "modulo":    modulo,
            "save_path": save_path,
            "formato":   formato,
            "qualidade": qualidade,
            "embutir":   embutir,
            "titulo":    "",
        })
    q = load_queue()
    print(f"{colors.SUCCESS}  ✔ {len(urls)} item(s) adicionado(s). Fila: {len(q)} total.{colors.RESET}")


def processar_fila(yt_dlp_path: str, ffmpeg_path: str, cor: str):
    q = load_queue()
    if not q:
        print(f"{colors.WARN}  Fila vazia.{colors.RESET}")
        pausar(cor)
        return

    total_fila = len(q)
    print(f"\n{cor}  ▶ Processando fila — {total_fila} item(s){colors.RESET}")
    ok_total = err_total = 0
    idx_fila = 0

    while True:
        item = dequeue()
        if not item:
            break

        idx_fila += 1
        url       = item.get("url", "")
        modulo    = item.get("modulo", "musica")
        save_path = item.get("save_path", "")
        formato   = item.get("formato", "mp3")
        qualidade = item.get("qualidade", "0")
        embutir   = item.get("embutir", True)
        titulo    = item.get("titulo", "")

        label_item = titulo if titulo else url[:60]
        print(f"\n{cor}  [{idx_fila}/{total_fila}]  {label_item}{colors.RESET}")

        postproc = build_postproc(embutir)
        _, restrict = _cfg_download()

        try:
            out = safe_join(save_path, "%(title)s.%(ext)s")
        except ValueError:
            print(f"{colors.ERROR}  Caminho inválido, pulando.{colors.RESET}")
            err_total += 1
            continue

        if modulo == "video":
            cmd = build_cmd_video(yt_dlp_path, ffmpeg_path, formato,
                                  "bestvideo+bestaudio/best", out, url,
                                  restrict=restrict, save_path=save_path)
        else:
            cmd = build_cmd_audio(yt_dlp_path, ffmpeg_path, formato, postproc,
                                  out, url, quality=qualidade,
                                  restrict=restrict, save_path=save_path)

        success, title = executar_comando(cmd, "Falha.", None)
        if success:
            ok_total += 1
            record_download(url, title, save_path, modulo)
            print(f"{colors.SUCCESS}  ✔ Salvo em: {save_path}{colors.RESET}")
        else:
            err_total += 1

    msg = f"{ok_total} concluído(s)"
    if err_total:
        msg += f", {err_total} erro(s)"
    notify("ICYRIP — Fila concluída", msg)
    print(f"\n{colors.SUCCESS}  ✔ Fila finalizada — {msg}{colors.RESET}")
    pausar(cor)


def menu_fila(yt_dlp_path: str, ffmpeg_path: str, cor: str, save_path: str, modulo: str):
    while True:
        q = load_queue()
        _s = _theme_sep()
        print(f"\n{_s}")
        print(f"  {cor}Fila de Downloads  {colors.DIM}({len(q)} item(s)){colors.RESET}")
        print(_s)

        if not q:
            print(f"  {colors.DIM}Fila vazia.{colors.RESET}")
        else:
            for i, item in enumerate(q, 1):
                url_short = item.get("url", "")[:55]
                fmt  = item.get("formato", "?").upper()
                mod  = item.get("modulo", "?")
                print(f"  {cor}[{i:2}]{colors.RESET}  {colors.DIM}{mod:<10}{colors.RESET}  "
                      f"{colors.BOLD}{url_short}{colors.RESET}  {colors.DIM}{fmt}{colors.RESET}")

        print(_s)
        print(f"  {cor}[+]{colors.RESET}  Adicionar URLs à fila")
        print(f"  {cor}[r]{colors.RESET}  Executar fila agora")
        print(f"  {cor}[d]{colors.RESET}  Remover item")
        print(f"  {cor}[x]{colors.RESET}  Limpar fila toda")
        print(f"  {cor}[0]{colors.RESET}  Voltar")
        print(_s)

        op = prompt_input("Opção", cor)

        if op == "0":
            break
        elif op == "+":
            _enfileirar_url(cor, modulo, save_path)
        elif op == "r":
            processar_fila(yt_dlp_path, ffmpeg_path, cor)
        elif op == "d":
            if not q:
                continue
            raw = prompt_input("Número do item", cor)
            if raw.isdigit() and 1 <= int(raw) <= len(q):
                remove_from_queue(int(raw) - 1)
                print(f"{colors.SUCCESS}  ✔ Removido.{colors.RESET}")
        elif op == "x":
            clear_queue()
            print(f"{colors.SUCCESS}  ✔ Fila limpa.{colors.RESET}")

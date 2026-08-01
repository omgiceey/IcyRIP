import sys
import time

import core.colors as colors
from core import utils
from core.colors import apply_theme_to_module
from core.utils import (
    configurar_dependencias,
    animate_banner_in,
    animate_exit,
    compact_width, compact_header, compact_line, compact_row,
)
from core.downloader import (
    limpar_tela, sep, pausar,
    configurar_pasta, get_pasta_salva,
    baixar_musica, baixar_playlist,
    baixar_clipe, converter_para_audio,
)

MODULO = "sound"

BANNER = r"""
 ██▓ ▄████▄▓██   ██▓  ██████  ▒█████   █    ██  ███▄    █ ▓█████▄
▓██▒▒██▀ ▀█ ▒██  ██▒▒██    ▒ ▒██▒  ██▒ ██  ▓██▒ ██ ▀█   █ ▒██▀ ██▌
▒██▒▒▓█    ▄ ▒██ ██░░ ▓██▄   ▒██░  ██▒▓██  ▒██░▓██  ▀█ ██▒░██   █▌
░██░▒▓▓▄ ▄██▒░ ▐██▓░  ▒   ██▒▒██   ██░▓▓█  ░██░▓██▒  ▐▌██▒░▓█▄   ▌
░██░▒ ▓███▀ ░░ ██▒▓░▒██████▒▒░ ████▓▒░▒▒█████▓ ▒██░   ▓██░░▒████▓
░▓  ░ ░▒ ▒  ░ ██▒▒▒ ▒ ▒▓▒ ▒ ░░ ▒░▒░▒░ ░▒▓▒ ▒ ▒ ░ ▒░   ▒ ▒  ▒▒▓  ▒
 ▒ ░  ░  ▒  ▓██ ░▒░ ░ ░▒  ░ ░  ░ ▒ ▒░ ░░▒░ ░ ░ ░ ░░   ░ ▒░ ░ ▒  ▒
 ▒ ░░       ▒ ▒ ░░  ░  ░  ░  ░ ░ ░ ▒   ░░░ ░ ░    ░   ░ ░  ░ ░  ░
 ░  ░ ░     ░ ░           ░      ░ ░     ░              ░    ░
    ░       ░ ░                                            ░
"""

RST = colors.RESET

def _O(): return colors.ORANGE


def _validar_url_sc(url: str) -> bool:
    if "soundcloud.com" not in url.lower():
        print(f"{colors.WARN}  ⚠  URL inválida: este módulo aceita apenas links do SoundCloud.{RST}")
        return False
    return True


def _resolve_banner_colors():
    try:
        import core.config as _cfg
        cfg   = _cfg.load_config()
        start = colors.theme_color(cfg, "ORANGE")
        end   = colors.theme_color(cfg, "ACCENT")
        raw   = cfg.get("ascii_style", "follow_theme")
        style = raw.get("sound", "follow_theme") if isinstance(raw, dict) else raw
        if style == "neon":    return "#00ff99", "#8a2be2"
        if style == "default": return colors.DEFAULT_THEME["HEADER"], colors.DEFAULT_THEME["ACCENT"]
        if style == "custom":
            ac = (cfg.get("ascii_colors") or {}).get("sound", {})
            return ac.get("start", start), ac.get("end", end)
        return start, end
    except Exception:
        return colors.DEFAULT_THEME["HEADER"], colors.DEFAULT_THEME["ACCENT"]


def mostrar_header(animated: bool = False):
    limpar_tela()
    s_hex, e_hex = _resolve_banner_colors()
    try:
        centered = utils.center_text(BANNER)
        if animated:
            animate_banner_in(centered, s_hex, e_hex, delay=0.012)
        else:
            print(colors.gradient_text(centered, s_hex, e_hex))
    except Exception:
        print(f"{_O()}ICYRIP SoundCloud{RST}")

    _sep = sep(s_hex, e_hex)
    print(_sep)
    print(f"{_O()}  ✦ ICYSOUND SoundCloud v2.1  ·  By Icey  ·  Powered by yt-dlp  ✦{RST}")
    print(_sep)


def exibir_opcoes(save_path: str):
    tw = compact_width()
    print()
    compact_header("✦  SOUNDCLOUD  ·  ICYSOUND  ✦", f"destino: {save_path}", _O(), tw)
    print(compact_row("1", "🎵  Baixar Música",            "faixa individual",              _O(),          tw))
    print(compact_row("2", "📝  Baixar Playlist / Álbum",   "todas as faixas",               _O(),          tw))
    print(compact_row("3", "✂️  Baixar Clipe",              "trecho por tempo",              _O(),          tw))
    print(compact_row("4", "🔄  Converter para áudio",      "converte arquivo local",        _O(),          tw))
    print(compact_line(tw))
    print(compact_row("5", "📁  Alterar pasta",             "muda destino dos downloads",    _O(),          tw))
    print(compact_row("f", "📌  Fila",                       "gerenciar fila de downloads",   _O(),          tw))
    print(compact_row("6", "←   Voltar ao HUB",             "menu principal",                colors.DIM, tw))
    print(compact_row("0", "✕   Sair",                       "encerrar",                      colors.DIM, tw))
    print(compact_line(tw))


def menu(yt_dlp_path, ffmpeg_path):
    save_path = get_pasta_salva(MODULO, "SoundCloud")

    acoes = {
        "1": lambda sp: baixar_musica(sp, yt_dlp_path, ffmpeg_path, _O(), _validar_url_sc),
        "2": lambda sp: baixar_playlist(sp, yt_dlp_path, ffmpeg_path, _O(),
                                        "playlist / álbum", _validar_url_sc),
        "3": lambda sp: baixar_clipe(sp, yt_dlp_path, ffmpeg_path, _O(),
                                     permitir_video=False, validar_url=_validar_url_sc),
        "4": lambda sp: converter_para_audio(sp, ffmpeg_path, _O()),
    }

    try:
        while True:
            from core import config as _cfgmod
            _cfg = _cfgmod.load_config()
            apply_theme_to_module(_cfg)
            mostrar_header(animated=True)
            exibir_opcoes(save_path)
            opcao = input(f"\n{_O()}  ❯ {RST}").strip()

            if opcao in acoes:
                acoes[opcao](save_path)
            elif opcao == "5":
                save_path = configurar_pasta(MODULO, _O(), "SoundCloud")
            elif opcao == "f":
                from core.downloader import menu_fila
                menu_fila(yt_dlp_path, ffmpeg_path, _O(), save_path, "musica")
            elif opcao == "6":
                animate_exit("Voltando ao HUB", _O())
                break
            elif opcao == "0":
                animate_exit("Até logo", _O())
                sys.exit(0)
            else:
                print(f"{colors.WARN}  Opção inválida.{RST}")
                time.sleep(0.7)
    except KeyboardInterrupt:
        print(f"\n{colors.INFO}  Encerrando...{RST}\n")


if __name__ == "__main__":
    mostrar_header(animated=True)
    yt_dlp_path, ffmpeg_path = configurar_dependencias()
    if yt_dlp_path and ffmpeg_path:
        menu(yt_dlp_path, ffmpeg_path)

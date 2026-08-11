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
    baixar_musica, baixar_playlist, baixar_album,
    baixar_video, baixar_clipe, converter_para_audio,
    abrir_pasta,
)

MODULO = "ytb"

BANNER = r"""
░██████  ░██████  ░██     ░██ ░██████████░████████
  ░██   ░██   ░██  ░██   ░██      ░██    ░██    ░██
  ░██  ░██          ░██ ░██       ░██    ░██    ░██
  ░██  ░██           ░████        ░██    ░████████
  ░██  ░██            ░██         ░██    ░██     ░██
  ░██   ░██   ░██     ░██         ░██    ░██     ░██
░██████  ░██████      ░██         ░██    ░█████████
"""

RST = colors.RESET

def _C(): return colors.RED


def _resolve_banner_colors():
    try:
        import core.config as _cfg
        cfg   = _cfg.load_config()
        if cfg.get("color_mode", "follow_preset") == "follow_app":
            from core.colors import APP_COLORS
            ac = APP_COLORS.get("ytb", {})
            return ac["_banner_start"], ac["_banner_end"]
        start = colors.theme_color(cfg, "RED")
        end   = colors.theme_color(cfg, "ACCENT")
        raw   = cfg.get("ascii_style", "follow_theme")
        style = raw.get("ytb", "follow_theme") if isinstance(raw, dict) else raw
        if style == "neon":    return "#00ff99", "#8a2be2"
        if style == "default": return colors.DEFAULT_THEME["HEADER"], colors.DEFAULT_THEME["ACCENT"]
        if style == "custom":
            ac = (cfg.get("ascii_colors") or {}).get("ytb", {})
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
        print(f"{_C()}ICYRIP YouTube{RST}")

    _sep = sep(s_hex, e_hex)
    print(_sep)
    print(f"{_C()}  ✦ ICYRIP YouTube (ICYTB) v2.3  ·  By Icey  ·  Powered by yt-dlp  ✦{RST}")
    print(_sep)


def exibir_opcoes(save_path: str):
    tw = compact_width()
    print()
    compact_header("✦  YOUTUBE  ·  ICYTB  ✦", f"destino: {save_path}", _C(), tw)
    print(compact_row("1", "🎵  Baixar Música",       "audio de uma URL",              _C(),          tw))
    print(compact_row("2", "📝  Baixar Playlist",       "todas as faixas",               _C(),          tw))
    print(compact_row("3", "💿  Baixar Álbum",          "playlist em subpasta",          _C(),          tw))
    print(compact_row("4", "🎥  Baixar Vídeo",          "mp4 / mkv / webm + qualidade",  _C(),          tw))
    print(compact_row("5", "✂️  Baixar Clipe",          "trecho por tempo",              _C(),          tw))
    print(compact_row("6", "🔄  Converter para áudio",  "converte arquivo local",        _C(),          tw))
    print(compact_line(tw))
    print(compact_row("7", "📁  Alterar pasta",         "muda destino dos downloads",    _C(),          tw))
    print(compact_row("p", "📂  Abrir pasta",           "abre o explorador de arquivos",  _C(),          tw))
    print(compact_row("f", "📌  Fila",                   "gerenciar fila de downloads",   _C(),          tw))
    print(compact_row("8", "←   Voltar ao HUB",         "menu principal",                colors.DIM, tw))
    print(compact_row("0", "✕   Sair",                   "encerrar",                      colors.DIM, tw))
    print(compact_line(tw))


def menu(yt_dlp_path, ffmpeg_path):
    save_path = get_pasta_salva(MODULO, "Músicas")

    acoes = {
        "1": lambda sp: baixar_musica(sp, yt_dlp_path, ffmpeg_path, _C()),
        "2": lambda sp: baixar_playlist(sp, yt_dlp_path, ffmpeg_path, _C(), "playlist"),
        "3": lambda sp: baixar_album(sp, yt_dlp_path, ffmpeg_path, _C()),
        "4": lambda sp: baixar_video(sp, yt_dlp_path, ffmpeg_path, _C()),
        "5": lambda sp: baixar_clipe(sp, yt_dlp_path, ffmpeg_path, _C(), permitir_video=True),
        "6": lambda sp: converter_para_audio(sp, ffmpeg_path, _C()),
    }

    try:
        while True:
            from core import config as _cfgmod
            _cfg = _cfgmod.load_config()
            apply_theme_to_module(_cfg, MODULO)
            mostrar_header(animated=True)
            exibir_opcoes(save_path)
            opcao = input(f"\n{_C()}  ❯ {RST}").strip()

            if opcao in acoes:
                acoes[opcao](save_path)
            elif opcao == "7":
                save_path = configurar_pasta(MODULO, _C(), "Músicas")
            elif opcao == "p":
                abrir_pasta(save_path, _C())
            elif opcao == "f":
                from core.downloader import menu_fila
                menu_fila(yt_dlp_path, ffmpeg_path, _C(), save_path, "musica")
            elif opcao == "8":
                animate_exit("Voltando ao HUB", _C())
                break
            elif opcao == "0":
                animate_exit("Até logo", _C())
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

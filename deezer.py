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
    baixar_clipe, converter_para_audio,
    abrir_pasta,
)

MODULO = "deezer"

_PINK     = "#a238ff"
_PINK_END = "#ff6ec7"

BANNER = r"""
░▒▓███████▓▒░░▒▓████████▓▒░▒▓████████▓▒░▒▓████████▓▒░▒▓████████▓▒░▒▓███████▓▒░  
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░             ░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░           ░▒▓██▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓██████▓▒░ ░▒▓██████▓▒░    ░▒▓██▓▒░  ░▒▓██████▓▒░ ░▒▓███████▓▒░  
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░       ░▒▓██▓▒░    ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓███████▓▒░░▒▓████████▓▒░▒▓████████▓▒░▒▓████████▓▒░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░                                                   
"""

RST = colors.RESET


def _D():
    return colors.to_ansi(_PINK)


def _validar_url_dz(url: str) -> bool:
    if "deezer.com" not in url.lower():
        print(f"{colors.WARN}  ⚠  URL inválida: este módulo aceita apenas links do Deezer.{RST}")
        return False
    return True


def _resolve_banner_colors():
    try:
        import core.config as _cfg
        cfg = _cfg.load_config()
        if cfg.get("color_mode", "follow_preset") == "follow_app":
            from core.colors import APP_COLORS
            ac = APP_COLORS.get("deezer", {})
            return ac["_banner_start"], ac["_banner_end"]
        raw = cfg.get("ascii_style", "follow_theme")
        style = raw.get("deezer", "follow_theme") if isinstance(raw, dict) else raw
        if style == "neon":    return "#00ff99", "#8a2be2"
        if style == "default": return colors.DEFAULT_THEME["HEADER"], colors.DEFAULT_THEME["ACCENT"]
        if style == "custom":
            ac = (cfg.get("ascii_colors") or {}).get("deezer", {})
            return ac.get("start", _PINK), ac.get("end", _PINK_END)
        return _PINK, _PINK_END
    except Exception:
        return _PINK, _PINK_END


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
        print(f"{_D()}ICYRIP Deezer{RST}")

    _sep = sep(s_hex, e_hex)
    print(_sep)
    print(f"{_D()}  ✦ ICYRIP Deezer v2.3  ·  By Icey  ·  Powered by yt-dlp  ✦{RST}")
    print(_sep)


def exibir_opcoes(save_path: str):
    tw = compact_width()
    print()
    compact_header("✦  DEEZER  ·  ICYDZ  ✦", f"destino: {save_path}", _D(), tw)
    print(compact_row("1", "🎵  Baixar Música",           "faixa individual",              _D(),          tw))
    print(compact_row("2", "📝  Baixar Playlist",          "todas as faixas",               _D(),          tw))
    print(compact_row("3", "💿  Baixar Álbum",             "álbum em subpasta",             _D(),          tw))
    print(compact_row("4", "✂️  Baixar Clipe",             "trecho por tempo",              _D(),          tw))
    print(compact_row("5", "🔄  Converter para áudio",     "converte arquivo local",        _D(),          tw))
    print(compact_line(tw))
    print(compact_row("6", "📁  Alterar pasta",            "muda destino dos downloads",    _D(),          tw))
    print(compact_row("p", "📂  Abrir pasta",              "abre o explorador de arquivos", _D(),          tw))
    print(compact_row("f", "📌  Fila",                      "gerenciar fila de downloads",   _D(),          tw))
    print(compact_row("7", "←   Voltar ao HUB",            "menu principal",                colors.DIM, tw))
    print(compact_row("0", "✕   Sair",                      "encerrar",                      colors.DIM, tw))
    print(compact_line(tw))


def menu(yt_dlp_path, ffmpeg_path):
    save_path = get_pasta_salva(MODULO, "Deezer")

    acoes = {
        "1": lambda sp: baixar_musica(sp, yt_dlp_path, ffmpeg_path, _D(), _validar_url_dz),
        "2": lambda sp: baixar_playlist(sp, yt_dlp_path, ffmpeg_path, _D(),
                                        "playlist", _validar_url_dz),
        "3": lambda sp: baixar_album(sp, yt_dlp_path, ffmpeg_path, _D()),
        "4": lambda sp: baixar_clipe(sp, yt_dlp_path, ffmpeg_path, _D(),
                                     permitir_video=False, validar_url=_validar_url_dz),
        "5": lambda sp: converter_para_audio(sp, ffmpeg_path, _D()),
    }

    try:
        while True:
            from core import config as _cfgmod
            _cfg = _cfgmod.load_config()
            apply_theme_to_module(_cfg, MODULO)
            mostrar_header(animated=True)
            exibir_opcoes(save_path)
            opcao = input(f"\n{_D()}  ❯ {RST}").strip()

            if opcao in acoes:
                acoes[opcao](save_path)
            elif opcao == "6":
                save_path = configurar_pasta(MODULO, _D(), "Deezer")
            elif opcao == "p":
                abrir_pasta(save_path, _D())
            elif opcao == "f":
                from core.downloader import menu_fila
                menu_fila(yt_dlp_path, ffmpeg_path, _D(), save_path, "musica")
            elif opcao == "7":
                animate_exit("Voltando ao HUB", _D())
                break
            elif opcao == "0":
                animate_exit("Até logo", _D())
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

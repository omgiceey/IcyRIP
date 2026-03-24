
import sys
import importlib
from pathlib import Path

from core import colors
import core.config as cfgmod
import locale
import shutil
import os


ASCII = r"""
________  ______   __  __   ______     ________  ______    
/_______/\/_____/\ /_/\/_/\ /_____/\   /_______/\/_____/
\__.::._\/\:::__\/ \ \ \ \ \\:::_ \ \  \__.::._\/\:::_ \ \  
   \::\ \  \:\ \  __\:\_\ \ \\:(_) ) )_   \::\ \  \:(_) \ \ 
   _\::\ \__\:\ \/_//\\::::_\/ \: __ `\ \  _\::\ \__\: ___\/ 
  /__\::\__/\\:\_\ \ \ \::\ \  \ \ `\ \ \/__\::\__/\\ \ \   
  \________\/ \_____\/  \__\/   \_\/ \_\/\________\/ \_\/
"""


def limpar_tela():
    import os

    os.system("cls" if os.name == "nt" else "clear")


def escolher_idioma():
    limpar_tela()
    print(f"{colors.CYAN}{ASCII}{colors.RESET}")
    print(f"{colors.CYAN}ICYRIP - Selecione o idioma / Select language{colors.RESET}")
    print(f"{colors.CYAN}[1]{colors.RESET} Português (pt-BR)")
    print(f"{colors.CYAN}[2]{colors.RESET} English (en)")
    escolha = input(f"{colors.CYAN}Escolha (1/2): {colors.RESET}").strip()
    return "pt" if escolha == "1" else "en"


def prompt_startup_language_choice():
    cfg = cfgmod.load_config()
    if cfg.get('startup_language_asked'):
        return cfg.get('language', 'pt')
    limpar_tela()
    print(f"{colors.CYAN}{ASCII}{colors.RESET}")
    print(f"{colors.CYAN}Deseja usar o idioma detectado pelo sistema (com base nas configurações regionais)?{colors.RESET}")
    print(f"{colors.CYAN}Se não, você poderá escolher manualmente no próximo passo.{colors.RESET}")
    escolha = input(f"{colors.CYAN}Usar idioma do sistema? (s)im / (n)ão: {colors.RESET}").strip().lower()
    if escolha.startswith('s'):
        syslang = locale.getdefaultlocale()[0] or 'pt'
        lang = 'pt' if syslang.lower().startswith('pt') else 'en'
        cfg['language'] = lang
        cfg['use_system_language'] = True
    else:
        novo = escolher_idioma()
        cfg['language'] = novo
        cfg['use_system_language'] = False
    cfg['startup_language_asked'] = True
    cfgmod.save_config(cfg)
    return cfg.get('language', 'pt')


def configure_dependencies_hub():
    
    cfg = cfgmod.load_config()
    limpar_tela()
    print(f"{colors.CYAN}{ASCII}{colors.RESET}")
    print(f"{colors.CYAN}Configuração de Dependências{colors.RESET}")
    print(f"{colors.CYAN}═══════════════════════════════════════════════{colors.RESET}")
    
    found_yt = shutil.which('yt-dlp') or cfg.get('yt_dlp_path')
    found_ff = shutil.which('ffmpeg') or cfg.get('ffmpeg_path')
    print(f"yt-dlp: {colors.GREEN if found_yt else colors.RED}{found_yt or 'Não encontrado'}{colors.RESET}")
    print(f"ffmpeg: {colors.GREEN if found_ff else colors.RED}{found_ff or 'Não encontrado'}{colors.RESET}")
    print("")
    print("[1] Informar caminho do yt-dlp")
    print("[2] Informar caminho do ffmpeg")
    print("[3] Adicionar diretório ao PATH (persistente, opcional)")
    print("[0] Voltar")
    opt = input(f"{colors.CYAN}Escolha: {colors.RESET}").strip()
    if opt == '1':
        p = input(f"{colors.CYAN}Caminho completo para o executável yt-dlp: {colors.RESET}").strip()
        if p:
            cfg['yt_dlp_path'] = p
            cfgmod.save_config(cfg)
            print(f"{colors.GREEN}yt-dlp gravado em config.{colors.RESET}")
    elif opt == '2':
        p = input(f"{colors.CYAN}Caminho completo para o executável ffmpeg: {colors.RESET}").strip()
        if p:
            cfg['ffmpeg_path'] = p
            cfgmod.save_config(cfg)
            print(f"{colors.GREEN}ffmpeg gravado em config.{colors.RESET}")
    elif opt == '3':
        shell = os.environ.get('SHELL', '')
        rc = '~/.zshrc' if 'zsh' in shell else '~/.bashrc'
        dirp = input(f"{colors.CYAN}Digite o diretório a adicionar ao PATH: {colors.RESET}").strip()
        if dirp:
            rcpath = Path(dirp).expanduser()
            
            rcfile = Path(os.path.expanduser(rc))
            line = f'\n# ICYRIP: add yt-dlp/ffmpeg\nexport PATH="$PATH:{dirp}"\n'
            try:
                with rcfile.open('a', encoding='utf-8') as f:
                    f.write(line)
                print(f"{colors.GREEN}Adicionado a {rcfile}. Abra um novo terminal para aplicar.{colors.RESET}")
            except Exception as e:
                print(f"{colors.RED}Falha ao editar {rcfile}: {e}{colors.RESET}")
    else:
        return
    input(f"{colors.CYAN}Pressione Enter para continuar...{colors.RESET}")


def configurar_cores():
    limpar_tela()
    print(f"{colors.CYAN}{ASCII}{colors.RESET}")
    print(f"{colors.CYAN}Tema de cores - escolha um esquema (Enter = padrão){colors.RESET}")
    print(f"{colors.CYAN}[1]{colors.RESET} Padrão (Ciano - Hub, Vermelho - YouTube, Laranja - SoundCloud)")
    print(f"{colors.CYAN}[2]{colors.RESET} Alternativo (Verde - Hub, Vermelho - YouTube, Amarelo - SoundCloud)")
    escolha = input(f"{colors.CYAN}Escolha (Enter p/ padrão): {colors.RESET}").strip()
    cfg = cfgmod.load_config()
    if escolha == "2":
        cfg['theme'] = 'alternative'
    else:
        cfg['theme'] = 'default'
    cfgmod.save_config(cfg)
    apply_theme(cfg.get('theme', 'default'))


def customizar_cores():
    cfg = cfgmod.load_config()
    limpar_tela()
    print(f"{colors.CYAN}{ASCII}{colors.RESET}")
    print(f"{colors.CYAN}Customizar Cores{colors.RESET}")
    print("Escolha qual elemento deseja customizar:")
    print("[1] Hub (Cores do cabeçalho)")
    print("[2] YouTube (vermelho)")
    print("[3] SoundCloud (laranja)")
    print("[0] Voltar")
    escolha = input(f"{colors.CYAN}Escolha: {colors.RESET}").strip()
    key_map = {'1': 'CYAN', '2': 'RED', '3': 'ORANGE'}
    if escolha not in key_map:
        return
    target = key_map[escolha]
    
    palette = [
        ('Black', '\033[30m'),
        ('Red', '\033[31m'),
        ('Green', '\033[32m'),
        ('Yellow', '\033[33m'),
        ('Blue', '\033[34m'),
        ('Magenta', '\033[35m'),
        ('Cyan', '\033[36m'),
        ('White', '\033[37m'),
        ('Bright Cyan', '\033[96m'),
        ('Bright Red', '\033[91m'),
    ]
    print("Paleta disponível:")
    for i, (name, code) in enumerate(palette, start=1):
        print(f"[{i}] {code}{name}{colors.RESET}")
    print("[c] Inserir código 256 (número de 0-255)")
    sel = input(f"{colors.CYAN}Escolha (número ou c): {colors.RESET}").strip().lower()
    chosen = None
    if sel == 'c':
        num = input(f"{colors.CYAN}Digite o código 256 (0-255): {colors.RESET}").strip()
        try:
            n = int(num)
            if 0 <= n <= 255:
                chosen = f"\033[38;5;{n}m"
        except Exception:
            pass
    else:
        try:
            idx = int(sel) - 1
            if 0 <= idx < len(palette):
                chosen = palette[idx][1]
        except Exception:
            pass
    if not chosen:
        print(f"{colors.RED}Seleção inválida.{colors.RESET}")
        input(f"{colors.CYAN}Pressione Enter...{colors.RESET}")
        return
    
    cfg_colors = cfg.get('colors', {}) or {}
    cfg_colors[target] = chosen
    cfg['colors'] = cfg_colors
    cfgmod.save_config(cfg)
    apply_theme(cfg.get('theme', 'default'))
    print(f"{colors.GREEN}Cor atualizada para {target}.{colors.RESET}")
    input(f"{colors.CYAN}Pressione Enter...{colors.RESET}")


def apply_theme(theme_name: str):
    
    if theme_name == 'alternative':
        default_map = {'CYAN': "\033[92m", 'RED': "\033[91m", 'ORANGE': "\033[33m"}
    else:
        default_map = {'CYAN': "\033[96m", 'RED': "\033[91m", 'ORANGE': "\033[38;5;208m"}
   
    try:
        cfg = cfgmod.load_config()
        custom = cfg.get('colors') or {}
    except Exception:
        custom = {}
    for k, v in default_map.items():
        if custom.get(k):
            setattr(colors, k, custom.get(k))
        else:
            setattr(colors, k, v)


def main_menu():
    cfg = cfgmod.load_config()
    apply_theme(cfg.get('theme', 'default'))
    
    lang = prompt_startup_language_choice()
    try:
        while True:
            limpar_tela()
            print(f"{colors.CYAN}{ASCII}{colors.RESET}")
            print(f"{colors.CYAN}✦ ICYRIP v1.2 - HUB ✦ By Icey{colors.RESET}")
            print(f"{colors.CYAN}═══════════════════════════════════════════════{colors.RESET}")
            print(f"{colors.CYAN}[1] YouTube (ICYTB){colors.RESET}")
            print(f"{colors.ORANGE}[2] SoundCloud (ICYSOUND){colors.RESET}")
            print(f"{colors.CYAN}[3] Configurações (Idioma / Cores){colors.RESET}")
            print(f"{colors.CYAN}[4] Verificar/Configurar Dependências{colors.RESET}")
            print(f"{colors.CYAN}[0] Sair{colors.RESET}")
            print(f"{colors.CYAN}═══════════════════════════════════════════════{colors.RESET}")

            opc = input("Selecione a opção: ").strip()
            if opc == "1":
                
                mod = importlib.import_module("ytb")
                
                yt, ff = mod.configurar_dependencias()
                mod.menu(yt, ff)
            elif opc == "2":
                mod = importlib.import_module("sound")
                yt, ff = mod.configurar_dependencias()
                mod.menu(yt, ff)
            elif opc == "3":
                
                cfg = cfgmod.load_config()
                limpar_tela()
                print(f"{colors.CYAN}{ASCII}{colors.RESET}")
                print(f"{colors.CYAN}Configurações Atuais:{colors.RESET}")
                print(f"{colors.CYAN}  Idioma: {colors.RESET}{cfg.get('language', 'pt')}")
                print(f"{colors.CYAN}  Tema: {colors.RESET}{cfg.get('theme', 'default')}")
                print(f"{colors.CYAN}  Limite de Aviso Playlist: {colors.RESET}{cfg.get('playlist_warning_threshold', 50)} itens")
                print(f"{colors.CYAN}═══════════════════════════════════════════════{colors.RESET}")
                print(f"{colors.CYAN}[1]{colors.RESET} Mudar idioma")
                print(f"{colors.CYAN}[2]{colors.RESET} Mudar tema de cores")
                print(f"{colors.CYAN}[3]{colors.RESET} Customizar cores (avançado)")
                print(f"{colors.CYAN}[4]{colors.RESET} Ajustar Limite de Aviso Playlist")
                print(f"{colors.CYAN}[0]{colors.RESET} Voltar")
                c = input(f"{colors.CYAN}Escolha: {colors.RESET}").strip()
                if c == "1":
                    novo = escolher_idioma()
                    cfg['language'] = novo
                    cfgmod.save_config(cfg)
                    print(f"{colors.GREEN}Idioma alterado para: {novo}{colors.RESET}")
                    input(f"{colors.CYAN}Pressione Enter...{colors.RESET}")
                elif c == "2":
                    configurar_cores()
                    print(f"{colors.GREEN}Tema aplicado.{colors.RESET}")
                    input(f"{colors.CYAN}Pressione Enter...{colors.RESET}")
                elif c == "3":
                    customizar_cores()
                    print(f"{colors.GREEN}Cores customizadas.{colors.RESET}")
                    input(f"{colors.CYAN}Pressione Enter...{colors.RESET}")
                elif c == "4":
                    val = input(f"{colors.CYAN}Novo Limite de Aviso Playlist (número de itens que dispara aviso, Enter mantém {cfg.get('playlist_warning_threshold',50)}): {colors.RESET}").strip()
                    if val:
                        try:
                            ival = int(val)
                            cfg['playlist_warning_threshold'] = max(1, ival)
                            cfgmod.save_config(cfg)
                            print(f"{colors.GREEN}Limite de Aviso Playlist alterado para {cfg['playlist_warning_threshold']}{colors.RESET}")
                        except Exception:
                            print(f"{colors.RED}Valor inválido.{colors.RESET}")
                    input(f"{colors.CYAN}Pressione Enter...{colors.RESET}")
            elif opc == "4":
                configure_dependencies_hub()
            elif opc == "0":
                print(f"{colors.CYAN}Saindo...{colors.RESET}")
                break
            else:
                print("Opção inválida.")
                input("Pressione Enter para continuar...")
    except KeyboardInterrupt:
        print()
        print(f"{colors.CYAN}Encerrando...{colors.RESET}")


if __name__ == "__main__":
    main_menu()

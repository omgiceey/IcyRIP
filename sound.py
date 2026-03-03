import os
import platform
import subprocess
import sys
import time

RED = "\033[91m"
RESET = "\033[0m"
GREEN = "\033[92m"


def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")


def mostrar_header():
    limpar_tela()
    print(
        f"""{RED}
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
{RESET}"""
    )
    print(f"{RED}✦ ICYSOUND SoundCloud | v1.2 ✦ By Icey — Powered by yt-dlp{RESET}")
    print(f"{RED}═══════════════════════════════════════════════{RESET}")


def configurar_pasta():
    sistema = platform.system()
    pasta_padrao = os.path.expanduser("~\\Downloads\\SoundCloud") if sistema == "Windows" else os.path.expanduser("~/SoundCloud")

    save_path = input(f"{RED}Digite o caminho para salvar as músicas (Enter para padrão {pasta_padrao}): {RESET}").strip()
    if not save_path:
        save_path = pasta_padrao

    if not os.path.isdir(save_path):
        os.makedirs(save_path, exist_ok=True)
        print(f"{GREEN}Pasta criada: {save_path}{RESET}")
    else:
        print(f"{GREEN}Pasta configurada: {save_path}{RESET}")
    return save_path


def resolver_ffmpeg_location(ffmpeg_path):
    if os.path.isabs(ffmpeg_path) or os.path.sep in ffmpeg_path:
        diretorio = os.path.dirname(ffmpeg_path)
        return diretorio if diretorio else ffmpeg_path
    return ffmpeg_path


def validar_dependencia(comando, nome):
    try:
        subprocess.run(comando, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        print(f"{RED}{nome} não encontrado! Instale ou configure o caminho correto.{RESET}")
    except subprocess.CalledProcessError:
        print(f"{RED}{nome} falhou ao executar. Verifique a instalação.{RESET}")
    return False


def configurar_dependencias():
    sistema = platform.system()

    yt_dlp_path = input(f"{RED}Caminho do yt-dlp (Enter se estiver no PATH): {RESET}").strip()
    if not yt_dlp_path:
        yt_dlp_path = "yt-dlp.exe" if sistema == "Windows" else "yt-dlp"

    ffmpeg_path = input(f"{RED}Caminho do ffmpeg (Enter se estiver no PATH): {RESET}").strip()
    if not ffmpeg_path:
        ffmpeg_path = "ffmpeg.exe" if sistema == "Windows" else "ffmpeg"

    if not validar_dependencia([yt_dlp_path, "--version"], "yt-dlp"):
        sys.exit(1)
    if not validar_dependencia([ffmpeg_path, "-version"], "ffmpeg"):
        sys.exit(1)

    return yt_dlp_path, ffmpeg_path


def executar_comando(comando, mensagem_erro):
    try:
        subprocess.run(comando, check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"{RED}{mensagem_erro}{RESET}")
        return False


def baixar_musica(save_path, yt_dlp_path, ffmpeg_path):
    url = input(f"{RED}Digite o link da música/playlist do SoundCloud: {RESET}").strip()
    if not url:
        print(f"{RED}Nenhum link informado.{RESET}")
        input(f"{RED}Pressione Enter para continuar...{RESET}")
        return

    comando = [
        yt_dlp_path,
        "--extract-audio",
        "--audio-format",
        "mp3",
        "--ffmpeg-location",
        resolver_ffmpeg_location(ffmpeg_path),
        "-o",
        os.path.join(save_path, "%(title)s.%(ext)s"),
        url,
    ]
    print(f"{RED}Baixando...{RESET}")
    if executar_comando(comando, "Falha no download do SoundCloud."):
        print(f"{GREEN}Download concluído! Salvo em: {save_path}{RESET}")
    input(f"{RED}Pressione Enter para continuar...{RESET}")


def exibir_opcoes():
    print(f"{RED}═══════════════════════════════════════════════{RESET}")
    print(f"{RED}[1] Baixar música/playlist do SoundCloud{RESET}")
    print(f"{RED}[0] Sair{RESET}")
    print(f"{RED}═══════════════════════════════════════════════{RESET}")


def menu(yt_dlp_path, ffmpeg_path):
    save_path = configurar_pasta()
    while True:
        mostrar_header()
        exibir_opcoes()
        opcao = input(f"{RED}Selecione a opção: {RESET}").strip()
        if opcao == "1":
            baixar_musica(save_path, yt_dlp_path, ffmpeg_path)
        elif opcao == "0":
            print(f"{RED}Saindo...{RESET}")
            break
        else:
            print(f"{RED}Opção inválida.{RESET}")
            time.sleep(1)


if __name__ == "__main__":
    mostrar_header()
    yt_dlp_path, ffmpeg_path = configurar_dependencias()
    menu(yt_dlp_path, ffmpeg_path)

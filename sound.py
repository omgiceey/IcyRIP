import os
import platform
import subprocess
import sys
import time
import shutil
from pathlib import Path

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
    pasta_padrao = Path.home() / ("Downloads" if sistema == "Windows" else "") / ("SoundCloud")

    save_path = input(f"{RED}Digite o caminho para salvar as músicas (Enter para padrão {pasta_padrao}): {RESET}").strip()
    if not save_path:
        save_path = str(pasta_padrao)

    save_dir = Path(save_path).expanduser()
    if not save_dir.exists():
        save_dir.mkdir(parents=True, exist_ok=True)
        print(f"{GREEN}Pasta criada: {save_dir}{RESET}")
    else:
        print(f"{GREEN}Pasta configurada: {save_dir}{RESET}")
    return str(save_dir.resolve())


def resolver_ffmpeg_location(ffmpeg_path):
    if os.path.isdir(ffmpeg_path):
        return ffmpeg_path
    if os.path.isabs(ffmpeg_path) or os.path.sep in ffmpeg_path:
        diretorio = os.path.dirname(ffmpeg_path)
        return diretorio if diretorio else ffmpeg_path
    found = shutil.which(ffmpeg_path)
    if found:
        return os.path.dirname(found)
    return ffmpeg_path

def localizar_executavel(user_input, default_name):
    if user_input:
        p = Path(user_input).expanduser()
        if p.is_file() and os.access(str(p), os.X_OK):
            return str(p)
        if p.is_dir():
            cand = p / default_name
            if cand.is_file() and os.access(str(cand), os.X_OK):
                return str(cand)
    return shutil.which(default_name)


def validar_dependencia(comando, nome):
    try:
        proc = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode == 0:
            return True
        else:
            print(f"{RED}{nome} falhou ao executar. Saída: {proc.stderr}{RESET}")
    except FileNotFoundError:
        print(f"{RED}{nome} não encontrado! Instale ou configure o caminho correto.{RESET}")
    except Exception as e:
        print(f"{RED}Erro ao validar {nome}: {e}{RESET}")
    return False


def configurar_dependencias():
    sistema = platform.system()
    yt_input = input(f"{RED}Caminho do yt-dlp (Enter se estiver no PATH): {RESET}").strip()
    default_yt = "yt-dlp.exe" if sistema == "Windows" else "yt-dlp"
    yt_dlp_path = localizar_executavel(yt_input, default_yt) or shutil.which(default_yt)

    ff_input = input(f"{RED}Caminho do ffmpeg (Enter se estiver no PATH): {RESET}").strip()
    default_ff = "ffmpeg.exe" if sistema == "Windows" else "ffmpeg"
    ffmpeg_path = localizar_executavel(ff_input, default_ff) or shutil.which(default_ff)

    if not yt_dlp_path or not validar_dependencia([yt_dlp_path, "--version"], "yt-dlp"):
        print(f"{RED}yt-dlp não encontrado ou inválido. Instale ou informe o caminho correto.{RESET}")
        sys.exit(1)
    if not ffmpeg_path or not validar_dependencia([ffmpeg_path, "-version"], "ffmpeg"):
        print(f"{RED}ffmpeg não encontrado ou inválido. Instale ou informe o caminho correto.{RESET}")
        sys.exit(1)

    return yt_dlp_path, ffmpeg_path


def executar_comando(comando, mensagem_erro):
    try:
        proc = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode == 0:
            return True
        else:
            print(f"{RED}{mensagem_erro}\n{proc.stderr}{RESET}")
            return False
    except FileNotFoundError:
        print(f"{RED}Comando não encontrado: {comando[0]}{RESET}")
        return False
    except Exception as e:
        print(f"{RED}Erro ao executar comando: {e}{RESET}")
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
        "--restrict-filenames",
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
    try:
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
    except KeyboardInterrupt:
        print(f"\n{RED}Encerrando...{RESET}")


if __name__ == "__main__":
    mostrar_header()
    yt_dlp_path, ffmpeg_path = configurar_dependencias()
    menu(yt_dlp_path, ffmpeg_path)

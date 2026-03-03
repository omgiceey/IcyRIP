import os
import platform
import subprocess
import re
import sys
import time
import shutil
from pathlib import Path

RED = "\033[91m"
RESET = "\033[0m"
GREEN = "\033[92m"
VERBOSE = False


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


def parse_progress(line):
    m = re.search(r"(?P<pct>\d{1,3}(?:\.\d+)?)%.*?of\s+(?P<total>[\d\.]+[KMGT]?i?B).*?at\s+(?P<speed>[\d\.]+[KMGT]?i?B/s).*?ETA\s+(?P<eta>\S+)", line)
    if m:
        return m.groupdict()
    m = re.search(r"(?P<pct>\d{1,3}(?:\.\d+)?)%.*?at\s+(?P<speed>[\d\.]+[KMGT]?i?B/s).*?ETA\s+(?P<eta>\S+)", line)
    if m:
        return {'pct': m.group('pct'), 'speed': m.group('speed'), 'eta': m.group('eta')}
    m = re.search(r"time=(?P<time>\S+).*?bitrate=\s*(?P<bitrate>\S+).*?speed=\s*(?P<speed>\S+)", line)
    if m:
        return {'time': m.group('time'), 'bitrate': m.group('bitrate'), 'speed': m.group('speed')}
    return None


def render_progress_line(pct, total=None, speed=None, eta=None, color=RED, width=30):
    try:
        p = float(pct)
    except Exception:
        p = None
    if p is None:
        return f"{color}{pct}{RESET}"

    filled = int((p / 100.0) * width)
    bar = '[' + '#' * filled + '-' * (width - filled) + ']'
    parts = [bar, f"{p:.0f}%"]
    if speed:
        parts.append(f"{speed}")
    return f"{color}{' '.join(parts)}{RESET}"


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
        p = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        pct = None
        pattern = re.compile(r"(?P<pct>\d{1,3}(?:\.\d)?)%")
        other_lines = []
        for line in p.stdout:
            line = line.rstrip('\n')
            prog = parse_progress(line)
            if prog and 'pct' in prog:
                pct = prog.get('pct')
                speed = prog.get('speed')
                line_out = render_progress_line(pct, speed=speed, color=RED)
                sys.stdout.write(f"\r{line_out}")
                sys.stdout.flush()
            elif prog and 'time' in prog:
                t = prog.get('time')
                sp = prog.get('speed')
                if VERBOSE:
                    sys.stdout.write(f"\r{RED}time={t} speed={sp}{RESET}")
                    sys.stdout.flush()
            else:
                if VERBOSE:
                    print(line)
                else:
                    other_lines.append(line)
        p.wait()
        if pct is not None:
            print()
        if p.returncode == 0:
            if pct is not None:
                print()
            return True
        else:
            print(f"{RED}{mensagem_erro}{RESET}")
            if other_lines:
                print('\n'.join(other_lines))
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

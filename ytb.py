import os
import platform
import subprocess
import re
import sys
import time
import shutil
from pathlib import Path

CYAN = "\033[96m"
RESET = "\033[0m"
GREEN = "\033[92m"
RED = "\033[91m"
VERBOSE = False


def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")


def mostrar_header():
    limpar_tela()
    print(
        f"""{CYAN}
██╗ ██████╗██╗   ██╗████████╗██████╗ 
██║██╔════╝╚██╗ ██╔╝╚══██╔══╝██╔══██╗
██║██║      ╚████╔╝    ██║   ██████╔╝
██║██║       ╚██╔╝     ██║   ██╔══██╗
██║╚██████╗   ██║      ██║   ██████╔╝
╚═╝ ╚═════╝   ╚═╝      ╚═╝   ╚═════╝
{RESET}"""
    )
    print(f"{CYAN}✦ ICYRIP | v1.6 ✦ By Icey — Powered by yt-dlp{RESET}")
    print(f"{CYAN}═══════════════════════════════════════════════{RESET}")


def parse_progress(line):
    # tenta padrões comuns do yt-dlp: percent, total, speed e ETA
    m = re.search(r"(?P<pct>\d{1,3}(?:\.\d+)?)%.*?of\s+(?P<total>[\d\.]+[KMGT]?i?B).*?at\s+(?P<speed>[\d\.]+[KMGT]?i?B/s).*?ETA\s+(?P<eta>\S+)", line)
    if m:
        return m.groupdict()
    m = re.search(r"(?P<pct>\d{1,3}(?:\.\d+)?)%.*?at\s+(?P<speed>[\d\.]+[KMGT]?i?B/s).*?ETA\s+(?P<eta>\S+)", line)
    if m:
        return {'pct': m.group('pct'), 'speed': m.group('speed'), 'eta': m.group('eta')}
    # padrão do ffmpeg (time/bitrate/speed)
    m = re.search(r"time=(?P<time>\S+).*?bitrate=\s*(?P<bitrate>\S+).*?speed=\s*(?P<speed>\S+)", line)
    if m:
        return {'time': m.group('time'), 'bitrate': m.group('bitrate'), 'speed': m.group('speed')}
    return None


def render_progress_line(pct, total=None, speed=None, eta=None, color=CYAN, width=30):
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
    pasta_padrao = Path.home() / ("Downloads" if sistema == "Windows" else "") / ("Musicas" if sistema == "Windows" else "Músicas")

    print(f"{CYAN}Pasta de destino:{RESET} ", end="")
    save_path = input(
        f"{CYAN}Digite o caminho completo da pasta ou pressione Enter para usar o padrão ({pasta_padrao}): {RESET}"
    ).strip()
    if not save_path:
        save_path = str(pasta_padrao)

    save_dir = Path(save_path).expanduser()
    if not save_dir.exists():
        save_dir.mkdir(parents=True, exist_ok=True)
        print(f"{GREEN}Pasta criada em: {save_dir}{RESET}")
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
    found = shutil.which(default_name)
    return found


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
    print(f"{CYAN}Configuração das dependências:{RESET}")
    yt_dlp_input = input(f"{CYAN}Digite o caminho do yt-dlp (ou Enter se estiver no PATH): {RESET}").strip()
    default_yt = "yt-dlp.exe" if sistema == "Windows" else "yt-dlp"
    yt_dlp_path = localizar_executavel(yt_dlp_input, default_yt) or shutil.which(default_yt)

    ffmpeg_input = input(f"{CYAN}Digite o caminho do ffmpeg (ou Enter se estiver no PATH): {RESET}").strip()
    default_ff = "ffmpeg.exe" if sistema == "Windows" else "ffmpeg"
    ffmpeg_path = localizar_executavel(ffmpeg_input, default_ff) or shutil.which(default_ff)

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
                line_out = render_progress_line(pct, speed=speed, color=CYAN)
                sys.stdout.write(f"\r{line_out}")
                sys.stdout.flush()
            elif prog and 'time' in prog:
                # ffmpeg-like short info when available
                t = prog.get('time')
                sp = prog.get('speed')
                if VERBOSE:
                    sys.stdout.write(f"\r{CYAN}time={t} speed={sp}{RESET}")
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
            # clear progress line
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


def baixar_playlist(save_path, yt_dlp_path, ffmpeg_path):
    playlist_url = input(f"{CYAN}Digite o link da playlist do YouTube: {RESET}").strip()
    if not playlist_url:
        print(f"{RED}Nenhum link informado.{RESET}")
        input(f"{CYAN}Pressione Enter para continuar...{RESET}")
        return

    # permitir ao usuário escolher formato além de MP3
    formato = escolher_formato_audio()

    comando = [
        yt_dlp_path,
        "--extract-audio",
        "--audio-format",
        formato,
        "--restrict-filenames",
        "--ffmpeg-location",
        resolver_ffmpeg_location(ffmpeg_path),
        "-o",
        os.path.join(save_path, "%(title)s.%(ext)s"),
        playlist_url,
    ]
    print(f"{CYAN}Baixando a playlist...{RESET}")
    if executar_comando(comando, "Falha ao baixar playlist."):
        print(f"{GREEN}Playlist baixada com sucesso! Salva em: {save_path}{RESET}")
    input(f"{CYAN}Pressione Enter para continuar...{RESET}")


def baixar_musica(save_path, yt_dlp_path, ffmpeg_path):
    musica_url = input(f"{CYAN}Digite a URL da música que deseja baixar: {RESET}").strip()
    if not musica_url:
        print(f"{RED}Nenhum link informado.{RESET}")
        input(f"{CYAN}Pressione Enter para continuar...{RESET}")
        return

    # permitir ao usuário escolher formato além de MP3
    formato = escolher_formato_audio()

    comando = [
        yt_dlp_path,
        "--extract-audio",
        "--audio-format",
        formato,
        "--restrict-filenames",
        "--ffmpeg-location",
        resolver_ffmpeg_location(ffmpeg_path),
        "-o",
        os.path.join(save_path, "%(title)s.%(ext)s"),
        musica_url,
    ]
    print(f"{CYAN}Baixando a música...{RESET}")
    if executar_comando(comando, "Falha ao baixar música."):
        print(f"{GREEN}Música baixada com sucesso! Salva em: {save_path}{RESET}")
    input(f"{CYAN}Pressione Enter para continuar...{RESET}")


def escolher_formato_audio(default="mp3"):
    """Permite ao usuário escolher o formato de saída de áudio."""
    opcoes = ["mp3", "m4a", "opus", "wav", "aac", "flac", "ogg"]
    escolha = input(f"{CYAN}Formato de saída (padrão {default}). Opções: {', '.join(opcoes)}: {RESET}").strip().lower()
    if not escolha:
        return default
    if escolha in opcoes:
        return escolha
    print(f"{RED}Formato inválido. Usando {default}.{RESET}")
    return default


def converter_para_audio(save_path, ffmpeg_path):
    arquivo = input(f"{CYAN}Digite o nome do arquivo (com extensão) para converter: {RESET}").strip()
    if not arquivo or "." not in arquivo:
        print(f"{RED}Arquivo inválido. Informe nome com extensão.{RESET}")
        input(f"{CYAN}Pressione Enter para continuar...{RESET}")
        return

    entrada = os.path.join(save_path, arquivo)
    if not os.path.isfile(entrada):
        print(f"{RED}Arquivo não encontrado: {entrada}{RESET}")
        input(f"{CYAN}Pressione Enter para continuar...{RESET}")
        return

    formato = escolher_formato_audio()
    saida = os.path.join(save_path, arquivo.rsplit(".", 1)[0] + f".{formato}")
    comando = [ffmpeg_path, "-y", "-i", entrada, saida]
    print(f"{CYAN}Convertendo para {formato}...{RESET}")
    if executar_comando(comando, f"Falha ao converter arquivo para {formato}."):
        print(f"{GREEN}Conversão concluída! Salvo em: {saida}{RESET}")
    input(f"{CYAN}Pressione Enter para continuar...{RESET}")


def exibir_opcoes():
    print(f"{CYAN}═══════════════════════════════════════════════{RESET}")
    print(f"{CYAN}[1] Baixar Playlist{RESET}")
    print(f"{CYAN}[2] Baixar Música{RESET}")
    print(f"{CYAN}[3] Converter para MP3{RESET}")
    print(f"{CYAN}[0] Sair{RESET}")
    print(f"{CYAN}═══════════════════════════════════════════════{RESET}")


def menu(yt_dlp_path, ffmpeg_path):
    save_path = configurar_pasta()
    try:
        while True:
            mostrar_header()
            exibir_opcoes()
            opcao = input(f"{CYAN}Selecione a opção: {RESET}").strip()
            if opcao == "1":
                baixar_playlist(save_path, yt_dlp_path, ffmpeg_path)
            elif opcao == "2":
                baixar_musica(save_path, yt_dlp_path, ffmpeg_path)
            elif opcao == "3":
                converter_para_audio(save_path, ffmpeg_path)
            elif opcao == "0":
                print(f"{CYAN}Saindo...{RESET}")
                break
            else:
                print(f"{RED}Opção inválida. Tente novamente.{RESET}")
                time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{CYAN}Encerrando...{RESET}")


if __name__ == "__main__":
    mostrar_header()
    yt_dlp_path, ffmpeg_path = configurar_dependencias()
    menu(yt_dlp_path, ffmpeg_path)

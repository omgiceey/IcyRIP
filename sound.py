import os
import platform
import subprocess
import re
import sys
import time
import shutil
from pathlib import Path
import json

import core.colors as colors
VERBOSE = False


def limpar_tela():
    os.system("cls" if os.name == "nt" else "clear")


def mostrar_header():
    limpar_tela()
    print(
        f"""{colors.ORANGE}
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
{colors.RESET}"""
    )
    print(f"{colors.ORANGE}✦ ICYSOUND SoundCloud | v1.8 ✦ By Icey — Powered by yt-dlp{colors.RESET}")
    print(f"{colors.ORANGE}═══════════════════════════════════════════════{colors.RESET}")


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


def render_progress_line(pct, total=None, speed=None, eta=None, color=colors.ORANGE, width=30):
    
    try:
        p = float(pct)
    except Exception:
        p = None
    if p is None:
        return f"{color}{pct}{colors.RESET}"

    bar_width = width
    filled = int((p / 100.0) * bar_width)
    empty = bar_width - filled
    bar = '█' * filled + '░' * max(0, empty)

    pct_text = f"{p:.0f}%"
    info_parts = [pct_text]
    if speed:
        info_parts.append(f"{speed}")
    if eta:
        info_parts.append(f"ETA: {eta}")
    info = " | ".join(info_parts)

    return f"{color}[{bar}] {info}{colors.RESET}"


def configurar_pasta():
    sistema = platform.system()
    pasta_padrao = Path.home() / ("Downloads" if sistema == "Windows" else "") / ("SoundCloud")

    save_path = input(f"{colors.ORANGE}Digite o caminho para salvar as músicas (Enter para padrão {pasta_padrao}): {colors.RESET}").strip()
    if not save_path:
        save_path = str(pasta_padrao)

    save_dir = Path(save_path).expanduser()
    if not save_dir.exists():
        save_dir.mkdir(parents=True, exist_ok=True)
        print(f"{colors.GREEN}Pasta criada: {save_dir}{colors.RESET}")
    else:
        print(f"{colors.GREEN}Pasta configurada: {save_dir}{colors.RESET}")
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


def get_playlist_entries(yt_dlp_path, url):
    
    try:
        proc = subprocess.run([yt_dlp_path, "--flat-playlist", "--dump-json", url], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            return []
        titles = []
        for line in proc.stdout.splitlines():
            try:
                obj = json.loads(line)
            except Exception:
                continue
            title = obj.get('title') or obj.get('fulltitle') or obj.get('id')
            titles.append(title)
        return titles
    except Exception:
        return []


def get_playlist_stats(yt_dlp_path, url):
    
    try:
        proc = subprocess.run([yt_dlp_path, "--dump-json", url], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode != 0:
            return {'count': None, 'total_duration': None, 'total_size': None}
        total_duration = 0
        total_size = 0
        count = 0
        any_duration = False
        any_size = False
        for line in proc.stdout.splitlines():
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            count += 1
            dur = obj.get('duration')
            if isinstance(dur, (int, float)):
                total_duration += int(dur)
                any_duration = True

            size = obj.get('filesize') or obj.get('filesize_approx')
            if isinstance(size, (int, float)):
                total_size += int(size)
                any_size = True
            else:
                fmts = obj.get('formats') or []
                best = 0
                for f in fmts:
                    fs = f.get('filesize') or f.get('filesize_approx')
                    if isinstance(fs, (int, float)) and fs > best:
                        best = int(fs)
                if best:
                    total_size += best
                    any_size = True

        return {
            'count': count if count > 0 else None,
            'total_duration': total_duration if any_duration else None,
            'total_size': total_size if any_size else None,
        }
    except Exception:
        return {'count': None, 'total_duration': None, 'total_size': None}


def _format_bytes(n):
    if n is None:
        return None
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if n < 1024.0:
            return f"{n:.1f}{unit}"
        n /= 1024.0
    return f"{n:.1f}PB"


def _format_duration(s):
    if s is None:
        return None
    m, sec = divmod(int(s), 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m}m {sec}s"
    if m:
        return f"{m}m {sec}s"
    return f"{sec}s"


def validar_dependencia(comando, nome):
    try:
        proc = subprocess.run(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if proc.returncode == 0:
            return True
        else:
            print(f"{colors.RED}{nome} falhou ao executar. Saída: {proc.stderr}{colors.RESET}")
    except FileNotFoundError:
        print(f"{colors.RED}{nome} não encontrado! Instale ou configure o caminho correto.{colors.RESET}")
    except Exception as e:
        print(f"{colors.RED}Erro ao validar {nome}: {e}{colors.RESET}")
    return False


def escolher_formato_audio(default="mp3"):
    
    opcoes = ["mp3", "wav"]
    escolha = input(f"{colors.ORANGE}Formato de saída (padrão {default.upper()}). Opções: MP3, WAV: {colors.RESET}").strip().lower()
    if not escolha:
        return default.lower()
    if escolha in opcoes:
        return escolha
    print(f"{colors.RED}Formato inválido. Usando {default.upper()}.{colors.RESET}")
    return default.lower()


def perguntar_embutir_capa(default=True):
    pad = 's' if default else 'n'
    resp = input(f"{colors.ORANGE}Deseja embutir a capa no arquivo final? (s/n) [padrão {pad}]: {colors.RESET}").strip().lower()
    if not resp:
        return default
    return resp.startswith('s')


def configurar_dependencias():
    
    try:
        from core import config as _config
        cfg = _config.load_config()
    except Exception:
        cfg = {}

    yt_dlp_path = cfg.get('yt_dlp_path') or shutil.which('yt-dlp')
    ffmpeg_path = cfg.get('ffmpeg_path') or shutil.which('ffmpeg')

    if not yt_dlp_path or not validar_dependencia([yt_dlp_path, "--version"], "yt-dlp"):
        print(f"{colors.RED}yt-dlp não configurado ou inválido. Configure pelo HUB (Verificar/Configurar Dependências).{colors.RESET}")
        return None, None
    if not ffmpeg_path or not validar_dependencia([ffmpeg_path, "-version"], "ffmpeg"):
        print(f"{colors.RED}ffmpeg não configurado ou inválido. Configure pelo HUB (Verificar/Configurar Dependências).{colors.RESET}")
        return None, None

    return yt_dlp_path, ffmpeg_path


def executar_comando(comando, mensagem_erro, entries_list=None):
    try:
        p = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        pct = None
        current_title = None
        printed_title = False
        idx = None
        total = None
        other_lines = []
        for line in p.stdout:
            line = line.rstrip('\n')

            
            m_idx = re.search(r"Downloading (?:video|playlist item) (?P<idx>\d+) of (?P<total>\d+)", line)
            if m_idx:
                try:
                    idx = int(m_idx.group('idx'))
                    total = int(m_idx.group('total'))
                except Exception:
                    idx = None
                    total = None

            
            m_dest = re.search(r"\[download\] Destination: (?P<path>.+)$", line) or re.search(r"Destination: (?P<path>.+)$", line)
            if m_dest:
                path = m_dest.group('path').strip()
                current_title = os.path.basename(path)
                
                if entries_list and not idx:
                    def _norm(s):
                        return re.sub(r"\W+", " ", s or "").strip().lower()
                    cur = _norm(os.path.splitext(current_title)[0])
                    for i, e in enumerate(entries_list):
                        if not e:
                            continue
                        if cur in _norm(e) or _norm(e) in cur:
                            idx = i + 1
                            total = len(entries_list)
                            break

            prog = parse_progress(line)
            if prog and 'pct' in prog:
                pct = prog.get('pct')
                speed = prog.get('speed')
                eta = prog.get('eta') if 'eta' in prog else None
                
                if current_title and not printed_title:
                    title_display = current_title
                    
                    print()
                    if idx and total:
                        print(f"{colors.ORANGE}[{idx}/{total}] {title_display}{colors.RESET}")
                    else:
                        print(f"{colors.ORANGE}{title_display}{colors.RESET}")
                    printed_title = True
                   
                    line_out = render_progress_line(pct, total=total, speed=speed, eta=eta, color=colors.ORANGE)
                    sys.stdout.write(f"{line_out}")
                    sys.stdout.flush()
                else:
                    line_out = render_progress_line(pct, total=total, speed=speed, eta=eta, color=colors.ORANGE)
                    sys.stdout.write(f"\r{line_out}")
                    sys.stdout.flush()
            elif prog and 'time' in prog:
                t = prog.get('time')
                sp = prog.get('speed')
                if VERBOSE:
                    sys.stdout.write(f"\r{colors.ORANGE}time={t} speed={sp}{colors.RESET}")
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
            return True, current_title
        else:
            print(f"{colors.RED}{mensagem_erro}{colors.RESET}")
            if other_lines:
                print('\n'.join(other_lines))
            return False, None
    except FileNotFoundError:
        print(f"{colors.RED}Comando não encontrado: {comando[0]}{colors.RESET}")
        return False, None
    except Exception as e:
        print(f"{colors.RED}Erro ao executar comando: {e}{colors.RESET}")
        return False, None


def baixar_musica(save_path, yt_dlp_path, ffmpeg_path):
    url = input(f"{colors.ORANGE}Digite o link da música do SoundCloud: {colors.RESET}").strip()
    if not url:
        print(f"{colors.RED}Nenhum link informado.{colors.RESET}")
        input(f"{colors.ORANGE}Pressione Enter para continuar...{colors.RESET}")
        return
    if "soundcloud.com" not in url.lower():
        print(f"{colors.RED}URL inválida: este módulo aceita apenas links do SoundCloud.{colors.RESET}")
        input(f"{colors.ORANGE}Pressione Enter para continuar...{colors.RESET}")
        return

    formato = escolher_formato_audio()

    embutir = perguntar_embutir_capa(default=True)
    postproc = ["--add-metadata"]
    if embutir:
        postproc.append("--embed-thumbnail")

    comando = [
        yt_dlp_path,
        "--extract-audio",
        "--audio-format",
        formato,
        "--restrict-filenames",
        "--ffmpeg-location",
        resolver_ffmpeg_location(ffmpeg_path),
    ] + postproc + [
        "--concurrent-fragments", "4",
        "--no-part",
        "--no-cache-dir",
        "--retries", "10",
        "--fragment-retries", "10",
        "--ignore-errors",
        "--no-overwrites",
        "-o",
        os.path.join(save_path, "%(title)s.%(ext)s"),
        url,
    ]
    print(f"{colors.ORANGE}Baixando...{colors.RESET}")
    success, title = executar_comando(comando, "Falha no download do SoundCloud.", None)
    if success:
        print(f"{colors.GREEN}Download concluído! Salvo em: {save_path}{colors.RESET}")
        
    input(f"{colors.ORANGE}Pressione Enter para continuar...{colors.RESET}")


def exibir_opcoes():
    print(f"{colors.ORANGE}═══════════════════════════════════════════════{colors.RESET}")
    print(f"{colors.ORANGE}[1] Baixar música do SoundCloud{colors.RESET}")
    print(f"{colors.ORANGE}[2] Baixar álbum/playlist do SoundCloud{colors.RESET}")
    print(f"{colors.ORANGE}[0] Sair{colors.RESET}")
    print(f"{colors.ORANGE}═══════════════════════════════════════════════{colors.RESET}")


def menu(yt_dlp_path, ffmpeg_path):
    save_path = configurar_pasta()
    try:
        while True:
            mostrar_header()
            exibir_opcoes()
            opcao = input(f"{colors.ORANGE}Selecione a opção: {colors.RESET}").strip()
            if opcao == "1":
                baixar_musica(save_path, yt_dlp_path, ffmpeg_path)
            elif opcao == "2":
                
                url = input(f"{colors.ORANGE}Digite o link da playlist/álbum do SoundCloud: {colors.RESET}").strip()
                if not url:
                    print(f"{colors.RED}Nenhum link informado.{colors.RESET}")
                    input(f"{colors.ORANGE}Pressione Enter para continuar...{colors.RESET}")
                elif "soundcloud.com" not in url.lower():
                    print(f"{colors.RED}URL inválida: este módulo aceita apenas links do SoundCloud.{colors.RESET}")
                    input(f"{colors.ORANGE}Pressione Enter para continuar...{colors.RESET}")
                else:
                    formato = escolher_formato_audio()
                    out_template = os.path.join(save_path, "%(playlist_index)s - %(title)s.%(ext)s")
                    embutir = perguntar_embutir_capa(default=True)
                    postproc = ["--add-metadata"]
                    if embutir:
                        postproc.append("--embed-thumbnail")

                    comando = [
                        yt_dlp_path,
                        "--extract-audio",
                        "--audio-format",
                        formato,
                        "--restrict-filenames",
                        "--ffmpeg-location",
                        resolver_ffmpeg_location(ffmpeg_path),
                    ] + postproc + [
                        "--concurrent-fragments", "4",
                        "--no-part",
                        "--no-cache-dir",
                        "--retries", "10",
                        "--fragment-retries", "10",
                        "--ignore-errors",
                        "--no-overwrites",
                        "-o",
                        out_template,
                        url,
                    ]
                    
                    entries = get_playlist_entries(yt_dlp_path, url)
                    if entries:
                        print(f"{colors.ORANGE}Playlist detectada: {len(entries)} itens{colors.RESET}")
                        
                        try:
                            from core import config as _config
                            thresh = _config.load_config().get('playlist_warning_threshold', 50)
                        except Exception:
                            thresh = 50
                        if len(entries) > 1:
                            resp = input(f"{colors.ORANGE}Deseja baixar todos os {len(entries)} itens? (s/n): {colors.RESET}").strip().lower()
                            if not resp.startswith('s'):
                                print(f"{colors.ORANGE}Operação cancelada pelo usuário.{colors.RESET}")
                                input(f"{colors.ORANGE}Pressione Enter para continuar...{colors.RESET}")
                                continue
                        if len(entries) > thresh:
                            stats = get_playlist_stats(yt_dlp_path, url)
                            dur = _format_duration(stats.get('total_duration'))
                            size = _format_bytes(stats.get('total_size'))
                            est_parts = []
                            if dur:
                                est_parts.append(f"duração ~ {dur}")
                            if size:
                                est_parts.append(f"tamanho ~ {size}")
                            est_text = (" — " + ", ".join(est_parts)) if est_parts else ""

                            resp2 = input(f"{colors.ORANGE}AVISO: você está prestes a baixar uma playlist grande ({len(entries)} itens){est_text}. Pode demorar bastante, pode haver variações de velocidade. Não feche o programa. Deseja continuar? (s/n): {colors.RESET}").strip().lower()
                            if not resp2.startswith('s'):
                                print(f"{colors.ORANGE}Operação cancelada pelo usuário.{colors.RESET}")
                                input(f"{colors.ORANGE}Pressione Enter para continuar...{colors.RESET}")
                                continue
                    print(f"{colors.ORANGE}Baixando playlist/álbum...{colors.RESET}")
                    success, title = executar_comando(comando, "Falha no download do SoundCloud.", entries)
                    if success:
                        print(f"{colors.GREEN}Download concluído! Salvo em: {save_path}{colors.RESET}")
                        
                    input(f"{colors.ORANGE}Pressione Enter para continuar...{colors.RESET}")
            elif opcao == "0":
                print(f"{colors.ORANGE}Saindo...{colors.RESET}")
                break
            else:
                print(f"{colors.RED}Opção inválida.{colors.RESET}")
                time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{colors.RED}Encerrando...{colors.RESET}")


if __name__ == "__main__":
    mostrar_header()
    yt_dlp_path, ffmpeg_path = configurar_dependencias()
    menu(yt_dlp_path, ffmpeg_path)

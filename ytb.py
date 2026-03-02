import os
import subprocess
import sys
import time
import platform

CYAN = "\033[96m"
RESET = "\033[0m"
GREEN = "\033[92m"
RED = "\033[91m"

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_header():
    limpar_tela()
    print(f"""{CYAN}
██╗ ██████╗██╗   ██╗████████╗██████╗ 
██║██╔════╝╚██╗ ██╔╝╚══██╔══╝██╔══██╗
██║██║      ╚████╔╝    ██║   ██████╔╝
██║██║       ╚██╔╝     ██║   ██╔══██╗
██║╚██████╗   ██║      ██║   ██████╔╝
╚═╝ ╚═════╝   ╚═╝      ╚═╝   ╚═════╝                                                                                                  
{RESET}""")
    print(f"{CYAN}✦ ICYRIP | v1.4 ✦ By Icey — Powered by yt-dlp{RESET}")
    print(f"{CYAN}═══════════════════════════════════════════════{RESET}")

def configurar_pasta():
    sistema = platform.system()
    if sistema == "Windows":
        pasta_padrao = os.path.expanduser("~\\Downloads\\Musicas")
    else:  
        pasta_padrao = os.path.expanduser("~/Músicas")

    print(f"{CYAN}Pasta de destino:{RESET} ", end="")
    save_path = input(f"{CYAN}Digite o caminho completo da pasta ou pressione Enter para usar o padrão ({pasta_padrao}): {RESET}")
    if not save_path:
        save_path = pasta_padrao

    if not os.path.isdir(save_path):
        os.makedirs(save_path, exist_ok=True)
        print(f"{GREEN}Pasta criada em: {save_path}{RESET}")
    else:
        print(f"{GREEN}Pasta configurada: {save_path}{RESET}")
    return save_path

def configurar_dependencias():
    sistema = platform.system()
    print(f"{CYAN}Configuração das dependências:{RESET}")

    yt_dlp_path = input(f"{CYAN}Digite o caminho do yt-dlp (ou Enter se estiver no PATH): {RESET}").strip()
    if not yt_dlp_path:
        yt_dlp_path = "yt-dlp.exe" if sistema == "Windows" else "yt-dlp"

    ffmpeg_path = input(f"{CYAN}Digite o caminho do ffmpeg (ou Enter se estiver no PATH): {RESET}").strip()
    if not ffmpeg_path:
        ffmpeg_path = "ffmpeg.exe" if sistema == "Windows" else "ffmpeg"

    
    try:
        subprocess.run([yt_dlp_path, "--version"], check=True, stdout=subprocess.DEVNULL)
    except:
        print(f"{RED}yt-dlp não encontrado! Instale ou configure o caminho correto.{RESET}")
        sys.exit(1)

    try:
        subprocess.run([ffmpeg_path, "-version"], check=True, stdout=subprocess.DEVNULL)
    except:
        print(f"{RED}ffmpeg não encontrado! Instale ou configure o caminho correto.{RESET}")
        sys.exit(1)

    return yt_dlp_path, ffmpeg_path

def baixar_playlist(save_path, yt_dlp_path, ffmpeg_path):
    playlist_url = input(f"{CYAN}Digite o link da playlist do YouTube: {RESET}")
    comando = [yt_dlp_path, "--extract-audio", "--audio-format", "mp3",
               "--ffmpeg-location", ffmpeg_path,
               "-o", os.path.join(save_path, "%(title)s.%(ext)s"),
               playlist_url]
    print(f"{CYAN}Baixando a playlist...{RESET}")
    subprocess.run(comando)
    print(f"{GREEN}Playlist baixada com sucesso! Salva em: {save_path}{RESET}")
    input(f"{CYAN}Pressione Enter para continuar...{RESET}")

def baixar_musica(save_path, yt_dlp_path, ffmpeg_path):
    musica_url = input(f"{CYAN}Digite a URL da música que deseja baixar: {RESET}")
    comando = [yt_dlp_path, "--extract-audio", "--audio-format", "mp3",
               "--ffmpeg-location", ffmpeg_path,
               "-o", os.path.join(save_path, "%(title)s.%(ext)s"),
               musica_url]
    print(f"{CYAN}Baixando a música...{RESET}")
    subprocess.run(comando)
    print(f"{GREEN}Música baixada com sucesso! Salva em: {save_path}{RESET}")
    input(f"{CYAN}Pressione Enter para continuar...{RESET}")

def converter_para_mp3(save_path, ffmpeg_path):
    arquivo = input(f"{CYAN}Digite o nome do arquivo (com extensão) para converter para MP3: {RESET}")
    entrada = os.path.join(save_path, arquivo)
    saida = os.path.join(save_path, arquivo.rsplit(".", 1)[0] + ".mp3")

    comando = [ffmpeg_path, "-i", entrada, saida]
    print(f"{CYAN}Convertendo para MP3...{RESET}")
    subprocess.run(comando)
    print(f"{GREEN}Conversão concluída! Salvo em: {save_path}{RESET}")
    input(f"{CYAN}Pressione Enter para continuar...{RESET}")

def exibir_opcoes():
    print(f"{CYAN}═══════════════════════════════════════════════{RESET}")
    print(f"{CYAN}[1] Baixar Playlist{RESET}")
    print(f"{CYAN}[2] Baixar Música{RESET}")
    print(f"{CYAN}[3] Converter para MP3{RESET}")
    print(f"{CYAN}[0] Sair{RESET}")
    print(f"{CYAN}═══════════════════════════════════════════════{RESET}")

def menu():
    save_path = configurar_pasta()
    while True:
        mostrar_header()
        exibir_opcoes()
        opcao = input(f"{CYAN}Selecione a opção: {RESET}")
        if opcao == "1":
            baixar_playlist(save_path, yt_dlp_path, ffmpeg_path)
        elif opcao == "2":
            baixar_musica(save_path, yt_dlp_path, ffmpeg_path)
        elif opcao == "3":
            converter_para_mp3(save_path, ffmpeg_path)
        elif opcao == "0":
            print(f"{CYAN}Saindo...{RESET}")
            break
        else:
            print(f"{RED}Opção inválida. Tente novamente.{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    mostrar_header()
    yt_dlp_path, ffmpeg_path = configurar_dependencias()
    menu()


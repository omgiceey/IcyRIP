# ICYRIP v2.1

```
░▒▓█▓▒░░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░░▒▓█▓▒░▒▓███████▓▒░
░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░
░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░
░▒▓█▓▒░▒▓█▓▒░       ░▒▓██████▓▒░░▒▓███████▓▒░░▒▓█▓▒░▒▓███████▓▒░
░▒▓█▓▒░▒▓█▓▒░         ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░
░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░  ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░
░▒▓█▓▒░░▒▓██████▓▒░   ░▒▓█▓▒░   ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░
```

> Ferramenta CLI em Python para baixar áudio e vídeo do **YouTube**, **SoundCloud** e **Spotify** usando `yt-dlp` + `ffmpeg`. Interface colorida, animada e totalmente no terminal.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows%20%7C%20Termux-lightgrey?style=flat-square)

---

## Pré-requisitos

- Python 3.10+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [ffmpeg](https://ffmpeg.org/) + ffprobe

```bash
yt-dlp --version
ffmpeg -version
```

### Linux / macOS

```bash
sudo apt install ffmpeg        # Debian/Ubuntu
brew install ffmpeg            # macOS

pipx install yt-dlp            # recomendado
```

### Windows

```powershell
winget install yt-dlp ffmpeg
```

---

## Instalação

### Via Git (recomendado — permite atualização automática)

```bash
git clone https://github.com/omgiceey/IcyRIP.git
cd IcyRIP
pip install -r requirements.txt
python main.py
```

### Via ZIP

1. Baixe o ZIP em [github.com/omgiceey/IcyRIP/releases/latest](https://github.com/omgiceey/IcyRIP/releases/latest)
2. Extraia e entre na pasta
3. `pip install -r requirements.txt`
4. `python main.py`

> **Atenção:** quem instala por ZIP não pode usar a atualização automática do HUB. Para atualizar, baixe o ZIP da nova versão e substitua os arquivos.

---

## Como usar

```bash
python main.py      # HUB principal (recomendado)
python ytb.py       # YouTube direto
python sound.py     # SoundCloud direto
python spotify.py   # Spotify direto
```

---

## Funcionalidades

### 🎵 YouTube (ICYTB)

| Opção | Descrição |
|-------|-----------|
| Baixar Música | Áudio de qualquer URL do YouTube |
| Baixar Playlist | Todas as faixas com spinner de busca e aviso de tamanho |
| Baixar Álbum | Playlist salva em subpasta com nome do álbum |
| Baixar Vídeo | MP4/MKV/WebM com seleção de qualidade (melhor/1080p/720p/480p) |
| Baixar Clipe | Trecho por tempo (áudio ou vídeo) |
| Converter | Converte arquivo local para qualquer formato de áudio |

### 🔊 SoundCloud (ICYSOUND)

| Opção | Descrição |
|-------|-----------|
| Baixar Música | Faixa individual com validação de URL |
| Baixar Playlist / Álbum | Com spinner de busca e aviso de tamanho |
| Baixar Clipe | Trecho por tempo |
| Converter | Converte arquivo local para qualquer formato de áudio |

### 🟢 Spotify (ICYSPOT)

| Opção | Descrição |
|-------|-----------|
| Baixar Música | Faixa individual (`open.spotify.com/track/...`) |
| Baixar Playlist | Todas as faixas (`open.spotify.com/playlist/...`) |
| Baixar Álbum | Álbum em subpasta (`open.spotify.com/album/...`) |
| Baixar Clipe | Trecho por tempo |
| Converter | Converte arquivo local para qualquer formato de áudio |

> **Como o Spotify funciona:** o yt-dlp resolve URLs do Spotify buscando as faixas correspondentes no **YouTube Music**. Não é feito download direto dos servidores do Spotify — o áudio vem do YouTube. Por isso a qualidade e disponibilidade dependem do que estiver no YouTube Music.
>
> Para melhores resultados, mantenha o yt-dlp sempre atualizado (`yt-dlp -U` no HUB → Dependências).

### Formatos suportados

- **Áudio:** MP3, WAV, FLAC, OGG, OPUS, AAC, M4A
- **Vídeo:** MP4, MKV, WebM

---

## Interface

- **Banner animado** — aparece linha por linha com gradiente de cores ao entrar em cada módulo
- **Menu responsivo** — se ajusta automaticamente à largura do terminal (mín. 52, máx. 90 cols), com redesenho ao redimensionar a janela
- **Barra de download** — gradiente verde → amarelo → vermelho por porcentagem, com velocidade e ETA
- **Barra de conversão ffmpeg** — azul → ciano com tempo atual / duração total e bitrate
- **Spinner animado** — ao buscar metadados de playlists e durante conversões
- **Prompt estilizado** — inputs com moldura `╭─ label / ╰▶`
- **Resumo de playlist** — ao final mostra `✔ X concluídos · ✗ Y erros · ⏱ tempo total`
- **Histórico de downloads** — últimos 50 downloads com timestamp, módulo e nome
- **Fila persistente** — adicione URLs à fila e processe depois
- **Notificações nativas** — aviso ao concluir downloads (Linux/macOS/Windows)
- **Verificação de update** — checa nova versão em background ao iniciar; HUB → `[6]` mostra a versão disponível e atualiza via `git pull` (requer instalação por Git)

---

## Temas e Presets

O HUB inclui **19 presets de cores** com preview visual antes de aplicar:

| Preset | Descrição |
|--------|-----------|
| default | Ciano + Laranja |
| cyberpunk | Magenta + Ciano neon |
| dracula | Roxo + Rosa |
| monokai | Verde + Rosa |
| ocean | Azul profundo + Verde-água |
| forest | Verde escuro + Verde claro |
| rose | Rosa claro + Rosa escuro |
| midnight | Violeta + Azul elétrico |
| aurora | Ciano brilhante + Verde neon |
| candy | Rosa chiclete + Amarelo |
| blood | Vermelho intenso |
| matrix | Verde terminal |
| gold | Dourado + Âmbar |
| synthwave | Roxo neon + Laranja retrowave |
| arctic | Azul gelo + Ciano pálido |
| lava | Laranja queimado + Amarelo incandescente |
| sakura | Rosa suave + Lilás |
| slate | Cinza azulado + Teal |
| toxic | Verde limão + Amarelo ácido |

Além dos presets, é possível customizar cada role de cor individualmente (HEX livre) e configurar o gradiente do banner ASCII por módulo (Hub, YouTube, SoundCloud, Spotify).

---

## Configuração

O arquivo de configuração fica em `~/.config/icyrip/config.json`.

```json
{
  "language": "pt",
  "preset": "default",
  "playlist_warning_threshold": 50,
  "verbose": false,
  "yt_dlp_path": null,
  "ffmpeg_path": null,
  "cookies_browser": null,
  "restrict_filenames": false,
  "notifications": true,
  "use_archive": true,
  "colors": {},
  "ascii_style": "follow_theme",
  "ascii_colors": {}
}
```

Pelo **HUB → Configurações** é possível:
- Mudar idioma (pt-BR / en)
- Aplicar preset de cores com preview
- Customizar cor individual por role (HEX livre)
- Customizar gradiente do banner ASCII por módulo
- Ajustar limite de aviso de playlist
- Ativar/desativar verbose
- Configurar cookies do browser
- Ativar restrição de nomes de arquivo
- Gerenciar perfis de download
- Ver estatísticas e histórico
- Exportar / importar / resetar configuração

---

## Estrutura do projeto

```
icyrip/
├── main.py          HUB principal, menus, temas, configurações
├── ytb.py           Módulo YouTube
├── sound.py         Módulo SoundCloud
├── spotify.py       Módulo Spotify
├── requirements.txt
├── LICENSE
├── core/
│   ├── colors.py    Sistema de cores, presets, gradientes
│   ├── config.py    Leitura/escrita de configuração
│   ├── downloader.py Lógica de download, progresso, conversão
│   ├── i18n.py      Internacionalização (pt-BR / en)
│   └── utils.py     Spinner, animações, histórico, execução de comandos
└── README.md
```

---

## Termux (Android)

O ICYRIP roda no Termux sem nenhuma modificação.

**1.** Baixe o Termux pelo [F-Droid](https://f-droid.org/packages/com.termux) — a versão da Play Store está desatualizada.

**2.** Instale as dependências:

```bash
pkg update && pkg upgrade
pkg install python ffmpeg git
pip install yt-dlp
```

**3.** Clone e rode:

```bash
git clone https://github.com/omgiceey/IcyRIP.git
cd IcyRIP
python main.py
```

**Dicas:**
- Rode `termux-setup-storage` uma vez para acessar o armazenamento externo
- Se o ffmpeg não for encontrado, informe o caminho no HUB → Dependências: `/data/data/com.termux/files/usr/bin/ffmpeg`

---

## Problemas comuns

| Problema | Solução |
|----------|---------|
| `yt-dlp não encontrado` | Configure o caminho no HUB → Dependências |
| `ffmpeg não encontrado` | Instale via apt/brew/winget ou configure o caminho |
| Erro 403 / bloqueado | Atualize o yt-dlp: `pipx upgrade yt-dlp` |
| Vídeo bloqueado por idade | Configure cookies do browser no HUB → Dependências |
| Barra de progresso sem cor | Terminal não suporta truecolor — defina `COLORTERM=truecolor` |
| Menu desalinhado | Use um terminal com suporte a Unicode e fonte monospace |
| Box não redimensiona | Redimensione a janela e pressione Enter |

---

Projeto desenvolvido com apoio da IA. Tmj. 🎵

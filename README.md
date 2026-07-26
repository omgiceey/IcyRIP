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
- [Git](https://git-scm.com/) *(opcional, necessário para atualização automática)*

---

## Instalando as dependências

### Python

Baixe em [python.org/downloads](https://www.python.org/downloads/) e instale normalmente.  
No Linux/macOS geralmente já vem instalado. Verifique com:

```bash
python3 --version
```

### Git

O Git é necessário para clonar o repositório e usar a atualização automática do HUB.

**Linux (Debian/Ubuntu):**
```bash
sudo apt install git
```

**macOS:**
```bash
brew install git
```

**Windows:**  
Baixe em [git-scm.com/download/win](https://git-scm.com/download/win) e instale.  
Ou via winget:
```powershell
winget install Git.Git
```

Verifique:
```bash
git --version
```

### yt-dlp

**Linux/macOS (recomendado):**
```bash
pipx install yt-dlp
```

Ou via pip:
```bash
pip install yt-dlp
```

**Windows:**
```powershell
winget install yt-dlp
```

Ou baixe o executável direto em [github.com/yt-dlp/yt-dlp/releases/latest](https://github.com/yt-dlp/yt-dlp/releases/latest) (`yt-dlp.exe`).

Verifique:
```bash
yt-dlp --version
```

### ffmpeg

O ffmpeg é obrigatório para converter e processar o áudio/vídeo.

**Linux (Debian/Ubuntu):**
```bash
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
```powershell
winget install ffmpeg
```

Ou baixe os binários em [ffmpeg.org/download.html](https://ffmpeg.org/download.html) (builds para Windows em [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/)).

Verifique:
```bash
ffmpeg -version
```

> **Não consegue instalar globalmente?** Veja a seção [Pasta tools/](#pasta-tools) abaixo — você pode colocar os executáveis direto na pasta do ICYRIP.

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

## Pasta tools/

A pasta `tools/` é a forma **recomendada** de fornecer o `yt-dlp` e o `ffmpeg` para o ICYRIP, especialmente se você não tem permissão para instalar programas globalmente no sistema (sem admin, Termux, ambiente restrito, etc.).

> **Por que é recomendado?** Colocando os executáveis em `tools/`, o ICYRIP os detecta automaticamente sem precisar configurar nada. Não depende do PATH do sistema, não quebra com atualizações do SO, e funciona igual em qualquer ambiente.

Crie a pasta `tools/` dentro da pasta do ICYRIP e coloque os executáveis lá:

```
IcyRIP/
└── tools/
    ├── yt-dlp          (ou yt-dlp.exe no Windows)
    └── ffmpeg          (ou ffmpeg.exe no Windows)
```

Depois vá em **HUB → `[5]` Dependências → `[7]` Pasta tools/** — o ICYRIP vai escanear a pasta automaticamente e salvar os caminhos na configuração.

**Como baixar os executáveis:**

- **yt-dlp:** [github.com/yt-dlp/yt-dlp/releases/latest](https://github.com/yt-dlp/yt-dlp/releases/latest) → baixe `yt-dlp` (Linux/macOS) ou `yt-dlp.exe` (Windows)
- **ffmpeg:** [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/) (Windows) ou [ffmpeg.org/download.html](https://ffmpeg.org/download.html)

No Linux/macOS, dê permissão de execução após baixar:
```bash
chmod +x tools/yt-dlp tools/ffmpeg
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

## HUB

| Opção | Descrição |
|-------|-----------|
| `[1]` YouTube | Abre o módulo YouTube |
| `[2]` SoundCloud | Abre o módulo SoundCloud |
| `[3]` Spotify | Abre o módulo Spotify |
| `[4]` Configurações | Idioma, temas, cores, fila, perfis, histórico, estatísticas |
| `[5]` Dependências | Caminhos de yt-dlp/ffmpeg, cookies, pasta tools/, atualizar yt-dlp |
| `[6]` Verificar atualização | Checa nova versão e atualiza via `git pull` (requer Git) |

> Quem instalou por ZIP não pode usar a atualização automática do `[6]`. Baixe o ZIP da nova versão em [releases](https://github.com/omgiceey/IcyRIP/releases/latest) e substitua os arquivos.

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
├── tools/           (opcional) coloque yt-dlp e ffmpeg aqui se não instalou globalmente
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
- A atualização automática (`[6]` no HUB) funciona normalmente no Termux se instalou via `git clone`
- Notificações nativas não funcionam no Termux — o aviso de conclusão de download não será exibido

---

## Problemas comuns

| Problema | Solução |
|----------|---------|
| `yt-dlp não encontrado` | Instale com `pip install yt-dlp` ou coloque o executável em `tools/` |
| `ffmpeg não encontrado` | Instale via apt/brew/winget ou coloque o executável em `tools/` |
| Configurei o caminho mas não funciona | Certifique-se de apontar para o **executável**, não para a pasta. Ex: `/usr/bin/ffmpeg` |
| Erro 403 / bloqueado | Atualize o yt-dlp: `pipx upgrade yt-dlp` ou HUB → Dependências → `[4]` |
| Vídeo bloqueado por idade | Configure cookies do browser no HUB → Dependências |
| Faixa do Spotify não encontrada | O yt-dlp busca no YouTube Music — se não achar, a faixa pode não estar disponível lá. Tente atualizar o yt-dlp |
| Barra de progresso sem cor | Terminal não suporta truecolor — defina `COLORTERM=truecolor` |
| Menu desalinhado | Use um terminal com suporte a Unicode e fonte monospace |
| Box não redimensiona | Redimensione a janela e pressione Enter |

---

Projeto desenvolvido com apoio da IA. Tmj. 🎵

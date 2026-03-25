# 🎵 ICYRIP

```text
 ________  ______   __  __   ______     ________  ______    
/_______/\/_____/\ /_/\/_/\ /_____/\   /_______/\/_____/\   
\__.::._\/\:::__\/ \ \ \ \ \\:::_ \ \  \__.::._\/\:::_ \ \  
   \::\ \  \:\ \  __\:\_\ \ \\:(_) ) )_   \::\ \  \:(_) \ \ 
   _\::\ \__\:\ \/_/\\::::_\/ \: __ `\ \  _\::\ \__\: ___\/ 
  /__\::\__/\\:\_\ \ \ \::\ \  \ \ `\ \ \/__\::\__/\\ \ \   
  \________\/ \_____\/  \__\/   \_\/ \_\/\________\/ \_\/   
```

## 📝 O que é

**ICYRIP** é uma ferramenta CLI em Python para baixar áudio do **YouTube** e **SoundCloud** usando `yt-dlp` + `ffmpeg`, salvando tudo em **MP3**.

A ideia é simples: abrir → colar link → baixar → pronto.

---

## ⚡ Funcionalidades

- Baixa **playlists** do YouTube
- Baixa **música individual**
- Converte automaticamente para **MP3**
- Permite escolher a **pasta de destino**
- Barra de progresso **limpa e minimalista**

---

## 🛠 Pré-requisitos (IMPORTANTE)

Você precisa de:

- **Python 3.10+**
- **yt-dlp**
- **ffmpeg**

### ✅ Teste rápido (execute antes de rodar)

```bash
ffmpeg -version
yt-dlp --version
```

Se esses comandos não funcionarem, a ferramenta não vai conseguir baixar ou converter.

> **⚠️ Aviso**: `ffmpeg` NÃO instala via pip. Instale via apt, ou baixe o binário direto.

---

## � Como usar

O método recomendado é abrir o HUB (menu principal) que unifica YouTube, SoundCloud e configurações:

```bash
python3 main.py   # Abre o HUB (recomendado)
```

Ainda é possível executar os módulos diretamente se preferir:

```bash
python3 ytb.py    # YouTube (modo standalone)
python3 sound.py  # SoundCloud (modo standalone)
```

No Windows, use `python` em vez de `python3`.

### Menu do YouTube

O menu do módulo YouTube (`ytb.py`) possui as opções abaixo:

```
[1] Baixar Playlist
[2] Baixar Música
[3] Converter para MP3
[4] Baixar Álbum
[0] Sair
```

Observações rápidas sobre o comportamento:
- Formatos suportados para extração: MP3 e WAV (o script pergunta antes de baixar/converter).
- Há opção para embutir a capa (thumbnail) e adicionar metadados.
- O script pode estimar tamanho/duração de playlists grandes e pedirá confirmação antes de prosseguir.

---

## Estrutura do Projeto

```
ICYRIP/
 ├── downloads/      # músicas baixadas (criadas conforme uso)
 ├── playlists/      # playlists aqui (quando aplicável)
 ├── main.py         # HUB / menu principal (recomendado)
 ├── ytb.py          # módulo YouTube (também executável)
 ├── sound.py        # módulo SoundCloud (também executável)
 ├── core/           # módulos auxiliares (config, cores, etc.)
 └── README.md
```

Os scripts criam pastas automaticamente quando necessário. O HUB (`main.py`) também permite:

- Verificar / configurar caminhos de `yt-dlp` e `ffmpeg` e salvá-los em `config.json`;
- Ajustar idioma e tema de cores;
- Ajustar o limite que dispara aviso para playlists grandes.

### Arquivo de configuração

O programa grava um `config.json` no diretório de trabalho com as seguintes chaves (padrões):

- `language`: `pt` (ou `en`)
- `theme`: `default` (ou `alternative`)
- `playlist_warning_threshold`: 50
- `yt_dlp_path`: caminho para o executável `yt-dlp` (opcional)
- `ffmpeg_path`: caminho para o executável `ffmpeg` (opcional)

Você pode editar essas opções pelo HUB em "Verificar/Configurar Dependências" ou alterando `config.json` manualmente.

```

Segue abaixo alternativas práticas para instalar o `yt-dlp` e o `ffmpeg` por plataforma.

### Instalando yt-dlp e ffmpeg (alternativas rápidas)

Linux (Debian/Ubuntu):

```bash
# ffmpeg via apt
sudo apt update && sudo apt install ffmpeg

# yt-dlp via pipx (recomendado)
pipx install yt-dlp


```

Linux (baixar binários):

```bash
# Baixe o binário do yt-dlp e mova para ~/.local/bin
curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o ~/.local/bin/yt-dlp
chmod +x ~/.local/bin/yt-dlp

# Baixe FFmpeg builds (ex.: https://johnvansickle.com/ffmpeg/ ou site oficial) e extraia

```

Se preferir, baixe os binários diretamente das releases oficiais:

- yt-dlp: https://github.com/yt-dlp/yt-dlp/releases
- FFmpeg: https://ffmpeg.org/download.html

Observação: em ambientes gerenciados (ex.: mensagem "externally-managed-environment" do pip), a atualização via `pip install --upgrade yt-dlp` pode falhar; nesses casos use `pipx`, um venv, ou o binário direto.

---

## 🪟 Windows (Compatibilidade)

**ICYRIP funciona 100% no Windows.** Mas tome cuidado com:

- Use **PowerShell** ou **Windows Terminal** (CMD antigo pode ter problemas com cores ANSI)
- Caminho do `yt-dlp` e `ffmpeg`: quando o script pedir, use:
  - `C:\caminho\para\yt-dlp.exe`
  - `C:\caminho\para\ffmpeg.exe`
- Se não estiverem no PATH, coloque na **mesma pasta** do script

### Instalando yt-dlp e ffmpeg no Windows

**Via winget**:

```powershell
winget install yt-dlp ffmpeg
```

**Ou baixe os binários**:
- [yt-dlp Releases](https://github.com/yt-dlp/yt-dlp/releases)
- [FFmpeg Downloads](https://ffmpeg.org/download.html)

---

## 🚀 Como usar

Execute um dos módulos:

```bash
python3 ytb.py    # YouTube
python3 sound.py  # SoundCloud
```

No Windows, use `python` em vez de `python3`.

### Menu do YouTube

```
[1] Baixar Playlist
[2] Baixar Música
[3] Converter para MP3
[0] Sair
```

---

## � Estrutura do Projeto

```
ICYRIP/
 ├── downloads/      # músicas baixadas
 ├── playlists/      # playlists aqui
 ├── ytb.py          # módulo YouTube
 ├── sound.py        # módulo SoundCloud
 └── README.md
```

Os scripts criam pastas automaticamente quando necessário.

---

## 🧯 Problemas Comuns

| Problema | Solução |
|----------|---------|
| `ffmpeg não encontrado` | Verifique se está no PATH ou informe o caminho no prompt |
| `yt-dlp não encontrado` | Atualize via `pipx`, binário ou `apt` |
| `Erro 403 / Blocked` | Atualize yt-dlp ou tente outro link |
| `Link inválido` | Verifique se a URL é válida e acessível |

---

## 💡 Dicas rápidas

- Use pastas com nomes simples
- Mantenha yt-dlp e ffmpeg atualizados
- Evite caracteres especiais no nome da pasta

## 📌 Nota

Esse projeto nasceu com apoio de IA, mas a estrutura, ajustes e testes finais foram feitos manualmente.

Se você usar e curtir, já valeu demais.
Tmj. 😄

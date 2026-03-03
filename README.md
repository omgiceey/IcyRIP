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

## 🖥 Instalação

### Opção 1: Git (Recomendado)

Clone e entre no diretório:

```bash
git clone https://github.com/omgiceey/IcyRIP.git
cd ICYRIP
```

### Opção 2: Download .zip

1. Baixe o `.zip` do repositório
2. Descompacte em uma pasta
3. Abra o terminal nessa pasta

Sem problema usar `.zip` — o script funciona normal!

Instale dependências Python (opcional):

```bash
pip install -r requirements.txt
```

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
 ├── logs/           # logs de erro
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

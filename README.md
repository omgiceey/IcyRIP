# 🎵 ICYRIP

**ICYRIP** é uma ferramenta de terminal feita em Python para baixar áudio do YouTube e SoundCloud e converter automaticamente para MP3.

Simples, direta e funcional:  
**colar link → baixar → converter → pronto.**

---

## ✨ Recursos

- Download de playlists do YouTube
- Download de músicas individuais
- Download de faixas e playlists do SoundCloud
- Conversão automática para MP3
- Escolha de pasta de destino
- Interface simples via terminal

---

## 📦 Requisitos

Antes de usar, instale:

- Python 3.10+
- yt-dlp
- FFmpeg

---

## 🖥 Instalação no Windows (passo a passo)

### 1) Instalar Python

Baixe em:  
https://www.python.org/downloads/

Durante a instalação, marque a opção **Add Python to PATH**.

### 2) Instalar yt-dlp

No CMD/PowerShell:

```bash
pip install -U yt-dlp
```

Teste:

```bash
yt-dlp --version
```

### 3) Instalar FFmpeg

Acesse:  
https://www.gyan.dev/ffmpeg/builds/

Baixe o arquivo **ffmpeg-release-essentials.zip** (latest release).

Extraia para, por exemplo:

```text
C:\Tools\ffmpeg\
```

Adicione ao PATH do Windows:

1. Abra **Variáveis de Ambiente**
2. Edite a variável **Path**
3. Adicione:

```text
C:\Tools\ffmpeg\bin
```

Teste:

```bash
ffmpeg -version
```

Se aparecer a versão, está funcionando.

---

## 🐧 Instalação no Linux (Debian/Ubuntu)

```bash
sudo apt update
sudo apt install yt-dlp ffmpeg python3 -y
```

---

## 📥 Baixando o projeto

```bash
git clone https://github.com/omgiceey/IcyRIP.git
cd IcyRIP
```

Ou, se preferir, baixe o projeto em ZIP no GitHub.

---

## 🚀 Como usar

### YouTube

```bash
python ytb.py
```

ou

```bash
python3 ytb.py
```

### SoundCloud

```bash
python sound.py
```

---

## 📂 Menu (YouTube)

```text
[1] Baixar Playlist
[2] Baixar Música
[3] Converter para MP3
[0] Sair
```

---

## ⚠️ Observações

Mantenha o yt-dlp atualizado:

```bash
pip install -U yt-dlp
```

Se o download finalizar mas não converter para MP3, verifique se o FFmpeg foi instalado e configurado corretamente no PATH.

---

## 📤 GitHub rápido (opcional)

Se você editou algo e quer subir para o repositório:

```bash
git add .
git commit -m "Atualiza projeto"
git push origin main
```

Se sua branch não for `main`, troque no último comando.

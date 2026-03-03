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

O **ICYRIP** é uma ferramenta de terminal feita em Python para baixar áudio do **YouTube** e do **SoundCloud** e salvar em **MP3**.
A ideia é ser simples: abrir, colar o link, baixar e pronto.

---

## ⚡ O que ele faz

- Baixa playlists do YouTube
- Baixa músicas individuais
- Converte arquivos para MP3
- Permite escolher a pasta de destino

---

## 🛠 Pré-requisitos

Você precisa ter:

- Python 3.12+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp/releases)
- [ffmpeg](https://ffmpeg.org/download.html)

### Windows
Use caminhos simples para os executáveis, por exemplo:

- `C:\Tools\yt-dlp.exe`
- `C:\Tools\ffmpeg\bin\ffmpeg.exe`

### Linux (Debian/Ubuntu)

```bash
sudo apt update && sudo apt install yt-dlp ffmpeg -y
```

---

## 🖥 Instalação

```bash
git clone https://github.com/omgiceey/IcyRIP.git
cd ICYRIP
```

Se precisar de dependências Python extras:

```bash
pip install -r requirements.txt
```

---

## 🚀 Como usar

No terminal, execute:

```bash
python ytb.py    # módulo YouTube
python sound.py  # módulo SoundCloud
```

No Linux, se necessário:

```bash
python3 ytb.py
python3 sound.py
```

Menu do YouTube:

```text
[1] Baixar Playlist
[2] Baixar Música
[3] Converter para MP3
[0] Sair
```

---

## 💡 Dicas rápidas

- Prefira pastas com nomes simples
- Mantenha `yt-dlp` e `ffmpeg` atualizados
- Use uma pasta para playlist e outra para downloads avulsos

---

## 📤 Como subir pro GitHub (sem complicação)

Se você alterou algo e quer enviar pro seu repositório:

```bash
git add .
git commit -m "Atualiza projeto"
git push origin main
```

Se sua branch não for `main`, troque no último comando:

```bash
git push origin NOME_DA_BRANCH
```

Se o GitHub pedir senha, use um **Personal Access Token**.

---

## 📌 Nota

Esse projeto nasceu com apoio de IA, mas os ajustes finais e testes foram feitos manualmente por mim.
Se você usar e curtir, já valeu demais. 😄

# 🎵 ICYRIP


 ________  ______   __  __   ______     ________  ______    
/_______/\/_____/\ /_/\/_/\ /_____/\   /_______/\/_____/\   
\__.::._\/\:::__\/ \ \ \ \ \\:::_ \ \  \__.::._\/\:::_ \ \  
   \::\ \  \:\ \  __\:\_\ \ \\:(_) ) )_   \::\ \  \:(_) \ \ 
   _\::\ \__\:\ \/_/\\::::_\/ \: __ `\ \  _\::\ \__\: ___\/ 
  /__\::\__/\\:\_\ \ \ \::\ \  \ \ `\ \ \/__\::\__/\\ \ \   
  \________\/ \_____\/  \__\/   \_\/ \_\/\________\/ \_\/   
                                                            


**ICYRIP** é um script de terminal em Python para baixar músicas e playlists do **YouTube** e **SoundCloud** e convertê-las para **MP3**.
Funciona em **Windows** e **Linux**, é rápido, simples e totalmente personalizável.

---

## ⚡ Funcionalidades principais

* Baixar playlists inteiras
* Baixar músicas individuais
* Converter arquivos de áudio para MP3
* Configurar pastas de download personalizadas

---

## 🛠 Pré-requisitos

* Python 3.12+
* [yt-dlp](https://github.com/yt-dlp/yt-dlp/releases)
* [ffmpeg](https://ffmpeg.org/download.html)

> 🔹 No Windows: coloque os executáveis em pastas simples, ex.:
> `C:\Tools\yt-dlp.exe` e `C:\Tools\ffmpeg\bin\ffmpeg.exe`

> 🔹 No Linux: instale via terminal:
>
> ```bash
> sudo apt update && sudo apt install yt-dlp ffmpeg -y
> ```

---

## 🖥 Instalação

1. Clone ou baixe o repositório:

```bash
git clone https://github.com/SEU-USUARIO/ICYRIP.git
```

2. Entre na pasta do projeto:

```bash
cd ICYRIP
```

3. Instale dependências Python (se necessário):

```bash
pip install -r requirements.txt
```

---

## 🚀 Uso

Execute o script no terminal:

```bash
python main.py   # Windows
python3 main.py  # Linux
```

Siga o menu interativo para baixar ou converter suas músicas:

```
[1] Baixar Playlist
[2] Baixar Música
[3] Converter para MP3
[0] Sair
```

## 💡 Dicas

* Use nomes simples para pastas (sem espaços complicados)
* Mantenha `yt-dlp` e `ffmpeg` atualizados
* Separe pastas diferentes para playlists e músicas individuais

---

## 📌 Nota

O projeto foi criado com ajuda de IA, mas todos os ajustes foram feitos por mim.
Espero de coração que gostem — já estava na hora de lançar aqui no GitHub! 😄

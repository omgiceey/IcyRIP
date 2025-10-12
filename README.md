ICYRIP 🎵

ICYRIP é uma ferramenta de terminal para baixar músicas e playlists do YouTube e converter para MP3 usando yt-dlp e ffmpeg. Simples, rápido e personalizável.

⚡ Funcionalidades

Baixar playlists inteiras do YouTube/SoundCloud

Baixar músicas individuais

Converter arquivos de áudio para MP3

Configuração de pastas de download personalizadas

Suporte a Windows e Linux, detectando yt-dlp e ffmpeg automaticamente ou permitindo configuração manual

🛠 Pré-requisitos

Antes de usar o ICYTB/ICYSOUND, você precisa ter:

Python 3.12+ instalado no sistema

yt-dlp

ffmpeg

🔹 No Windows

Baixe o yt-dlp.exe:
👉 yt-dlp releases

Baixe o ffmpeg.exe:
👉 ffmpeg release essentials

Recomenda-se colocar ambos em pastas simples, ex:

C:\Tools\yt-dlp.exe
C:\Tools\ffmpeg\bin\ffmpeg.exe

🔹 No Linux (Kali/Ubuntu/Debian)

Instale diretamente pelos pacotes:

sudo apt update && sudo apt install yt-dlp ffmpeg -y


Ou, se preferir a versão mais recente do yt-dlp:

pip install -U yt-dlp


Os binários ficam em:

/usr/bin/yt-dlp
/usr/bin/ffmpeg

🚀 Instalação (igual para Windows e Linux)

Clone ou baixe o ICYTB/ICYSOUND na sua máquina.

Extraia o conteúdo em uma pasta de sua preferência.

Abra o PowerShell/Prompt (Windows) ou Terminal (Linux) na pasta do ICYTB/ICYSOUND.

Instale as dependências Python (se necessário):

pip install -r requirements.txt


Obs: Atualmente o ICYTB/ICYSOUND não precisa de bibliotecas externas além do Python.

🎛 Configuração

Ao executar o ICYTB/ICYSOUND pela primeira vez:

Ele perguntará onde salvar as músicas. Escolha qualquer pasta ou use o padrão.

Ele pedirá os caminhos para yt-dlp e ffmpeg.

Se os executáveis estiverem no PATH, basta pressionar Enter.

Caso contrário, digite o caminho completo:

Exemplo no Windows:
yt-dlp: C:\Tools\yt-dlp.exe
ffmpeg: C:\Tools\ffmpeg\bin\ffmpeg.exe

Exemplo no Linux:
yt-dlp: /usr/bin/yt-dlp
ffmpeg: /usr/bin/ffmpeg


O ICYRIP salva esses caminhos para futuras execuções.

🖥 Uso

Execute o script no terminal:

python main.py   # Windows
python3 main.py  # Linux


Menu de opções:

[1] Baixar Playlist
[2] Baixar Música
[3] Converter para MP3
[0] Sair


Selecione a opção desejada digitando o número correspondente.
Siga as instruções na tela.

⚠️ Observações

Sempre execute o script pelo terminal, não dê duplo clique no .py.

Certifique-se de que yt-dlp e ffmpeg têm permissão de execução.

Arquivos baixados e convertidos ficam na pasta configurada.

💡 Dicas

Use nomes simples para pastas e caminhos (sem espaços complicados).

Atualize o yt-dlp e ffmpeg regularmente para evitar erros.

Para organizar melhor as músicas, configure pastas diferentes para playlists e músicas individuais.

📌 Nota final

Eu tive a ideia do projeto e usei IA pra montar o código, já que ainda tô aprendendo Python. Fiz alguns ajustes por conta própria pra deixar do meu jeito.

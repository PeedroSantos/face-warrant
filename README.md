# Face-Warrant 🚨

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-brightgreen)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Face-Warrant** é um sistema simples e local de reconhecimento facial projetado para demonstrar como identificar pessoas em fotos, vídeos ou até em tempo real (via webcam). Imagine um "detector de procurados" de filme: você cadastra rostos conhecidos, marca alguns como "PROCURADO" e o sistema analisa novas imagens para alertar se encontrar alguém na lista. 

**Atenção importante:** Este é um projeto educacional e de demonstração. Ele **NÃO** deve ser usado com dados reais de pessoas sem autorização legal. Ele simula o conceito, mas não é um sistema profissional de segurança ou polícia. Use apenas para aprendizado!

## 📖 O que este projeto faz? (Explicação simples)

Pense no Face-Warrant como um "álbum de fotos inteligente":
- **Cadastra rostos:** Você adiciona fotos de pessoas (com nomes) e decide se elas são "procuradas" ou não.
- **Analisa imagens:** Envie uma foto ou vídeo, e o sistema desenha caixas ao redor dos rostos, diz quem é (se conhece) e avisa se é "PROCURADO" com um selo vermelho chamativo.
- **Tempo real:** Se o servidor tiver uma webcam, você pode ver detecções ao vivo.
- **Interface fácil:** Tudo roda em um site simples no seu navegador, sem complicações.

É perfeito para quem está aprendendo sobre Inteligência Artificial (IA), visão computacional ou programação web. Não precisa ser expert – basta seguir os passos!

## ✨ Funcionalidades principais

- **Cadastro de rostos:** Adicione fotos nítidas (frente do rosto) e marque como "PROCURADO".
- **Reconhecimento em imagens:** Detecta múltiplos rostos, mostra confiança (ex: 85% de certeza) e boxes coloridos.
- **Análise de vídeos:** Processa vídeos inteiros e conta quantas vezes cada pessoa aparece.
- **Webcam ao vivo:** Transmissão em tempo real do servidor (se disponível).
- **Lista de conhecidos:** Veja e edite rostos cadastrados facilmente.
- **Status do sistema:** Verifique se tudo está funcionando (CPU, memória, etc.).
- **Tema escuro e visual "Wanted":** Interface bonita e intuitiva, com animações suaves.

## 🛠️ Tecnologias usadas (para curiosos)

- **Backend:** Python com [FastAPI](https://fastapi.tiangolo.com/) (rápido e moderno).
- **IA para rostos:** 
  - [YOLO](https://github.com/ultralytics/yolov5) para detectar onde estão os rostos.
  - [DeepFace](https://github.com/serengil/deepface) para comparar e reconhecer.
- **Frontend:** HTML, CSS e JavaScript puro (sem frameworks pesados).
- **Outros:** Torch (para IA), FFmpeg (para vídeos, opcional).

Não se preocupe se não souber disso tudo – o foco é no uso, não no código!

## 🚀 Como instalar e rodar (passo a passo para iniciantes)

### Pré-requisitos
- **Computador com:** Windows, Mac ou Linux.
- **Python 3.10 ou superior:** Baixe em [python.org](https://www.python.org/downloads/). (Se não tiver, instale primeiro!)
- **Git:** Para baixar o projeto (baixe em [git-scm.com](https://git-scm.com/)).
- **Espaço em disco:** Pelo menos 2GB livres (modelos de IA ocupam espaço).
- **GPU (opcional):** Se tiver uma placa de vídeo NVIDIA, é mais rápido; senão, roda na CPU.

### Passos de instalação
1. **Baixe o projeto:**
   Abra o terminal (Prompt de Comando no Windows) e digite:
   ```
   git clone https://github.com/PeedroSantos/face-warrant.git
   cd face-warrant
   ```

2. **Crie um ambiente virtual (recomendado, para não bagunçar seu Python):**
   ```
   python -m venv .venv
   ```
   Ative-o:
   - **Windows:** `.venv\Scripts\activate`
   - **Mac/Linux:** `source .venv/bin/activate`

3. **Instale as dependências:**
   ```
   pip install -r requirements.txt
   ```
   (Isso baixa tudo automaticamente. Pode demorar 5-10 minutos na primeira vez.)

4. **Inicie o servidor:**
   ```
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```
   Você verá algo como "Uvicorn running on http://0.0.0.0:8000".

5. **Abra no navegador:**
   Vá para [http://localhost:8000](http://localhost:8000). Pronto! A interface aparece.

**Dica:** Se der erro no FFmpeg (para vídeos), instale em [ffmpeg.org](https://ffmpeg.org/download.html) e adicione ao PATH do sistema.

### Parando o servidor
Pressione `Ctrl + C` no terminal.

## 📱 Como usar (guia visual simples)

1. **Adicionar um rosto conhecido:**
   - Vá na seção "➕ Adicionar Rosto Conhecido".
   - Digite o nome (ex: "João Silva").
   - Marque "Marcar como PROCURADO" se quiser.
   - Escolha uma foto clara do rosto.
   - Clique "Adicionar ao Banco de Dados".
   - Veja a confirmação verde!

2. **Reconhecer uma imagem:**
   - Na seção "🖼️ Reconhecer Imagem", envie uma foto.
   - Clique "Reconhecer Rostos".
   - Resultado: Foto com boxes, nomes e alertas "PROCURADO" em vermelho.

3. **Analisar um vídeo:**
   - Envie um arquivo de vídeo na seção "🎬 Reconhecer Vídeo".
   - Aguarde o processamento (pode demorar).
   - Veja o resumo de detecções e assista ao vídeo anotado.

4. **Webcam ao vivo:**
   - Clique "Iniciar Webcam" (precisa de câmera no servidor).
   - Pare com "Parar Webcam".

5. **Gerenciar rostos:**
   - Na seção "👥 Rostos Conhecidos", atualize a lista.
   - Clique "Limpar Todos os Rostos" para resetar (cuidado!).

**Dicas para melhores resultados:**
- Use fotos nítidas e frontais para cadastrar.
- Adicione várias fotos da mesma pessoa para mais precisão.
- Iluminação boa ajuda a IA!
- Se o reconhecimento falhar, teste com menos rostos no banco.

## 🔌 API (para quem quer integrar com outros apps)

O backend é uma API REST simples. Use ferramentas como Postman ou curl. Exemplos:

- **Adicionar rosto:** `POST /api/add-known-face` (envie form-data: `name`, `file`, `wanted=true/false`).
- **Reconhecer imagem:** `POST /api/recognize-image` (envie `file`).
- **Lista de rostos:** `GET /api/known-faces`.
- **Limpar banco:** `POST /api/clear-database`.

Veja a [documentação automática do FastAPI](http://localhost:8000/docs) no navegador após rodar o servidor.

## ⚠️ Avisos de segurança e privacidade

- **Local apenas:** Rode só no seu computador. Não exponha na internet sem senha!
- **Dados sensíveis:** Fotos de rostos são salvas localmente (em `uploaded_files/` e `known_faces/`). Delete após usar.
- **Não para uso real:** Isso é demo. Para sistemas reais, use ferramentas profissionais com conformidade (ex: LGPD/GDPR).
- **Limitações:** Pode errar em ângulos ruins, baixa luz ou máscaras. Precisão ~80-95% em testes ideais.

## 🐛 Problemas comuns e soluções

| Problema | Solução |
|----------|---------|
| "No module named 'torch'" | Rode `pip install -r requirements.txt` novamente. |
| Webcam não inicia | Verifique se o servidor tem câmera; teste com `ls /dev/video*` (Linux). |
| Vídeo lento | Use CPU mais forte ou GPU; instale FFmpeg. |
| Erro de memória | Feche outros apps; reduza resolução de vídeos. |
| Interface não carrega | Verifique se o servidor roda em `localhost:8000`. |

## 👨‍💻 Autores

- **Diego Mendes** ([@Depowo](https://github.com/Depowo))
- **Davi Gomes** ([@falkz-cmd](https://github.com/falkz-cmd))
- **Luan Gonzaga Oliveira** ([@luanzz012](https://github.com/luanzz012))
- **Pedro Evangelista Santos** ([@PeedroSantos](https://github.com/PeedroSantos))
- **Pedro Henrique Fernandes Gonçalves** ([@pedrohfgg](https://github.com/pedrohfgg))
- **Murilo José Silva** ([@murilojs0](https://github.com/murilojs0))
- **Carlos Vinicius Luz Lima** ([@Carlos-fck](https://github.com/Carlos-fck))
- **Bruno Gaetano Rodovalho Lo Monaco** ([@brN146414](https://github.com/brN146414))
- **Richard Gazana** ([@AltRichard](https://github.com/AltRichard))
- **João Lucas Oliveira Ramos** ([@JaoLcs23](https://github.com/JaoLcs23))
- **Raul Fernandes Silva Melo** ([@T0tsuK4](https://github.com/T0tsuK4))
    
- Feito para um trabalho de reconhecimento facial (mandato de prisão simulado).

## 🙏 Agradecimentos

- [FastAPI](https://fastapi.tiangolo.com/) por ser incrível.
- [DeepFace](https://github.com/serengil/deepface) e [YOLO](https://github.com/ultralytics/yolov5) pela IA acessível.
- Professores e comunidade open-source!
- **Professor Maxwell Gomes** ([@maxwellsilva-boop](https://github.com/maxwellsilva-boop))

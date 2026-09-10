# Face-Warrant

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-brightgreen)](https://fastapi.tiangolo.com/)

Sistema local de reconhecimento facial que detecta e identifica pessoas em fotos,
vídeos e webcam. O usuário cadastra rostos conhecidos, pode marcar alguns como
"procurado", e o sistema analisa novas imagens e sinaliza correspondências.

> **Projeto educacional.** Foi feito para demonstrar detecção e reconhecimento
> facial em um trabalho acadêmico. **Não** é um produto de segurança ou
> vigilância e **não** deve ser usado com dados reais de pessoas sem
> consentimento e base legal (LGPD).

## Funcionalidades

- **Cadastro de rostos** com nome e flag opcional de "procurado".
- **Reconhecimento em imagem** — detecta múltiplos rostos, desenha as caixas e
  mostra o nível de confiança.
- **Análise de vídeo** — processa o arquivo e conta as aparições de cada pessoa.
- **Webcam ao vivo** — stream em tempo real quando há câmera no servidor.
- **Gerência do banco** de rostos conhecidos e **status do sistema** (CPU/memória).

## Stack

- **Backend:** Python + [FastAPI](https://fastapi.tiangolo.com/)
- **Detecção:** [YOLO](https://github.com/ultralytics/ultralytics) (modelo `faces.pt`)
- **Reconhecimento:** [DeepFace](https://github.com/serengil/deepface) (embeddings + distância de cosseno)
- **Frontend:** HTML, CSS e JavaScript sem framework
- **Vídeo:** OpenCV e FFmpeg (opcional, para re-encode compatível com navegador)

## Como rodar

Pré-requisitos: Python 3.10+, Git e ~2 GB de disco (os modelos ocupam espaço).
GPU NVIDIA é opcional — roda em CPU.

```bash
git clone https://github.com/PeedroSantos/face-warrant.git
cd face-warrant

python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Abra `http://localhost:8000`. A documentação interativa da API fica em
`http://localhost:8000/docs`.

## API

REST, sob o prefixo `/api`:

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/api/add-known-face` | Cadastra um rosto (`name`, `file`, `wanted`) |
| `POST` | `/api/recognize-image` | Reconhece rostos em uma imagem (`file`) |
| `POST` | `/api/recognize-video` | Processa um vídeo (`file`) |
| `GET`  | `/api/known-faces` | Lista os rostos cadastrados |
| `POST` | `/api/clear-database` | Limpa o banco de rostos |

## Privacidade e limitações

- Rode **localmente**; não exponha na internet sem autenticação.
- As imagens ficam em `uploaded_files/` e `known_faces/` — apague após o uso.
- A precisão cai com ângulos ruins, pouca luz ou oclusão. É uma demonstração,
  não um sistema de produção.

## Solução de problemas

| Problema | Solução |
|----------|---------|
| `No module named 'torch'` | Rode `pip install -r requirements.txt` de novo |
| Webcam não inicia | Confirme que há câmera no servidor |
| Vídeo lento | Use GPU ou uma CPU mais forte; instale o FFmpeg |
| Erro de memória | Feche outros apps; reduza a resolução do vídeo |

## Autores

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

Trabalho acadêmico de visão computacional, orientado pelo **Professor Maxwell
Gomes** ([@maxwellsilva-boop](https://github.com/maxwellsilva-boop)).

## Agradecimentos

[FastAPI](https://fastapi.tiangolo.com/), [DeepFace](https://github.com/serengil/deepface)
e [YOLO](https://github.com/ultralytics/ultralytics) pela base de IA acessível.

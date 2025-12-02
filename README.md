# Face-Warrant — Sistema de Reconhecimento Facial (Face-Warrant)

> Pequeno sistema local de reconhecimento facial com interface web e um banco de rostos conhecido (para uso em demonstração/estudo).

Este README é escrito para usuários iniciantes e também para desenvolvedores.

---

## O que faz o projeto

- Adicionar fotos de rostos conhecidos
- Marcar rostos como *PROCURADO* (destaque especial)
- Analisar imagens e vídeos e reconhecer rostos com boxes e rótulos
- Exibir transmissão da webcam do servidor com reconhecimento em tempo real (se houver câmera)

---

## Destaques das correções/ajustes recentes

As últimas mudanças incluíram:

- Corrigido visual de chips/status (o ícone do chip agora tem contraste para ficar legível)
- Removido o botão de header "Iniciar Análise" que não era necessário. (A navegação direta ainda está disponível na interface.)
- Corrigido o botão de marcação/desmarcação (toggle) — agora a ação envia dados corretamente e refresca a lista.
- Uploads: nomes de arquivos agora são sanitizados ao salvar em `uploaded_files/`.
- `/api/recognize-video` agora verifica se o arquivo pode ser aberto e processa menos frames para melhorar desempenho.

---

## Instalação (passo a passo)

1. Crie um diretório e entre nele

```powershell
git clone <repo-url> ; cd face-warrant
```

2. (Opcional, recomendado) Crie e ative um ambiente virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

3. Instale as dependências

```powershell
pip install -r requirements.txt
```

4. Inicie o servidor

```powershell
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

5. Abra: http://localhost:8000

---

## Como usar (passo a passo para leigos)

1. Abra a página no navegador.
2. Para adicionar rosto conhecido: selecione uma imagem frontal nítida, digite o nome e marque "Marcar como PROCURADO" se desejar.
3. Para verificar imagem ou vídeo: envie o arquivo e espere o processamento — verá a imagem/vídeo com boxes e rótulos.
4. Para marcar/desmarcar: acesse a lista de rostos, clique em "Marcar" (ou "Desmarcar"). O sistema atualiza o banco e o distintivo "PROCURADO" muda de acordo.

---

## Endpoints importantes (para desenvolvedores)

- GET `/` — Interface
- POST `/api/add-known-face` — FormData: `name`, `file`, `wanted` (true/false)
- POST `/api/recognize-image` — FormData: `file` — retorna `image` (base64) + `faces` list
- POST `/api/recognize-video` — FormData: `file` — retorna `video_url` e `recognized_faces`
- GET `/api/known-faces` — retorna array `{name, wanted}`
- POST `/api/set-wanted` — FormData: `name`, `wanted` — define a name as wanted or not
- POST `/api/clear-database` — limpa todos os rostos conhecidos

---

## Testes rápidos que você pode executar

1. Adicione 1 rosto usando o formulário de adicionar rosto.
2. Verifique se o rosto aparece na lista de rostos conhecidos, e teste marcar/desmarcar.
3. Faça o upload de uma imagem com a pessoa conhecida para ver se é reconhecida.
4. Faça o upload de um vídeo e verifique o resultado e o link de download.

---

## Avisos e privacidade

- Não exponha esse aplicativo publicamente sem autenticação e controle de acesso.
- Não use o sistema com dados/reconhecimento real sem autorização e cuidados legais.

---

Se quiser que eu implemente autenticação, locks para uploads maiores, ou mover processamento de vídeos para workers, posso ajudar com isso na próxima fase.
++ Begin Marker
# Face-Warrant — Sistema de Reconhecimento Facial (WWP)

Bem-vindo ao Face-Warrant — um projeto simples para demonstrar reconhecimento facial local com um front-end fácil de usar.

Este README explica de forma simples o que o projeto faz e como utilizá-lo, mesmo se você não for programador.

---

## O que é este projeto? 🤖

Face-Warrant é uma aplicação web local que permite:
- Adicionar fotos de pessoas ("rostos conhecidos") ao banco de dados;
- Marcar rostos como "PROCURADO" para destaque especial (útil para demonstrações); 
- Enviar imagens ou vídeos para reconhecimento e ver o resultado com caixas e rótulos no próprio navegador; 
- Usar uma câmera do servidor para detectar e reconhecer rostos em tempo real.

O projeto usa modelos de detecção (YOLO) e extração de características (DeepFace) para comparar rostos com um banco local.

---

## Requisitos mínimos

- Python 3.10+ (recomendado 3.11)
- Memória: mínimo 4GB (mais é melhor) — a execução com DeepFace/YOLO pode ser pesada
- Se você quiser aceleração por GPU (NVIDIA), instale os drivers e CUDA compatíveis com `torch`.
- `ffmpeg` pode ser necessário para certos processos de vídeo.

---

## Instalação (passo a passo)

1) Clone o repositório (ou copie os arquivos para uma pasta):

```powershell
git clone <repo-url>
cd face-warrant
```

2) Crie e ative um ambiente virtual (recomendado):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

3) Instale as dependências:

```powershell
pip install -r requirements.txt
```

4) (Opcional) Se você usar GPU, confirme que `torch` foi instalado corretamente com suporte a CUDA.

5) Inicie a aplicação:

```powershell
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

6) Abra no navegador: http://localhost:8000

---

## Uso (visualmente, para qualquer pessoa)

1. Ao abrir o site, você verá cartões com ações: Adicionar rosto conhecido, Reconhecer imagem, Reconhecer vídeo, e Iniciar webcam.
2. Para adicionar um rosto:
   - Selecione uma foto clara e frontal (frente do rosto) e digite o nome.
   - Marque a caixa "Marcar como PROCURADO" se quiser destacar esse rosto.
   - Clique em "Adicionar ao Banco de Dados" — se o sistema encontrar um rosto na imagem, ele será salvo localmente.
3. Para reconhecer em imagens:
   - Envie uma imagem e clique em "Reconhecer Rostos".
   - A aplicação retorna uma imagem anotada (com boxes), nomes, confiança e se a pessoa está marcada como "PROCURADO".
4. Para reconhecer em vídeo:
   - Envie um arquivo de vídeo; a aplicação irá processá-lo e retornar um link para visualização do vídeo anotado e uma lista das pessoas reconhecidas.
5. Webcam do servidor (se o servidor tiver câmera):
   - Verifique o status e inicie a webcam para obter um fluxo MJPEG com reconhecimento em tempo real.

---

## API (para desenvolvedores)

Principais rotas (HTTP):
- GET `/` — UI (pagina principal)
- POST `/api/add-known-face` — Adiciona rosto (FormData: `name`, `file`, `wanted`)
- POST `/api/recognize-image` — Reconhece rostos em imagem (FormData: `file`)
- POST `/api/recognize-video` — Processa vídeo (FormData: `file`) -> retorna link para vídeo anotado
- GET `/api/known-faces` — Lista rostos conhecidos
- POST `/api/set-wanted` — Marca/desmarca um nome como `wanted` (FormData: `name`, `wanted`)
- POST `/api/clear-database` — Limpa o banco de rostos
- GET `/api/video/{video_id}` — Serve o vídeo anotado, com suporte a Range Requests para streaming
- GET `/api/health` — Informações de saúde do serviço

---

## Notas importantes de segurança e privacidade ⚠️

- Este projeto não adiciona nenhum mecanismo de autenticação por padrão. Se você for usar em produção, adicione autenticação e autorização.
- Tenha cuidado com dados pessoais — imagens faciais são sensíveis. Evite usar rostos reais sem consentimento.
- Os arquivos enviados são salvos na pasta `uploaded_files` e o banco local em `known_faces/encodings.pkl`.
- Evite expor este serviço à Internet sem proteções adicionais.

---

## Dicas e resolução de problemas

- Se o app não iniciar ou informar `ModuleNotFoundError`, verifique a instalação com `pip install -r requirements.txt`.
- Se o YOLO/DeepFace demora para carregar, aguarde — modelos podem ser grandes.
- Se o vídeo não reproduzir no navegador, tente abrir o `video_static_url` em nova aba ou instalar codecs do sistema (ex: H.264).
- Para abrir câmera do servidor, o processo precisa de acesso físico à câmera ou dispositivo virtual no ambiente em execução.

---

## Contribuindo

Pequenas alterações de correção, melhorias na interface, ou adicionar autenticação são bem-vindas. Abra uma issue ou pull request.

---

## Licença

Coloque aqui a licença do seu projeto (MIT, Apache, etc.).

---

Se quiser, posso também gerar um pequeno arquivo `CONTRIBUTING.md` com passos para contribuir, ou adicionar instruções para rodar em Docker.

++ End Marker# Face-Warrant — Sistema de Reconhecimento de Procurados

Resumo das alterações que foram implementadas e próximos passos:

## O que foi revisado
- Consertei a função de detecção e reconhecimento para retornar o status `wanted` corretamente (boolean) e evitar entradas duplicadas.
- Adicionei suporte para marcar rostos como `PROCURADO` no banco de dados.
- Atualizei o front-end para:
  - Mostrar um tema escuro e visual de "WANTED" (Face-Warrant).
  - Adicionar uma opção ao cadastrar um rosto para marcá-lo como PROCURADO.
  - Exibir um distintivo "PROCURADO" nos rostos reconhecidos e na lista de rostos conhecidos.
  - Adicionar botão para marcar/desmarcar um rosto como PROCURADO no front-end.
- Corrigi algumas inconsistências na API / front-end (chaves de resposta e estrutura dos dados).
- Removi `known_faces` do workspace e adicionei ao `.gitignore`.

## Rotas principais
- `POST /api/add-known-face` - adiciona rosto ao banco; novo campo `wanted` (boolean)
- `GET /api/known-faces` - lista os rostos conhecidos com `{name, wanted}`
- `POST /api/set-wanted` - alterna o estado de procurado de um nome conhecido
- `POST /api/recognize-image` - retorna `faces`: lista com `{name, confidence, wanted, box}` e `image` (base64) com anotações
- `POST /api/recognize-video` - retorna `recognized_faces`: lista com `{name, count, wanted}`

## Remoção do known_faces
- `known_faces/` foi removido da árvore local e adicionado ao `.gitignore`.

## Como testar localmente
1. Configure um ambiente virtual e instale dependências: 

```powershell
python -m venv .venv; .\.venv\Scripts\Activate; pip install -r requirements.txt
```

2. Inicie a aplicação:

```powershell
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

3. Abra `http://localhost:8000` e teste as funcionalidades: enviar imagens, marcar como procurado, etc.
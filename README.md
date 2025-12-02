# Face-Warrant — Sistema de Reconhecimento de Procurados

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
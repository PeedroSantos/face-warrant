Aqui está o **README.md** atualizado, bonito, claro, didático e já com todos os autores do grupo listados corretamente.  
É só copiar e colar direto no repositório!

```markdown
# Face-Warrant

**Sistema de Reconhecimento Facial com Alerta de Procurados**  
Um projeto acadêmico que simula um “detector de mandados de prisão” usando visão computacional e inteligência artificial.

Você cadastra rostos conhecidos (com nome e opção “PROCURADO”), depois envia fotos, vídeos ou usa a webcam do servidor para que o sistema identifique automaticamente quem aparece e destaque em vermelho quem está marcado como procurado.

> **Atenção:** Este é um projeto **educacional/demonstrativo**. Não deve ser usado com dados reais de pessoas sem autorização legal adequada.

## O que o sistema faz (explicação simples)

- Cadastra fotos de pessoas e marca quem é “PROCURADO”
- Reconhece rostos em imagens e desenha caixas com nome + confiança
- Analisa vídeos inteiros e mostra quantas vezes cada pessoa apareceu
- Transmite webcam ao vivo (se o servidor tiver câmera)
- Interface web moderna e totalmente em português
- Tema escuro com destaque vermelho para “PROCURADO”

## Funcionalidades

- Cadastro rápido de rostos conhecidos  
- Reconhecimento em imagem única (com imagem anotada de volta)  
- Processamento de vídeos (com vídeo anotado + relatório)  
- Webcam em tempo real (MJPEG stream do servidor)  
- Lista de rostos conhecidos com botão para marcar/desmarcar como procurado  
- Limpar todo o banco com um clique  
- Painel de saúde do sistema (CPU, memória, quantidade de rostos, etc.)

## Tecnologias utilizadas

- **Backend** – Python + FastAPI
- **Detecção de rostos** – YOLOv8 (Ultralytics)
- **Reconhecimento facial** – DeepFace
- **Frontend** – HTML + CSS + JavaScript puro (sem frameworks)
- **Outros** – Torch, OpenCV, FFmpeg (para vídeos)

## Como instalar e rodar (passo a passo)

### Pré-requisitos
- Python 3.10 ou superior
- Git
- (Opcional) GPU NVIDIA para processamento mais rápido

### Instalação

```bash
git clone https://github.com/PeedroSantos/face-warrant.git
cd face-warrant

# Criar ambiente virtual (recomendado)
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### Executar

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Depois abra no navegador: http://localhost:8000

Pronto! A interface já estará funcionando.

## Como usar

1. **Adicionar rosto** → foto nítida + nome + (opcional) marcar como “PROCURADO”
2. **Testar com imagem** → envie qualquer foto e veja os rostos identificados
3. **Testar com vídeo** → envie um vídeo e receba um novo vídeo com caixas e alertas
4. **Webcam ao vivo** → clique em “Iniciar Webcam” (funciona se o servidor tiver câmera)

## Equipe – Autores do projeto

| Nome                                   | GitHub                                      |
|----------------------------------------|---------------------------------------------|
| Diego Mendes                           | https://github.com/Depowo                   |
| Davi Gomes                             | https://github.com/falkz-cmd                |
| Luan Gonzaga Oliveira                  | https://github.com/luanzz012                |
| Pedro Evangelista Santos               | https://github.com/PeedroSantos             |
| Pedro Henrique Fernandes Gonçalves     | https://github.com/pedrohfgg                |
| Murilo José Silva                      | https://github.com/murilojs0                |
| Carlos Vinicius Luz Lima               | https://github.com/Carlos-fck               |
| Bruno Gaetano Rodovalho Lo Monaco      | https://github.com/brN146414                |
| Richard Gazana                         | https://github.com/AltRichard               |
| João Lucas Oliveira Ramos              | https://github.com/JaoLcs23                 |
| Raul Fernandes Silva Melo              | https://github.com/T0tsuK4                  |

## Dúvidas ou problemas?

Abra uma **Issue** aqui no repositório que a gente responde o mais rápido possível.

Divirtam-se e bom estudo!
```

É só salvar como `README.md` na raiz do projeto que o GitHub já vai renderizar tudo bonitinho com a tabela de autores e tudo mais.

Qualquer outra coisa que precisar ajustar é só chamar! Boa entrega do trabalho!
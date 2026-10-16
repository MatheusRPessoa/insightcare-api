# InsightCare AI API

API para análise de atendimentos em saúde, construída com FastAPI, PostgreSQL, scikit-learn e Amazon Bedrock.

O projeto combina classificação local de intenção com análise generativa da transcrição para produzir resumo, sentimento, risco operacional, sinais detectados, evidências e ação recomendada.

## Funcionalidades

- Cadastro, listagem paginada, consulta e exclusão de atendimentos.
- Classificação de intenção com TF-IDF e regressão logística.
- Análise generativa com Amazon Bedrock, usando `amazon.nova-micro-v1:0` por padrão.
- Validação da resposta generativa e dos trechos usados como evidência.
- Persistência de uma análise por atendimento; uma nova análise substitui a anterior e marca o atendimento como `ANALYZED`.
- Endpoint de dashboard com totais e distribuições por status, risco, sentimento e intenção.
- Documentação interativa gerada pelo FastAPI.

## Tecnologias

| Camada | Tecnologias |
| --- | --- |
| API e validação | FastAPI, Pydantic e Uvicorn |
| Persistência | PostgreSQL 16, SQLAlchemy, Psycopg e Alembic |
| Classificação | scikit-learn, pandas e Joblib |
| IA generativa | Amazon Bedrock e Boto3 |
| Dados e artefatos de ML | Hugging Face Datasets e Hub |
| Testes | pytest e FastAPI TestClient |

## Execução local

Execute os comandos a partir da raiz do repositório. As instruções abaixo usam Bash, Python 3.12 e Docker Compose. O Compose inicia apenas o PostgreSQL; a API é executada no ambiente Python local.

### 1. Instalar as dependências

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 2. Configurar o ambiente

Crie um arquivo `.env` na raiz com o conteúdo abaixo. Se ele já existir, ajuste os valores necessários sem sobrescrever suas configurações.

```dotenv
DATABASE_URL=postgresql+psycopg://insightcare:insightcare_dev@localhost:5432/insightcare
AWS_PROFILE=insightcare
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.nova-micro-v1:0
```

Use o formato `CHAVE=valor`, sem anotações de tipo Python. O `.env.example` atual contém anotações nas linhas de AWS; utilize o bloco acima para essas variáveis.

| Variável | Descrição | Padrão no código |
| --- | --- | --- |
| `DATABASE_URL` | URL de conexão do SQLAlchemy | Obrigatória |
| `AWS_PROFILE` | Perfil local utilizado pelo Boto3 | `insightcare` |
| `AWS_REGION` | Região do cliente Bedrock | `us-east-1` |
| `BEDROCK_MODEL_ID` | Identificador do modelo generativo | `amazon.nova-micro-v1:0` |

O perfil AWS configurado precisa existir no ambiente e ter acesso ao modelo Bedrock escolhido. Ele só é necessário para as chamadas generativas; o CRUD e a classificação local não usam AWS. As credenciais ficam na configuração do perfil AWS, fora do repositório.

### 3. Iniciar o banco e aplicar as migrations

```bash
docker compose up -d postgres
docker compose ps
```

Quando o PostgreSQL estiver saudável (`healthy`), aplique as migrations:

```bash
python -m alembic upgrade head
```

As migrations criam as tabelas `interactions` e `interaction_analyses`. O banco usa a porta local `5432` e mantém os dados no volume `postgres_data`.

### 4. Preparar o classificador

Os endpoints de classificação e análise precisam do arquivo `ml/models/intent_classifier.joblib`.

Para gerar o modelo a partir do dataset configurado em `ml/download_dataset.py`:

```bash
python -m ml.download_dataset
python -m ml.train
```

O download requer acesso à internet e grava os splits em `ml/data/train.csv`, `validation.csv` e `test.csv`. O treinamento seleciona o parâmetro `C` pelo F1 macro de validação, reajusta o modelo com treino e validação e imprime os resultados no conjunto de teste antes de salvar o artefato.

Se o artefato de distribuição já estiver presente em `ml/huggingface/`, você também pode copiá-lo para o caminho usado pela API:

```bash
mkdir -p ml/models
cp ml/huggingface/intent_classifier.joblib ml/models/intent_classifier.joblib
```

Detalhes do modelo e de sua avaliação estão em [ml/huggingface/README.md](ml/huggingface/README.md). O classificador é carregado em cache; reinicie a API após substituir o arquivo.

### 5. Iniciar a API

```bash
python -m uvicorn app.main:app --reload
```

- API: <http://127.0.0.1:8000>
- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>
- OpenAPI: <http://127.0.0.1:8000/openapi.json>

O CORS permite as origens `http://localhost:5173` e `http://127.0.0.1:5173`, com os métodos `GET`, `POST`, `DELETE` e `OPTIONS`.

## Endpoints

Todos os endpoints abaixo usam o prefixo `/api/v1`.

| Método | Rota | Comportamento |
| --- | --- | --- |
| `GET` | `/health` | Retorna o status da API; não verifica banco ou AWS |
| `POST` | `/interactions` | Cria um atendimento com status `PENDING` |
| `GET` | `/interactions` | Lista atendimentos com `skip` e `limit` |
| `GET` | `/interactions/{id}` | Consulta um atendimento |
| `DELETE` | `/interactions/{id}` | Exclui o atendimento e sua análise vinculada |
| `POST` | `/interactions/{id}/classify` | Retorna intenção, confiança e modelo local |
| `POST` | `/interactions/{id}/analyze` | Executa ML e Bedrock, salva a análise e atualiza o status |
| `GET` | `/interactions/{id}/analysis` | Recupera a análise salva sem chamar os modelos |
| `GET` | `/dashboard/summary` | Retorna contagens e distribuições dos atendimentos |

A listagem usa `skip=0` e `limit=20` por padrão; `limit` aceita valores entre 1 e 100. A classificação isolada não salva uma análise nem altera o status do atendimento.

### Exemplo de uso

Crie um atendimento com canal `CHAT`, `PHONE` ou `EMAIL` e transcrição entre 10 e 20.000 caracteres:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/interactions \
  -H 'Content-Type: application/json' \
  -d '{"channel":"CHAT","transcript":"Quero cancelar meu plano porque o atendimento não resolveu meu problema."}'
```

Substitua o valor abaixo pelo `id` retornado:

```bash
INTERACTION_ID='cole-o-uuid-retornado-aqui'

curl -X POST "http://127.0.0.1:8000/api/v1/interactions/$INTERACTION_ID/classify"
curl -X POST "http://127.0.0.1:8000/api/v1/interactions/$INTERACTION_ID/analyze"
curl "http://127.0.0.1:8000/api/v1/interactions/$INTERACTION_ID/analysis"
curl http://127.0.0.1:8000/api/v1/dashboard/summary
```

A análise retorna `interaction_id`, `intent`, `confidence`, `classification_model`, `generative_model`, `summary`, `sentiment`, `risk_level`, `detected_signals`, `evidence` e `recommended_action`.

Sentimentos possíveis: `POSITIVE`, `NEUTRAL` e `NEGATIVE`. Níveis de risco operacional: `LOW`, `MEDIUM` e `HIGH`.

### Respostas de erro

| Status | Situação |
| --- | --- |
| `404` | Atendimento ou análise não encontrado |
| `422` | Dados da requisição inválidos |
| `502` | Resposta generativa inválida ou evidências incompatíveis com a transcrição |
| `503` | Modelo local ausente ou falha de acesso ao serviço generativo |

## Testes

Com o ambiente virtual ativo, o banco acessível, as migrations aplicadas e o classificador local disponível:

```bash
python -m pytest tests/ -v
```

Os testes usam o banco definido em `DATABASE_URL`, criam atendimentos e removem os registros criados ao final. Utilize um banco de desenvolvimento ou de testes. O teste de classificação usa o modelo local real; o teste de análise substitui as chamadas de ML e Bedrock por mocks e verifica a persistência e a atualização do status.

Para executar apenas o teste de saúde, sem conectar ao banco ou à AWS (a configuração `DATABASE_URL` ainda precisa existir):

```bash
python -m pytest tests/test_health.py -v
```

Há também scripts manuais para verificar as integrações externas:

```bash
python -m scripts.test_bedrock
python -m scripts.test_huggingface
```

O primeiro faz uma chamada real ao Bedrock. O segundo baixa o artefato do repositório configurado no script e executa exemplos de classificação; ele não instala o modelo no caminho usado pela API.

## Estrutura

```text
app/
  api/routes/       # Endpoints de saúde, atendimentos e dashboard
  core/             # Configuração e cliente AWS
  db/               # Base dos modelos e sessões do banco
  models/           # Modelos SQLAlchemy
  repositories/     # Consultas e operações de persistência
  schemas/          # Contratos de entrada e saída
  services/         # Regras de negócio e integração com ML/Bedrock
  main.py           # Aplicação FastAPI e CORS
migrations/         # Migrations Alembic
ml/                 # Preparação de dados, treinamento e artefatos
scripts/            # Verificações manuais das integrações
tests/              # Testes da API
compose.yaml        # PostgreSQL para desenvolvimento
requirements.txt    # Dependências Python
```

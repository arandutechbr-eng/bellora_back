# Bellora — Backend FastAPI

API do marketplace de beleza e estética.

Repo: `arandutechbr-eng/bellora_back`

## Estrutura

```txt
bellora_back/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   └── schemas/
├── requirements.txt
├── runtime.txt
└── .env.example
```

## Como rodar (local)

```bash
cd back
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Docs: http://localhost:8000/docs

## Deploy no Render

| Campo | Valor |
|-------|--------|
| **Root Directory** | *(vazio)* |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

Variável: `PYTHON_VERSION=3.11.9`

## Usuários de teste

| Papel | E-mail | Senha |
|-------|--------|-------|
| Cliente | cliente@bellora.com | 123456 |
| Profissional (cabelo) | cabelo@bellora.com | 123456 |
| Profissional (unhas) | unhas@bellora.com | 123456 |

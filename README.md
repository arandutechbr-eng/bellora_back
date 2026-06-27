# Bellora — Backend FastAPI

API do marketplace de beleza e estética.

## Estrutura

```txt
back/backend/
├── app/
│   ├── api/
│   ├── constants/
│   ├── core/
│   ├── db/
│   ├── models/
│   └── schemas/
├── requirements.txt
└── .env.example
```

## Como rodar

```bash
cd back/backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Docs: http://localhost:8000/docs

## Usuários de teste

| Papel | E-mail | Senha |
|-------|--------|-------|
| Cliente | cliente@bellora.com | 123456 |
| Profissional (cabelo) | cabelo@bellora.com | 123456 |
| Profissional (unhas) | unhas@bellora.com | 123456 |

## Endpoints principais

```txt
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
GET  /api/v1/categories
GET  /api/v1/professionals
GET  /api/v1/professionals/{id}
GET  /api/v1/reviews/professional/{professional_id}
POST /api/v1/requests
GET  /api/v1/requests/me
GET  /api/v1/messages/request/{request_id}
POST /api/v1/messages
```

## Como conectar no frontend Vite

No seu projeto React, crie o arquivo `.env` na raiz do `front`:

```txt
VITE_API_URL=http://localhost:8000/api/v1
```

Copie os arquivos de:

```txt
frontend-integration/src/services
```

para:

```txt
front/src/services
```

Depois substitua as chamadas mockadas por chamadas como:

```ts
import { marketplaceService } from '@/services/marketplaceService';

const professionals = await marketplaceService.professionals({
  city: 'Santos',
  min_rating: 4,
});
```

Login:

```ts
import { authService } from '@/services/authService';

await authService.login({
  email: 'cliente@zola.com',
  password: '123456',
});
```

## Observação

O banco padrão é SQLite para facilitar o desenvolvimento. Para produção, troque o `DATABASE_URL` por PostgreSQL:

```txt
DATABASE_URL=postgresql+psycopg://usuario:senha@localhost:5432/zola
```

Nesse caso, instale também o driver PostgreSQL.

## Upload de imagens (produção)

No **Render**, o disco é **temporário**: arquivos em `uploads/` somem no redeploy. Use **Supabase Storage**:

1. Supabase → **Storage** → **New bucket** → `zola-uploads` → marque **Public**
2. **Project Settings → API** → copie **Project URL** e **service_role** key
3. No Render, adicione:

```txt
PUBLIC_API_BASE_URL=https://zola-back.onrender.com
SUPABASE_URL=https://SEU_PROJECT_REF.supabase.co
SUPABASE_SERVICE_ROLE_KEY=sua-service-role-key
SUPABASE_STORAGE_BUCKET=zola-uploads
```

Sem essas variáveis, o upload até funciona, mas a URL pode apontar para `localhost` ou a imagem some após redeploy.

## Pagamentos no agendamento (Stripe)

Para exigir **sinal** ao reservar um horário (padrão: **30%** do valor, mínimo R$ 25):

1. Crie conta em [Stripe](https://stripe.com) (modo teste para desenvolvimento)
2. **Developers → API keys** → copie a **Secret key**
3. **Developers → Webhooks** → endpoint `https://zola-back.onrender.com/api/v1/webhooks/stripe`
   - Eventos: `checkout.session.completed`, `checkout.session.expired`
4. No Render:

```txt
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
BOOKING_DEPOSIT_PERCENT=30
BOOKING_DEPOSIT_MIN_BRL=25
FRONTEND_ORIGIN=https://seu-front.vercel.app
```

**Local sem Stripe:** `PAYMENTS_MOCK=true` confirma agendamentos sem cobrança.

Fluxo: cliente escolhe horário → paga sinal no Stripe → webhook confirma → agenda bloqueada. Reservas não pagas expiram em 30 minutos.

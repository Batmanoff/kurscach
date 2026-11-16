# ATELIER — Fashion Store (kurscach)

Премиальный fashion e-commerce (вдохновление: Zara / ASOS / Farfetch / COS) с российским стеком: **Flask + PostgreSQL + ЮKassa СБП** и **Next.js**.

```
fashion-store/frontend/   # Next.js 14, React, TypeScript, Tailwind, Framer Motion
fashion-store/backend/    # Python 3.12+, Flask, SQLAlchemy, JWT, YooKassa
docker-compose.yml
.env.example
```

## Возможности

- Каталог, карточка товара, корзина, избранное, кабинет, админ-панель
- JWT auth + роль `admin`
- Заказы в ₽ со статусами: `pending_payment`, `paid`, `processing`, `shipped`, `delivered`, `cancelled`, `refunded`
- Оплата **СБП через ЮKassa** (QR + confirmation URL + webhook + идемпотентность)
- **Mock-режим**, если `YOOKASSA_*` пустые — локальная разработка без ключей
- Seed-каталог через supplier adapter (без scraping)
- Docker Compose, Gunicorn, GitHub Actions skeleton

## Быстрый старт (Windows)

### 1. Клонирование и env

```powershell
cd C:\Users\batma\Projects\kurscach
Copy-Item .env.example .env
```

### 2. Backend (SQLite без Docker)

```powershell
cd fashion-store\backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:FLASK_APP = "run.py"
$env:DATABASE_URL = "sqlite:///fashion_store.db"
python seed.py
python run.py
```

API: http://localhost:5000/api/health

Демо-пользователи (после seed):

| Роль  | Email             | Пароль    |
|-------|-------------------|-----------|
| admin | admin@atelier.dev | Admin123! |
| demo  | demo@atelier.dev  | Demo123!  |

Промокод: `WELCOME10` (−10% от 5000 ₽).

### 3. Frontend

Нужны Node.js 20+ и npm:

```powershell
cd fashion-store\frontend
npm install
$env:NEXT_PUBLIC_API_URL = "http://localhost:5000/api"
npm run dev
```

UI: http://localhost:3000

### 4. PostgreSQL + Docker (опционально)

```powershell
Copy-Item .env.example .env
docker compose up --build
```

- Frontend: http://localhost:3000  
- Backend: http://localhost:5000  

## ЮKassa СБП

1. Создайте магазин в [ЮKassa](https://yookassa.ru/)
2. В `.env` укажите:
   - `YOOKASSA_SHOP_ID`
   - `YOOKASSA_SECRET_KEY`
   - `YOOKASSA_RETURN_URL` (например `http://localhost:3000/checkout/success`)
   - `YOOKASSA_WEBHOOK_SECRET` (рекомендуется)
3. Webhook URL: `POST /api/payments/webhook`
4. **Не доверяйте статусу с фронта** — только webhook или `GET /api/payments/<id>/status` (серверный lookup)

Без ключей API создаёт mock-платёж: QR + страница «банк» `/checkout/mock-pay` и `POST /api/payments/mock/confirm`.

### Альтернативы (заметки)

- **Т-Банк эквайринг / СБП**: отдельный merchant API, webhook + idempotency key; адаптер можно добавить рядом с `app/payments/yookassa_client.py`.
- **Robokassa**: ResultURL/SuccessURL, пароль #2 для подписи; не хранить пароли в репозитории.

## API (кратко)

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/auth/register` | Регистрация |
| POST | `/api/auth/login` | JWT |
| GET | `/api/auth/me` | Профиль |
| GET | `/api/products` | Каталог |
| GET | `/api/products/<slug>` | Карточка |
| GET/POST/PATCH/DELETE | `/api/cart`… | Корзина |
| GET/POST/DELETE | `/api/favorites`… | Избранное |
| POST | `/api/orders` | Создать заказ из корзины |
| POST | `/api/orders/<id>/pay` | Создать СБП-платёж |
| POST | `/api/payments/create` | Платёж |
| GET | `/api/payments/<id>/status` | Статус |
| POST | `/api/payments/webhook` | ЮKassa webhook |
| GET/PATCH | `/api/admin/…` | Админка |

## Миграции

```powershell
cd fashion-store\backend
.\.venv\Scripts\Activate.ps1
$env:FLASK_APP = "run.py"
flask db init      # один раз
flask db migrate -m "init"
flask db upgrade
```

Для SQLite-демо `seed.py` вызывает `db.create_all()`.

## Безопасность

- Пароли: Werkzeug hash
- JWT access/refresh
- Rate limit на auth
- Валидация полей, проверка stock при заказе
- Секреты только в `.env` (не коммитить)

## Структура backend

```
fashion-store/backend/
  app/__init__.py
  app/config.py
  app/models/
  app/routes/
  app/services/
  app/payments/
  app/auth/
  app/utils/
  run.py
  seed.py
  requirements.txt
  Dockerfile
```

## Production

- `gunicorn -b 0.0.0.0:5000 -w 2 run:app`
- PostgreSQL + Redis (rate limit storage)
- HTTPS, реальные ЮKassa ключи, webhook secret
- Frontend: `next build && next start` или Docker `standalone`
- CI skeleton: `.github/workflows/deploy.yml`

Подробнее для локального Windows-запуска: см. также документ в Project store `docs/how-to-run-local.md`.

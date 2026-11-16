# ATELIER — подробный setup

Краткий запуск: см. [README.md](../README.md) → `start.bat`.

## Стек

- `fashion-store/backend` — Flask, SQLAlchemy, JWT, ЮKassa SBP (mock без ключей)
- `fashion-store/frontend` — Next.js 14, TypeScript, Tailwind, Framer Motion
- По умолчанию SQLite (`sqlite:///fashion_store.db` в `instance/`)
- Redis опционален (rate limit → memory)
- Docker Compose — только если нужен PostgreSQL

## Ручной запуск (без start.bat)

```powershell
cd fashion-store\backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DATABASE_URL = "sqlite:///fashion_store.db"
python seed.py
python run.py
```

```powershell
cd fashion-store\frontend
npm install
$env:NEXT_PUBLIC_API_URL = "http://127.0.0.1:5000/api"
npm run dev
```

## ЮKassa СБП

В `.env` (из `.env.example`):

- `YOOKASSA_SHOP_ID`, `YOOKASSA_SECRET_KEY`, `YOOKASSA_RETURN_URL`, `YOOKASSA_WEBHOOK_SECRET`
- Webhook: `POST /api/payments/webhook`
- Без ключей работает **mock** (QR + `/checkout/mock-pay`)

Статус оплаты берётся с сервера, не с фронта.

Заметки: Т-Банк / Robokassa — отдельные адаптеры рядом с `app/payments/yookassa_client.py`.

## Docker (опционально)

```powershell
Copy-Item .env.example .env
docker compose up --build
```

UI :3000 · API :5000

## Миграции (PostgreSQL)

```powershell
cd fashion-store\backend
$env:FLASK_APP = "run.py"
flask db migrate -m "init"
flask db upgrade
```

Для SQLite-демо достаточно `python seed.py` (`db.create_all`).

## API (кратко)

Auth, products, cart, favorites, orders, payments (create/status/webhook/mock), admin — префикс `/api/`.

## Production

Gunicorn, PostgreSQL, HTTPS, реальные ключи ЮKassa. CI skeleton: `.github/workflows/deploy.yml`.

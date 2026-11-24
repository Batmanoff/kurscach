# Хостинг ATELIER (курсовая)

Локально достаточно `start.bat` (Flask + SQLite). На хостинге обычно нужен **PostgreSQL** и **Gunicorn**.

## Что деплоить

Только `fashion-store/backend` (+ корневые `.env`).  
Витрина уже внутри Flask (Jinja). Next.js **не нужен**.

## Переменные окружения

Скопируйте `.env.example` → `.env` на сервере и задайте:

| Переменная | Зачем |
|---|---|
| `SECRET_KEY` | Сессии Flask |
| `JWT_SECRET_KEY` | JWT API |
| `DATABASE_URL` | `postgresql+psycopg://USER:PASS@HOST:5432/DB` |
| `BACKEND_URL` | Публичный URL сайта, напр. `https://your-app.onrender.com` |
| `FRONTEND_URL` | Тот же URL (один сервис) |
| `YOOKASSA_RETURN_URL` | `https://…/checkout/success` |
| `YOOKASSA_SHOP_ID` / `YOOKASSA_SECRET_KEY` | Боевые ключи (пусто = mock) |
| `YOOKASSA_WEBHOOK_SECRET` | Подпись webhook (рекомендуется) |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | Первый админ при seed |

Webhook ЮKassa: `POST https://ВАШ_ДОМЕН/api/payments/webhook`

## Render / Railway

1. New Web Service → репозиторий `Batmanoff/kurscach`
2. Root / build: каталог `fashion-store/backend` (или Dockerfile там же)
3. Start: см. `Procfile` → `gunicorn -b 0.0.0.0:$PORT -w 2 run:app`
4. Добавьте Postgres addon → подставьте `DATABASE_URL` (для SQLAlchemy: `postgresql+psycopg://…`)
5. После первого деплоя: `python seed.py` (one-off / shell)
6. HTTPS даёт платформа; пропишите webhook в кабинете ЮKassa

`Procfile` в корне репо:

```
web: cd fashion-store/backend && gunicorn -b 0.0.0.0:${PORT:-5000} -w 2 run:app
```

На Render удобнее Dockerfile:

```
docker build -t atelier ./fashion-store/backend
```

## VPS (Timeweb / Beget / любой Linux)

```bash
git clone https://github.com/Batmanoff/kurscach.git
cd kurscach/fashion-store/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# .env с Postgres + секретами
python seed.py
gunicorn -b 0.0.0.0:5000 -w 2 run:app
```

Перед nginx/caddy: прокси на `127.0.0.1:5000`, SSL (Let's Encrypt).

## Docker (один сервис + Postgres)

```bash
docker compose up --build
```

По умолчанию compose поднимает Postgres и backend на `:5000`. Redis не обязателен.

## ЮKassa на проде

1. Ключи магазина в env  
2. Return URL → `/checkout/success`  
3. Webhook → `/api/payments/webhook`  
4. Не доверяйте статусу с браузера — только webhook / серверный lookup  

## SQLite на хостинге?

Для сдачи демо на VPS с одним диском — можно оставить SQLite, но при рестарте/нескольких воркерах лучше Postgres.

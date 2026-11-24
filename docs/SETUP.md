# Дополнительно

Основной путь: [README.md](../README.md) → `start.bat` (только Flask).  
Хостинг: [HOSTING.md](HOSTING.md).

## Опциональный Next.js

Папка `fashion-store/frontend` — **не нужна** для курсовой и хостинга.  
Это запасной SPA к JSON API (`/api/...`). Для запуска UI хватает Flask + Jinja.

## Ручной запуск backend

```powershell
cd fashion-store\backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:DATABASE_URL = "sqlite:///fashion_store.db"
python seed.py
python run.py
```

Открыть http://127.0.0.1:5000

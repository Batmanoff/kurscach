# Optional Next.js frontend

**Не требуется** для курсовой и хостинга.

Основная витрина — Flask + Jinja2 (`fashion-store/backend`, порт 5000).

Этот каталог — запасной React/Next UI к JSON API. Запускайте только если нужен отдельный фронт:

```powershell
npm install
$env:NEXT_PUBLIC_API_URL = "http://127.0.0.1:5000/api"
npm run dev
```

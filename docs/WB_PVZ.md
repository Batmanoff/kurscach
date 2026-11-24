# Доставка в ПВЗ Wildberries (курсовая «коллаба»)

Учебная интеграция: выбор пункта выдачи WB на checkout. Это **не** партнёрский договор с WB, а использование **публично доступных** данных карты/webapi, которые открывает сайт WB без ключей.

## Публичные endpoints

| Метод | URL | Назначение |
|---|---|---|
| GET | `https://www.wildberries.ru/webapi/spa/modules/pickups` | Компактный список ПВЗ: `value.pickups[]` → `id`, `coordinates: [lat, lon]` |
| POST | `https://www.wildberries.ru/webapi/poo/byids` | Детали по id: `address`, `workTime`, `rate`, `wayInfo` |
| UI | `https://map.wb.ru/` | Официальная карта ПВЗ |

Секреты не нужны. Официальный seller API WB полного справочника ПВЗ не отдаёт — для карты сайта используются webapi выше.

## Наш API

```
GET /api/delivery/pvz?city=Москва
GET /api/delivery/pvz?lat=55.75&lon=37.62&limit=20
```

Ответ: `{ items, source, fallback, meta }`.  
Если WB недоступен — `source: "seed"` и демо-список (Москва, СПб, Казань…).

## Как попробовать в UI

1. `start.bat` → http://127.0.0.1:5000  
2. Войти (`demo@atelier.dev` / `Demo123!`) → корзина → **Оформить**  
3. Способ: **Доставка в ПВЗ Wildberries** → «Найти ПВЗ в городе» → выбрать пункт → оплата (mock СБП)

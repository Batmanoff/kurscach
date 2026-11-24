# Доставка в ПВЗ Яндекс Маркет (курсовая)

Checkout предлагает **«Доставка в ПВЗ Яндекс Маркет»**. Это учебная интеграция, не партнёрский договор.

## Откуда данные (легально)

| Источник | Когда | Документация / UI |
|---|---|---|
| **Seed** (по умолчанию) | Нет ключей / офлайн | Демо-адреса (Вологда, Москва, СПб…) |
| **Yandex Maps Geosearch** | `YANDEX_MAPS_API_KEY` | https://yandex.ru/dev/geosearch/doc/ru/ |
| **Market Partner logistics-points** | `YANDEX_MARKET_API_KEY` + `YANDEX_MARKET_BUSINESS_ID` | [getLogisticPoints](https://yandex.ru/dev/market/partner-api/doc/ru/reference/logistic-points/getLogisticPoints) |
| **Карта категории** | Всегда ссылка в UI | https://yandex.ru/maps/21/vologda/category/point_of_delivery/18955887118/ |

Приватные/недокументированные API не парсим. Seller logistics-points — только с официальным API-Key.

## Наш endpoint

```
GET /api/delivery/pvz?city=Вологда
GET /api/delivery/pvz?city=Москва
GET /api/delivery/pvz?lat=59.22&lon=39.89&limit=20
```

Ответ: `{ items, source, fallback, map_url, provider: "yandex_market", meta }`.

## Как попробовать

1. `start.bat` → http://127.0.0.1:5000  
2. Войти → корзина → **Оформить**  
3. Город: `Вологда` или `Москва` → **Доставка в ПВЗ Яндекс Маркет** → «Найти ПВЗ» → выбрать → оплата  

WB webapi на BASTARD был недоступен — основной путь теперь Яндекс (seed + опциональные ключи). Старый `docs/WB_PVZ.md` оставлен как архив.

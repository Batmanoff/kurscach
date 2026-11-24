# Доставка в ПВЗ Яндекс Маркет (курсовая)

Checkout предлагает **«Доставка в ПВЗ Яндекс Маркет»**. Это учебная интеграция, не партнёрский договор.

## Карта на checkout

На шаге оформления слева — **встроенная карта**, справа — список ПВЗ.

| Режим | Когда | Что видно |
|---|---|---|
| **iframe map-widget** | Без ключа (по умолчанию) | Живая карта Яндекса по городу (`embed_url`) |
| **JS API 2.1** | Задан `YANDEX_MAPS_API_KEY` | Та же панель + метки из списка, клик по метке = выбор ПВЗ |

Ссылка на категорию (референс Вологда):  
https://yandex.ru/maps/21/vologda/category/point_of_delivery/18955887118/

## Откуда данные списка (легально)

| Источник | Когда | Документация / UI |
|---|---|---|
| **Seed** (по умолчанию) | Нет ключей / офлайн | Демо-адреса (Вологда, Москва, СПб…) |
| **Yandex Maps Geosearch** | `YANDEX_MAPS_API_KEY` | https://yandex.ru/dev/geosearch/doc/ru/ |
| **Market Partner logistics-points** | `YANDEX_MARKET_API_KEY` + `YANDEX_MARKET_BUSINESS_ID` | [getLogisticPoints](https://yandex.ru/dev/market/partner-api/doc/ru/reference/logistic-points/getLogisticPoints) |
| **Карта категории** | Всегда ссылка + iframe | point_of_delivery / map-widget |

Приватные API не парсим. Seller logistics-points — только с официальным API-Key.

## Endpoint

```
GET /api/delivery/pvz?city=Вологда
GET /api/delivery/pvz?city=Москва
GET /api/delivery/pvz?lat=59.22&lon=39.89&limit=20
```

Ответ: `{ items, source, fallback, map_url, embed_url, center, provider: "yandex_market", meta }`.

## Как попробовать

1. `start.bat` → http://127.0.0.1:5000  
2. Войти → корзина → **Оформить**  
3. Режим **«Доставка в ПВЗ Яндекс Маркет»** → город `Вологда` / `Москва` → карта + «Найти ПВЗ» → выбрать в списке → оплата  

Опционально в `.env`: `YANDEX_MAPS_API_KEY=` (JS API + Geosearch). Без ключа карта всё равно показывается через iframe.

WB webapi в учебной среде был недоступен — основной путь Яндекс (seed + опциональные ключи). Старый `docs/WB_PVZ.md` — архив.

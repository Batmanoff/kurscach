"""
Yandex Market PVZ (pickup points) for coursework checkout.

Legal sources (no private scraping):
  1) Seeded demo catalog (always works offline) — labeled «Яндекс Маркет ПВЗ».
  2) Optional Yandex Maps Geosearch (documented, needs YANDEX_MAPS_API_KEY):
       GET https://search-maps.yandex.ru/v1/
       docs: https://yandex.ru/dev/geosearch/doc/ru/
  3) Optional Market Partner logistics-points (seller API-Key, LaaS):
       POST https://api.partner.market.yandex.ru/v1/businesses/{id}/logistics-points
       docs: https://yandex.ru/dev/market/partner-api/doc/ru/reference/logistic-points/getLogisticPoints

Public map UI (category point_of_delivery):
  https://yandex.ru/maps/…/category/point_of_delivery/18955887118/
  Example (Вологда):
  https://yandex.ru/maps/21/vologda/category/point_of_delivery/18955887118/
"""

from __future__ import annotations

import math
import os
import threading
import time
from typing import Any
from urllib.parse import quote

import requests

GEOSEARCH_URL = "https://search-maps.yandex.ru/v1/"
PARTNER_POINTS_URL = "https://api.partner.market.yandex.ru/v1/businesses/{business_id}/logistics-points"
CATEGORY_ID = "18955887118"
MAPS_CATEGORY_TMPL = (
    "https://yandex.ru/maps/?text={query}&category=point_of_delivery"
)
# City slug examples for nicer deep links when known
CITY_MAP_LINKS: dict[str, str] = {
    "вологда": "https://yandex.ru/maps/21/vologda/category/point_of_delivery/18955887118/",
    "москва": "https://yandex.ru/maps/213/moscow/category/point_of_delivery/18955887118/",
    "санкт-петербург": "https://yandex.ru/maps/2/saint-petersburg/category/point_of_delivery/18955887118/",
    "спб": "https://yandex.ru/maps/2/saint-petersburg/category/point_of_delivery/18955887118/",
}

_CACHE_TTL = 20 * 60
_lock = threading.Lock()
_geo_cache: dict[str, Any] = {}

CITY_COORDS: dict[str, tuple[float, float]] = {
    "москва": (55.7558, 37.6173),
    "санкт-петербург": (59.9311, 30.3609),
    "спб": (59.9311, 30.3609),
    "питер": (59.9311, 30.3609),
    "вологда": (59.2205, 39.8915),
    "новосибирск": (55.0084, 82.9357),
    "екатеринбург": (56.8389, 60.6057),
    "казань": (55.7961, 49.1064),
    "нижний новгород": (56.2965, 43.9361),
    "челябинск": (55.1644, 61.4368),
    "самара": (53.1959, 50.1002),
    "ростов-на-дону": (47.2357, 39.7015),
    "краснодар": (45.0355, 38.9753),
    "воронеж": (51.6720, 39.1843),
    "пермь": (58.0105, 56.2502),
    "ярославль": (57.6261, 39.8845),
    "тула": (54.1931, 37.6173),
    "сочи": (43.6028, 39.7342),
}

# Realistic demo points (coursework). Not scraped live — student can cross-check on Maps.
SEEDED_PVZ: list[dict[str, Any]] = [
    {
        "id": "ym-vlg-1",
        "address": "г. Вологда, ул. Мира, д. 30",
        "work_time": "Ежедневно 10:00–21:00",
        "lat": 59.2185,
        "lon": 39.8820,
        "city": "Вологда",
        "brand": "Яндекс Маркет",
        "source": "seed",
    },
    {
        "id": "ym-vlg-2",
        "address": "г. Вологда, ул. Ленинградская, д. 71",
        "work_time": "Ежедневно 09:00–21:00",
        "lat": 59.2100,
        "lon": 39.8700,
        "city": "Вологда",
        "brand": "Яндекс Маркет",
        "source": "seed",
    },
    {
        "id": "ym-vlg-3",
        "address": "г. Вологда, Окружное шоссе, д. 12",
        "work_time": "Ежедневно 10:00–22:00",
        "lat": 59.1980,
        "lon": 39.9050,
        "city": "Вологда",
        "brand": "Яндекс Маркет",
        "source": "seed",
    },
    {
        "id": "ym-msk-1",
        "address": "г. Москва, ул. Тверская, д. 6/1",
        "work_time": "Ежедневно 10:00–22:00",
        "lat": 55.7580,
        "lon": 37.6130,
        "city": "Москва",
        "brand": "Яндекс Маркет",
        "source": "seed",
    },
    {
        "id": "ym-msk-2",
        "address": "г. Москва, Ленинградский проспект, д. 36",
        "work_time": "Ежедневно 09:00–21:00",
        "lat": 55.7880,
        "lon": 37.5480,
        "city": "Москва",
        "brand": "Яндекс Маркет",
        "source": "seed",
    },
    {
        "id": "ym-msk-3",
        "address": "г. Москва, ул. Профсоюзная, д. 45",
        "work_time": "Ежедневно 10:00–22:00",
        "lat": 55.6770,
        "lon": 37.5620,
        "city": "Москва",
        "brand": "Яндекс Маркет",
        "source": "seed",
    },
    {
        "id": "ym-msk-4",
        "address": "г. Москва, Варшавское шоссе, д. 87",
        "work_time": "Ежедневно 10:00–21:00",
        "lat": 55.6530,
        "lon": 37.6200,
        "city": "Москва",
        "brand": "Яндекс Маркет",
        "source": "seed",
    },
    {
        "id": "ym-spb-1",
        "address": "г. Санкт-Петербург, Невский проспект, д. 40",
        "work_time": "Ежедневно 10:00–22:00",
        "lat": 59.9330,
        "lon": 30.3400,
        "city": "Санкт-Петербург",
        "brand": "Яндекс Маркет",
        "source": "seed",
    },
    {
        "id": "ym-spb-2",
        "address": "г. Санкт-Петербург, Московский проспект, д. 129",
        "work_time": "Ежедневно 09:00–21:00",
        "lat": 59.8800,
        "lon": 30.3200,
        "city": "Санкт-Петербург",
        "brand": "Яндекс Маркет",
        "source": "seed",
    },
    {
        "id": "ym-kzn-1",
        "address": "г. Казань, ул. Баумана, д. 9",
        "work_time": "Ежедневно 10:00–21:00",
        "lat": 55.7870,
        "lon": 49.1225,
        "city": "Казань",
        "brand": "Яндекс Маркет",
        "source": "seed",
    },
]


def _norm(s: str) -> str:
    return (s or "").strip().lower().replace("ё", "е")


def _city_coords(city: str) -> tuple[float, float] | None:
    key = _norm(city)
    if key in CITY_COORDS:
        return CITY_COORDS[key]
    for name, coords in CITY_COORDS.items():
        if name in key or key in name:
            return coords
    return None


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def maps_category_url(city: str | None = None) -> str:
    key = _norm(city or "")
    if key in CITY_MAP_LINKS:
        return CITY_MAP_LINKS[key]
    if city:
        return (
            f"https://yandex.ru/maps/?text={quote('пункты выдачи Яндекс Маркет ' + city)}"
            f"&category=point_of_delivery"
        )
    return f"https://yandex.ru/maps/?category=point_of_delivery&text={quote('Яндекс Маркет пункт выдачи')}"


def maps_embed_url(city: str | None = None, lat: float | None = None, lon: float | None = None) -> str:
    """Iframe-friendly Yandex map-widget centered on city / PVZ search text (no API key)."""
    coords = None
    if lat is not None and lon is not None:
        coords = (float(lat), float(lon))
    else:
        coords = _city_coords(city) or (59.2205, 39.8915)  # Вологда — reference page
    clat, clon = coords
    label = city or "Вологда"
    text = quote(f"пункт выдачи Яндекс Маркет {label}")
    # ll is lon,lat for map-widget
    return f"https://yandex.ru/map-widget/v1/?ll={clon},{clat}&z=12&l=map&text={text}"


def city_center(city: str | None = None) -> dict[str, float]:
    coords = _city_coords(city) or (59.2205, 39.8915)
    return {"lat": coords[0], "lon": coords[1]}


def _meta() -> dict[str, Any]:
    return {
        "provider": "yandex_market",
        "category_id": CATEGORY_ID,
        "docs": {
            "geosearch": "https://yandex.ru/dev/geosearch/doc/ru/",
            "maps_js": "https://yandex.ru/dev/jsapi-v2-1/doc/ru/",
            "partner_logistic_points": (
                "https://yandex.ru/dev/market/partner-api/doc/ru/reference/"
                "logistic-points/getLogisticPoints"
            ),
        },
        "maps_category_example": CITY_MAP_LINKS["вологда"],
        "notes": (
            "Карта на checkout: iframe map-widget без ключа; "
            "при YANDEX_MAPS_API_KEY — JS API с метками из списка. "
            "Partner logistics-points — только с API-Key продавца."
        ),
    }


def _seed_search(*, city: str | None, lat: float | None, lon: float | None, limit: int) -> list[dict]:
    items = [dict(p) for p in SEEDED_PVZ]
    if city:
        c = _norm(city)
        filtered = [
            p
            for p in items
            if c in _norm(p.get("city", "")) or c in _norm(p.get("address", ""))
        ]
        if filtered:
            items = filtered
    if lat is not None and lon is not None:
        for p in items:
            p["distance_km"] = round(_haversine_km(lat, lon, float(p["lat"]), float(p["lon"])), 2)
        items.sort(key=lambda p: p.get("distance_km", 9999))
    for p in items:
        p.setdefault("brand", "Яндекс Маркет")
        p["map_url"] = maps_category_url(p.get("city") or city)
    return items[:limit]


def _geosearch(city: str | None, lat: float | None, lon: float | None, limit: int) -> list[dict] | None:
    api_key = (os.getenv("YANDEX_MAPS_API_KEY") or "").strip()
    if not api_key:
        return None
    cache_key = f"{city}|{lat}|{lon}|{limit}"
    now = time.time()
    with _lock:
        hit = _geo_cache.get(cache_key)
        if hit and now - hit["t"] < _CACHE_TTL:
            return hit["items"]

    text = "пункт выдачи Яндекс Маркет"
    if city:
        text = f"{text}, {city}"
    params: dict[str, Any] = {
        "apikey": api_key,
        "text": text,
        "type": "biz",
        "lang": "ru_RU",
        "results": min(limit, 25),
    }
    if lat is not None and lon is not None:
        params["ll"] = f"{lon},{lat}"
        params["spn"] = "0.3,0.3"

    try:
        resp = requests.get(GEOSEARCH_URL, params=params, timeout=10)
        if resp.status_code != 200:
            return None
        features = (resp.json() or {}).get("features") or []
    except Exception:
        return None

    items: list[dict] = []
    for f in features:
        props = f.get("properties") or {}
        geom = f.get("geometry") or {}
        coords = geom.get("coordinates") or [None, None]
        # GeoJSON: [lon, lat]
        lon_v, lat_v = (coords + [None, None])[:2]
        company = props.get("CompanyMetaData") or {}
        hours = ""
        try:
            hours = (company.get("Hours") or {}).get("text") or ""
        except Exception:
            hours = ""
        addr = company.get("address") or props.get("description") or props.get("name") or "ПВЗ Яндекс Маркет"
        items.append(
            {
                "id": str(company.get("id") or props.get("id") or f"geo-{len(items)}"),
                "address": addr,
                "work_time": hours,
                "lat": float(lat_v) if lat_v is not None else None,
                "lon": float(lon_v) if lon_v is not None else None,
                "city": city or "",
                "brand": "Яндекс Маркет",
                "source": "yandex_geosearch",
                "map_url": maps_category_url(city),
            }
        )
    with _lock:
        _geo_cache[cache_key] = {"t": now, "items": items}
    return items


def _partner_points(limit: int) -> list[dict] | None:
    api_key = (os.getenv("YANDEX_MARKET_API_KEY") or "").strip()
    business_id = (os.getenv("YANDEX_MARKET_BUSINESS_ID") or "").strip()
    if not api_key or not business_id:
        return None
    url = PARTNER_POINTS_URL.format(business_id=business_id)
    try:
        resp = requests.post(
            url,
            params={"limit": min(limit, 100)},
            headers={"Api-Key": api_key, "Content-Type": "application/json"},
            json={},
            timeout=12,
        )
        if resp.status_code != 200:
            return None
        points = ((resp.json() or {}).get("result") or {}).get("logisticPoints") or []
    except Exception:
        return None

    items: list[dict] = []
    for p in points[:limit]:
        addr = p.get("address") or {}
        gps = addr.get("gps") or {}
        full = addr.get("fullAddress") or ", ".join(
            filter(None, [addr.get("city"), addr.get("street"), addr.get("house")])
        )
        items.append(
            {
                "id": str(p.get("logisticPointId")),
                "address": full or f"ПВЗ #{p.get('logisticPointId')}",
                "work_time": "",
                "lat": gps.get("latitude"),
                "lon": gps.get("longitude"),
                "city": addr.get("city") or "",
                "brand": p.get("brand") or "MARKET",
                "source": "yandex_partner_api",
                "map_url": maps_category_url(addr.get("city")),
            }
        )
    return items


def search_pvz(
    *,
    city: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    limit = max(1, min(int(limit or 20), 50))
    if (lat is None or lon is None) and city:
        coords = _city_coords(city)
        if coords:
            lat, lon = coords

    map_url = maps_category_url(city)
    embed_url = maps_embed_url(city, lat, lon)
    center = city_center(city)

    def _pack(items: list[dict], source: str, fallback: bool, message: str | None = None) -> dict[str, Any]:
        data: dict[str, Any] = {
            "items": items,
            "source": source,
            "fallback": fallback,
            "count": len(items),
            "map_url": map_url,
            "embed_url": embed_url,
            "center": center,
            "provider": "yandex_market",
            "meta": _meta(),
        }
        if message:
            data["message"] = message
        return data

    # 1) Documented Partner API if keys present
    partner = _partner_points(limit)
    if partner:
        if city:
            c = _norm(city)
            partner = [p for p in partner if c in _norm(p.get("city", "")) or c in _norm(p.get("address", ""))] or partner
        if lat is not None and lon is not None:
            for p in partner:
                if p.get("lat") is not None and p.get("lon") is not None:
                    p["distance_km"] = round(_haversine_km(lat, lon, float(p["lat"]), float(p["lon"])), 2)
            partner.sort(key=lambda p: p.get("distance_km", 9999))
        return _pack(partner[:limit], "yandex_partner_api", False)

    # 2) Documented Geosearch if Maps API key present
    geo = _geosearch(city, lat, lon, limit)
    if geo:
        return _pack(geo[:limit], "yandex_geosearch", False)

    # 3) Seed (default for coursework — no secrets)
    seeded = _seed_search(city=city, lat=lat, lon=lon, limit=limit)
    return _pack(
        seeded,
        "seed",
        True,
        (
            "Используется демо-список ПВЗ Яндекс Маркет. "
            "Карта — iframe map-widget; для JS API / Geosearch задайте YANDEX_MAPS_API_KEY."
        ),
    )

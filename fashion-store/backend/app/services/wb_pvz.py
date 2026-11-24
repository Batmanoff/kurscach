"""
Wildberries PVZ (pickup points) — public map/webapi client + offline seed.

Public endpoints used (no auth; WB website/map data as commonly referenced):
  GET  https://www.wildberries.ru/webapi/spa/modules/pickups
       → value.pickups[]: { id, coordinates: [lat, lon], ... }
  POST https://www.wildberries.ru/webapi/poo/byids
       body: [id, ...]
       → value: { "<id>": { address, workTime, rate, wayInfo, ... } }

Public map UI: https://map.wb.ru/
Official seller API does not expose a full PVZ catalog; coursework uses the
same publicly reachable webapi the site map uses, with a seeded fallback.
"""

from __future__ import annotations

import math
import threading
import time
from typing import Any

import requests

PICKUPS_URL = "https://www.wildberries.ru/webapi/spa/modules/pickups"
BYIDS_URL = "https://www.wildberries.ru/webapi/poo/byids"
MAP_UI = "https://map.wb.ru/"

_CACHE_TTL_SEC = 30 * 60
_lock = threading.Lock()
_cache: dict[str, Any] = {"pickups": None, "fetched_at": 0.0, "source": "none"}

# Approx city centers for city→coords search (coursework helper).
CITY_COORDS: dict[str, tuple[float, float]] = {
    "москва": (55.7558, 37.6173),
    "санкт-петербург": (59.9311, 30.3609),
    "спб": (59.9311, 30.3609),
    "питер": (59.9311, 30.3609),
    "новосибирск": (55.0084, 82.9357),
    "екатеринбург": (56.8389, 60.6057),
    "казань": (55.7961, 49.1064),
    "нижний новгород": (56.2965, 43.9361),
    "челябинск": (55.1644, 61.4368),
    "самара": (53.1959, 50.1002),
    "омск": (54.9885, 73.3242),
    "ростов-на-дону": (47.2357, 39.7015),
    "уфа": (54.7388, 55.9721),
    "красноярск": (56.0153, 92.8932),
    "воронеж": (51.6720, 39.1843),
    "пермь": (58.0105, 56.2502),
    "волгоград": (48.7080, 44.5133),
    "краснодар": (45.0355, 38.9753),
    "саратов": (51.5336, 46.0343),
    "тюмень": (57.1522, 65.5272),
    "тольятти": (53.5303, 49.3461),
    "ижевск": (56.8527, 53.2115),
    "барнаул": (53.3481, 83.7798),
    "иркутск": (52.2869, 104.3050),
    "хабаровск": (48.4827, 135.0838),
    "ярославль": (57.6261, 39.8845),
    "владивосток": (43.1155, 131.8855),
    "махачкала": (42.9849, 47.5047),
    "томск": (56.4846, 84.9476),
    "оренбург": (51.7727, 55.0988),
    "кемерово": (55.3549, 86.0885),
    "рязань": (54.6292, 39.7363),
    "астрахань": (46.3497, 48.0408),
    "пенза": (53.2001, 45.0046),
    "липецк": (52.6031, 39.5708),
    "киров": (58.6035, 49.6679),
    "чебоксары": (56.1439, 47.2489),
    "калининград": (54.7104, 20.4522),
    "тула": (54.1931, 37.6173),
    "сочи": (43.6028, 39.7342),
}

# Offline demo PVZ — coursework still works if WB is unreachable.
SEEDED_PVZ: list[dict[str, Any]] = [
    {
        "id": "seed-msk-1",
        "address": "г. Москва, ул. Тверская, д. 12",
        "work_time": "Ежедневно 10:00–22:00",
        "lat": 55.7570,
        "lon": 37.6150,
        "rate": 4.9,
        "city": "Москва",
        "source": "seed",
    },
    {
        "id": "seed-msk-2",
        "address": "г. Москва, Ленинский проспект, д. 37А",
        "work_time": "Ежедневно 09:00–21:00",
        "lat": 55.7070,
        "lon": 37.5860,
        "rate": 4.8,
        "city": "Москва",
        "source": "seed",
    },
    {
        "id": "seed-msk-3",
        "address": "г. Москва, ул. Профсоюзная, д. 56",
        "work_time": "Ежедневно 10:00–22:00",
        "lat": 55.6700,
        "lon": 37.5550,
        "rate": 4.7,
        "city": "Москва",
        "source": "seed",
    },
    {
        "id": "seed-spb-1",
        "address": "г. Санкт-Петербург, Невский проспект, д. 28",
        "work_time": "Ежедневно 10:00–22:00",
        "lat": 59.9350,
        "lon": 30.3250,
        "rate": 4.9,
        "city": "Санкт-Петербург",
        "source": "seed",
    },
    {
        "id": "seed-spb-2",
        "address": "г. Санкт-Петербург, ул. Васильевский остров, 7-я линия, д. 16",
        "work_time": "Ежедневно 09:00–21:00",
        "lat": 59.9420,
        "lon": 30.2750,
        "rate": 4.6,
        "city": "Санкт-Петербург",
        "source": "seed",
    },
    {
        "id": "seed-kzn-1",
        "address": "г. Казань, ул. Баумана, д. 19",
        "work_time": "Ежедневно 10:00–21:00",
        "lat": 55.7880,
        "lon": 49.1220,
        "rate": 4.8,
        "city": "Казань",
        "source": "seed",
    },
    {
        "id": "seed-ekb-1",
        "address": "г. Екатеринбург, ул. Малышева, д. 36",
        "work_time": "Ежедневно 10:00–22:00",
        "lat": 56.8380,
        "lon": 60.5970,
        "rate": 4.7,
        "city": "Екатеринбург",
        "source": "seed",
    },
    {
        "id": "seed-nsb-1",
        "address": "г. Новосибирск, Красный проспект, д. 17",
        "work_time": "Ежедневно 10:00–21:00",
        "lat": 55.0300,
        "lon": 82.9200,
        "rate": 4.8,
        "city": "Новосибирск",
        "source": "seed",
    },
]


def _headers() -> dict[str, str]:
    return {
        "User-Agent": "ATELIER-Coursework/1.0 (educational; public map data)",
        "Accept": "application/json",
        "x-requested-with": "XMLHttpRequest",
        "Content-Type": "application/json",
    }


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def _normalize_city(city: str) -> str:
    return (city or "").strip().lower().replace("ё", "е")


def _city_coords(city: str) -> tuple[float, float] | None:
    key = _normalize_city(city)
    if key in CITY_COORDS:
        return CITY_COORDS[key]
    for name, coords in CITY_COORDS.items():
        if name in key or key in name:
            return coords
    return None


def _fetch_pickups_raw(timeout: float = 12.0) -> list[dict] | None:
    try:
        resp = requests.get(PICKUPS_URL, headers=_headers(), timeout=timeout)
        if resp.status_code != 200:
            return None
        data = resp.json()
        pickups = (data.get("value") or {}).get("pickups")
        if isinstance(pickups, list) and pickups:
            return pickups
    except Exception:
        return None
    return None


def _fetch_details(ids: list[int], timeout: float = 12.0) -> dict[str, dict]:
    if not ids:
        return {}
    try:
        resp = requests.post(BYIDS_URL, json=ids, headers=_headers(), timeout=timeout)
        if resp.status_code != 200:
            return {}
        value = resp.json().get("value") or {}
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _get_pickups_cached() -> tuple[list[dict], str]:
    now = time.time()
    with _lock:
        if _cache["pickups"] is not None and now - _cache["fetched_at"] < _CACHE_TTL_SEC:
            return _cache["pickups"], _cache["source"]

    raw = _fetch_pickups_raw()
    with _lock:
        if raw is not None:
            _cache["pickups"] = raw
            _cache["fetched_at"] = now
            _cache["source"] = "wb_webapi"
            return raw, "wb_webapi"
        # Keep stale cache if any
        if _cache["pickups"] is not None:
            return _cache["pickups"], _cache["source"] + "_stale"
    return [], "unavailable"


def _point_from_wb(pid: int, coords: list | tuple, detail: dict | None) -> dict[str, Any]:
    detail = detail or {}
    lat = float(coords[0]) if coords and len(coords) >= 2 else None
    lon = float(coords[1]) if coords and len(coords) >= 2 else None
    address = detail.get("address") or detail.get("name") or f"ПВЗ Wildberries #{pid}"
    return {
        "id": str(pid),
        "address": address,
        "work_time": detail.get("workTime") or detail.get("work_time") or "",
        "lat": lat,
        "lon": lon,
        "rate": detail.get("rate"),
        "way_info": detail.get("wayInfo") or "",
        "source": "wb_webapi",
    }


def _seed_search(*, city: str | None, lat: float | None, lon: float | None, limit: int) -> list[dict]:
    items = list(SEEDED_PVZ)
    if city:
        c = _normalize_city(city)
        items = [p for p in items if c in _normalize_city(p.get("city", "")) or c in _normalize_city(p["address"])]
    if lat is not None and lon is not None:
        for p in items:
            p = dict(p)
            p["distance_km"] = round(_haversine_km(lat, lon, p["lat"], p["lon"]), 2)
        items = sorted(items, key=lambda p: p.get("distance_km", 9999))
    return items[:limit]


def search_pvz(
    *,
    city: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    """Search PVZ by city name and/or coordinates. Falls back to seed list."""
    limit = max(1, min(int(limit or 20), 50))
    meta = {
        "endpoints": {"pickups": PICKUPS_URL, "byids": BYIDS_URL, "map_ui": MAP_UI},
        "fields_pickups": ["id", "coordinates"],
        "fields_byids": ["address", "workTime", "rate", "wayInfo"],
    }

    # Resolve city → coords when only city given
    if (lat is None or lon is None) and city:
        coords = _city_coords(city)
        if coords:
            lat, lon = coords

    pickups, source = _get_pickups_cached()
    if not pickups or lat is None or lon is None:
        seeded = _seed_search(city=city, lat=lat, lon=lon, limit=limit)
        return {
            "items": seeded,
            "source": "seed" if source == "unavailable" else f"seed_after_{source}",
            "count": len(seeded),
            "fallback": True,
            "meta": meta,
            "message": "WB webapi недоступен — показан демо-список ПВЗ"
            if source == "unavailable"
            else None,
        }

    # Nearest by coordinates from compact pickups list
    ranked: list[tuple[float, dict]] = []
    for p in pickups:
        try:
            pid = int(p["id"])
            c = p.get("coordinates") or []
            if len(c) < 2:
                continue
            dist = _haversine_km(lat, lon, float(c[0]), float(c[1]))
            ranked.append((dist, p))
        except (KeyError, TypeError, ValueError):
            continue
    ranked.sort(key=lambda x: x[0])
    nearest = ranked[: max(limit * 2, limit)]  # fetch a bit more, then trim
    ids = [int(p["id"]) for _, p in nearest]
    details = _fetch_details(ids)

    items: list[dict] = []
    for dist, p in nearest:
        pid = int(p["id"])
        point = _point_from_wb(pid, p.get("coordinates") or [], details.get(str(pid)) or details.get(pid))
        point["distance_km"] = round(dist, 2)
        if city:
            c = _normalize_city(city)
            addr = _normalize_city(point.get("address") or "")
            # Prefer matching city in address when details exist; keep by distance otherwise
            if details and c not in addr and addr:
                continue
        items.append(point)
        if len(items) >= limit:
            break

    if not items:
        seeded = _seed_search(city=city, lat=lat, lon=lon, limit=limit)
        return {
            "items": seeded,
            "source": "seed",
            "count": len(seeded),
            "fallback": True,
            "meta": meta,
            "message": "Нет совпадений WB — демо-список",
        }

    return {
        "items": items,
        "source": source,
        "count": len(items),
        "fallback": False,
        "meta": meta,
    }


def get_pvz_by_id(pvz_id: str) -> dict[str, Any] | None:
    if str(pvz_id).startswith("seed-"):
        for p in SEEDED_PVZ:
            if p["id"] == pvz_id:
                return dict(p)
        return None
    try:
        pid = int(pvz_id)
    except ValueError:
        return None
    details = _fetch_details([pid])
    detail = details.get(str(pid)) or details.get(pid)
    if not detail:
        return None
    return _point_from_wb(pid, detail.get("coordinates") or [None, None], detail)

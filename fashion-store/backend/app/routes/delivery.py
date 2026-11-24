from flask import Blueprint, jsonify, request

from app.services.yandex_pvz import search_pvz

bp = Blueprint("delivery", __name__)


@bp.get("/pvz")
def list_pvz():
    """
    GET /api/delivery/pvz?city=Вологда
    GET /api/delivery/pvz?city=Москва
    GET /api/delivery/pvz?lat=59.22&lon=39.89&limit=20

    Primary: Yandex Market ПВЗ (Geosearch / Partner API if keys set, else seed).
    """
    city = (request.args.get("city") or "").strip() or None
    lat_raw = request.args.get("lat")
    lon_raw = request.args.get("lon")
    limit = request.args.get("limit", 20)
    lat = lon = None
    try:
        if lat_raw is not None and lon_raw is not None and lat_raw != "" and lon_raw != "":
            lat = float(lat_raw)
            lon = float(lon_raw)
    except ValueError:
        return jsonify({"error": "invalid_coords"}), 400

    if not city and lat is None:
        return jsonify({"error": "validation_error", "missing": ["city or lat+lon"]}), 400

    result = search_pvz(city=city, lat=lat, lon=lon, limit=int(limit or 20))
    return jsonify(result)

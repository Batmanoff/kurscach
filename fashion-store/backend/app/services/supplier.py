"""
Demo supplier adapter — generates catalog data without scraping.
Swap implementation to call a licensed wholesale API later.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SupplierProduct:
    sku: str
    name: str
    brand: str
    category_slug: str
    price_rub: float
    compare_at: float | None
    description: str
    composition: str
    colors: list[tuple[str, str]]
    sizes: list[str]
    images: list[str]
    tags: list[str]
    featured: bool = False


class DemoSupplierAdapter:
    """Static premium catalog for local/demo use."""

    CATEGORIES = [
        {"slug": "women", "name": "Женщинам", "description": "Новая коллекция", "sort_order": 1},
        {"slug": "men", "name": "Мужчинам", "description": "Минимализм и крой", "sort_order": 2},
        {"slug": "outerwear", "name": "Верхняя одежда", "description": "Пальто и куртки", "sort_order": 3},
        {"slug": "shoes", "name": "Обувь", "description": "Кожа и текстиль", "sort_order": 4},
        {"slug": "accessories", "name": "Аксессуары", "description": "Сумки и детали", "sort_order": 5},
    ]

    def fetch_catalog(self) -> list[SupplierProduct]:
        img = "https://images.unsplash.com/photo-{id}?auto=format&fit=crop&w=900&q=80"
        return [
            SupplierProduct(
                sku="ATL-WOOL-COAT-01",
                name="Шерстяное пальто Avalon",
                brand="ATELIER",
                category_slug="outerwear",
                price_rub=24990,
                compare_at=29990,
                description="Двубортное пальто из итальянской шерсти. Чистый силуэт, мягкая посадка по плечам.",
                composition="80% шерсть, 20% полиамид",
                colors=[("Camel", "#C4A484"), ("Black", "#111111")],
                sizes=["XS", "S", "M", "L"],
                images=[
                    img.format(id="1525506006603-74a6e0aa4a9d"),
                    img.format(id="1483985988355-763728e1935b"),
                ],
                tags=["new", "outerwear"],
                featured=True,
            ),
            SupplierProduct(
                sku="ATL-SILK-BLOUSE-02",
                name="Шёлковая блуза Noir",
                brand="ATELIER",
                category_slug="women",
                price_rub=12990,
                compare_at=None,
                description="Полупрозрачная блуза с мягким воротом. Для вечера и делового гардероба.",
                composition="100% шёлк",
                colors=[("Ivory", "#F5F0E8"), ("Black", "#111111")],
                sizes=["XS", "S", "M", "L"],
                images=[img.format(id="1515372039744-b8f02a3ae446")],
                tags=["women", "evening"],
                featured=True,
            ),
            SupplierProduct(
                sku="ATL-LINEN-TROU-03",
                name="Льняные брюки Coast",
                brand="COS LINE",
                category_slug="women",
                price_rub=8990,
                compare_at=None,
                description="Широкие брюки из плотного льна. Высокая посадка, стрелки по бокам.",
                composition="100% лён",
                colors=[("Sand", "#D2B48C"), ("Olive", "#556B2F")],
                sizes=["S", "M", "L", "XL"],
                images=[img.format(id="1509631179647-0177331693ae")],
                tags=["linen", "summer"],
            ),
            SupplierProduct(
                sku="ATL-MERINO-KNIT-04",
                name="Мериносовый свитер Forma",
                brand="ATELIER",
                category_slug="men",
                price_rub=10990,
                compare_at=13990,
                description="Тонкий свитер из мериноса. Базовый слой для города.",
                composition="100% мериносовая шерсть",
                colors=[("Charcoal", "#36454F"), ("Cream", "#FFFDD0")],
                sizes=["S", "M", "L", "XL"],
                images=[img.format(id="1521572163474-6864f9cf17ab")],
                tags=["men", "knit"],
                featured=True,
            ),
            SupplierProduct(
                sku="ATL-OXFORD-SHIRT-05",
                name="Оксфордская рубашка Line",
                brand="FAR NORTH",
                category_slug="men",
                price_rub=6990,
                compare_at=None,
                description="Классическая рубашка из плотного оксфорда. Крой regular.",
                composition="100% хлопок",
                colors=[("White", "#FFFFFF"), ("Sky", "#87CEEB")],
                sizes=["S", "M", "L", "XL", "XXL"],
                images=[img.format(id="1594938298603-c8148c4dae35")],
                tags=["men", "shirts"],
            ),
            SupplierProduct(
                sku="ATL-LEATHER-BOOT-06",
                name="Кожаные челси Umbra",
                brand="ATELIER",
                category_slug="shoes",
                price_rub=18990,
                compare_at=None,
                description="Челси из гладкой кожи на резиновой подошве. Унисекс.",
                composition="Натуральная кожа",
                colors=[("Black", "#111111"), ("Brown", "#5C4033")],
                sizes=["36", "37", "38", "39", "40", "41", "42", "43", "44"],
                images=[img.format(id="1543163521-1bf539c55dd2")],
                tags=["shoes"],
                featured=True,
            ),
            SupplierProduct(
                sku="ATL-SNEAKER-07",
                name="Кроссовки Silent",
                brand="ASOS EDIT",
                category_slug="shoes",
                price_rub=11990,
                compare_at=14990,
                description="Минималистичные кроссовки на вулканизированной подошве.",
                composition="Кожа / резина",
                colors=[("White", "#F8F8F8"), ("Grey", "#A0A0A0")],
                sizes=["39", "40", "41", "42", "43", "44"],
                images=[img.format(id="1549298916-b41d38311247")],
                tags=["shoes", "sport"],
            ),
            SupplierProduct(
                sku="ATL-TOTE-08",
                name="Кожаная тоут-сумка Arc",
                brand="ATELIER",
                category_slug="accessories",
                price_rub=15990,
                compare_at=None,
                description="Структурированная тоут из зернистой кожи. Внутренний карман на молнии.",
                composition="Натуральная кожа",
                colors=[("Tan", "#D2B48C"), ("Black", "#111111")],
                sizes=["ONE"],
                images=[img.format(id="1590878907165-7f0b5a6b0b0f")],
                tags=["bags"],
            ),
            SupplierProduct(
                sku="ATL-SCARF-09",
                name="Кашемировый шарф Drift",
                brand="COS LINE",
                category_slug="accessories",
                price_rub=7990,
                compare_at=None,
                description="Мягкий шарф из кашемира. Нейтральная палитра сезона.",
                composition="100% кашемир",
                colors=[("Stone", "#928E85"), ("Wine", "#722F37")],
                sizes=["ONE"],
                images=[img.format(id="1520903479872-0c95d0b8b3b0")],
                tags=["accessories"],
            ),
            SupplierProduct(
                sku="ATL-DENIM-10",
                name="Джинсы Straight Raw",
                brand="Z-EDIT",
                category_slug="men",
                price_rub=9990,
                compare_at=None,
                description="Прямые джинсы из нестиранного денима. Высокая плотность ткани.",
                composition="100% хлопок",
                colors=[("Indigo", "#3F00FF")],
                sizes=["28", "30", "32", "34", "36"],
                images=[img.format(id="1542272604-787c3835535d")],
                tags=["denim", "men"],
            ),
            SupplierProduct(
                sku="ATL-DRESS-11",
                name="Платье Column Soft",
                brand="ATELIER",
                category_slug="women",
                price_rub=14990,
                compare_at=17990,
                description="Прямое платье миди из мягкого джерси. Без швов по бокам.",
                composition="65% вискоза, 35% полиэстер",
                colors=[("Black", "#111111"), ("Burgundy", "#800020")],
                sizes=["XS", "S", "M", "L"],
                images=[img.format(id="1496747611176-843222e1e57c")],
                tags=["women", "dresses"],
                featured=True,
            ),
            SupplierProduct(
                sku="ATL-BLAZER-12",
                name="Пиджак Structured Soft",
                brand="FARFETCH LAB",
                category_slug="women",
                price_rub=21990,
                compare_at=None,
                description="Полуприлегающий пиджак с мягкими плечами. На подкладке.",
                composition="Шерсть / вискоза",
                colors=[("Grey", "#808080"), ("Black", "#111111")],
                sizes=["XS", "S", "M", "L"],
                images=[img.format(id="1591362262223-6f0b0c0c0c0a")],
                tags=["women", "tailoring"],
            ),
        ]

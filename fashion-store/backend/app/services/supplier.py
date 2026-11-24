"""
Catalog supplier — sportswear with Unsplash images (Unsplash License).
No brand-CDN scraping. Swap to a licensed wholesale API later if needed.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ColorOption:
    name: str
    hex: str
    image: str


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
    colors: list[ColorOption]
    sizes: list[str]
    images: list[str]
    tags: list[str]
    featured: bool = False


def _u(photo_id: str, w: int = 900) -> str:
    return f"https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&w={w}&q=80"


# Curated Unsplash IDs (sport / street apparel & footwear).
IMG = {
    "hoodie_black": _u("1556821840-3a63f95609a7"),
    "hoodie_grey": _u("1578587011540-6ad66c8a7b2a"),
    "sweat_cream": _u("1620799140408-edc6dcb6d633"),
    "tee_black": _u("1583743814966-8936f5b7be1a"),
    "tee_white": _u("1521572163474-6864f9cf17ab"),
    "tee_signal": _u("1515886657613-9f3515b0c78f"),
    "gym_dark": _u("1517836357463-d25dfeac3438"),
    "athlete": _u("1571019614242-c5c5dee9f50b"),
    "jogger": _u("1552902865-b72c031ac5ea"),
    "outer_orange": _u("1544966503-7cc5ac882d5f"),
    "gym_floor": _u("1576678927484-cc907957088c"),
    "gym_hall": _u("1534438327276-14e5300c3a48"),
    "bomber": _u("1591047139829-d91aecb6caea"),
    "runner": _u("1483721313421-77a8a4d0c6b5"),
    "sneaker_white": _u("1549298916-b41d38311247"),
    "sneaker_court": _u("1606107557195-0e29a4b5b4aa"),
    "sneaker_color": _u("1552346154-21d32810aba3"),
    "trail": _u("1460353581641-37baddab0fa2"),
    "sneaker_pair": _u("1600185365926-3a2ce3cdb9eb"),
    "bag_black": _u("1553062407-98eeb64c6a62"),
    "bag_olive": _u("1547949003-979206a8a00f"),
    "fit_stretch": _u("1518611012118-696072aa579a"),
    "fashion_rack": _u("1483985988355-763728e1935b"),
    "hoodie_flat": _u("1618354691373-d851c5c3a990"),
    "sneaker_box": _u("1556906781-9a412961c28c"),
    "cap_street": _u("1521369909029-2afed882baee"),
    "socks_stack": _u("1586351477863-46921653aaab"),
    "vest_run": _u("1476480862126-209faa56af32"),
    "top_train": _u("1594737625785-a6cbdabd333c"),
    "shorts_run": _u("1461896833970-add300fc39b7"),
}


class DemoSupplierAdapter:
    """Street / sport catalog for the storefront."""

    CATEGORIES = [
        {"slug": "tops", "name": "Верх", "description": "Худи, футболки, лонгсливы", "sort_order": 1},
        {"slug": "bottoms", "name": "Низ", "description": "Джоггеры и шорты", "sort_order": 2},
        {"slug": "outerwear", "name": "Верхняя одежда", "description": "Ветровки и бомберы", "sort_order": 3},
        {"slug": "shoes", "name": "Обувь", "description": "Кроссовки и трейл", "sort_order": 4},
        {"slug": "accessories", "name": "Аксессуары", "description": "Кепки и сумки", "sort_order": 5},
    ]

    def fetch_catalog(self) -> list[SupplierProduct]:
        return [
            SupplierProduct(
                sku="BAST-HOOD-01",
                name="Худи Heavy Volt",
                brand="BAST",
                category_slug="tops",
                price_rub=7990,
                compare_at=9490,
                description="Плотное худи 460 г/м². Спущенное плечо, карман-кенгуру, манжеты в рубчик.",
                composition="80% хлопок, 20% полиэстер",
                colors=[
                    ColorOption("Black", "#111111", IMG["hoodie_black"]),
                    ColorOption("Volt", "#C8FF00", IMG["sweat_cream"]),
                    ColorOption("Grey", "#6B7280", IMG["hoodie_grey"]),
                ],
                sizes=["S", "M", "L", "XL", "XXL"],
                images=[IMG["hoodie_black"]],
                tags=["new", "hoodie"],
                featured=True,
            ),
            SupplierProduct(
                sku="BAST-TEE-02",
                name="Футболка Run Dry",
                brand="BAST",
                category_slug="tops",
                price_rub=2990,
                compare_at=None,
                description="Лёгкая футболка с быстрым отводом влаги. Прямой крой, графика на спине.",
                composition="100% полиэстер (dry-fit)",
                colors=[
                    ColorOption("Black", "#0A0A0A", IMG["tee_black"]),
                    ColorOption("White", "#F5F5F5", IMG["tee_white"]),
                    ColorOption("Signal", "#FF3B00", IMG["tee_signal"]),
                ],
                sizes=["XS", "S", "M", "L", "XL"],
                images=[IMG["tee_black"]],
                tags=["tee", "training"],
                featured=True,
            ),
            SupplierProduct(
                sku="BAST-LS-03",
                name="Лонгслив Grid Mesh",
                brand="NORTH GRID",
                category_slug="tops",
                price_rub=4490,
                compare_at=None,
                description="Сетка на спине и рукавах. Для зала и улицы.",
                composition="92% полиэстер, 8% эластан",
                colors=[
                    ColorOption("Black", "#111111", IMG["gym_dark"]),
                    ColorOption("Navy", "#0B1C2C", IMG["athlete"]),
                ],
                sizes=["S", "M", "L", "XL"],
                images=[IMG["gym_dark"]],
                tags=["training"],
            ),
            SupplierProduct(
                sku="BAST-JOG-04",
                name="Джоггеры Track Taper",
                brand="BAST",
                category_slug="bottoms",
                price_rub=5990,
                compare_at=6990,
                description="Зауженные джоггеры с молниями у щиколотки. Карманы на молнии.",
                composition="65% хлопок, 35% полиэстер",
                colors=[
                    ColorOption("Black", "#111111", IMG["jogger"]),
                    ColorOption("Olive", "#3F4A2F", IMG["outer_orange"]),
                ],
                sizes=["S", "M", "L", "XL"],
                images=[IMG["jogger"]],
                tags=["bottoms"],
                featured=True,
            ),
            SupplierProduct(
                sku="BAST-SHORT-05",
                name="Шорты Sprint 5\"",
                brand="PULSE",
                category_slug="bottoms",
                price_rub=3490,
                compare_at=None,
                description="Лёгкие шорты 5 дюймов. Внутренние шорты, карман для ключей.",
                composition="100% полиэстер",
                colors=[
                    ColorOption("Black", "#111111", IMG["shorts_run"]),
                    ColorOption("Volt", "#C8FF00", IMG["gym_hall"]),
                ],
                sizes=["S", "M", "L", "XL"],
                images=[IMG["shorts_run"]],
                tags=["running"],
            ),
            SupplierProduct(
                sku="BAST-WIND-06",
                name="Ветровка Aero Shell",
                brand="BAST",
                category_slug="outerwear",
                price_rub=9990,
                compare_at=11990,
                description="Лёгкая ветровка с капюшоном. Водоотталкивающая пропитка, пакуется в карман.",
                composition="100% нейлон",
                colors=[
                    ColorOption("Black", "#111111", IMG["bomber"]),
                    ColorOption("Orange", "#FF3B00", IMG["outer_orange"]),
                ],
                sizes=["S", "M", "L", "XL"],
                images=[IMG["bomber"]],
                tags=["outerwear", "new"],
                featured=True,
            ),
            SupplierProduct(
                sku="BAST-BOMB-07",
                name="Бомбер Night Shift",
                brand="VOID RUN",
                category_slug="outerwear",
                price_rub=12990,
                compare_at=None,
                description="Утеплённый бомбер на молнии. Ребристые манжеты, внутренний карман.",
                composition="Полиэстер / подкладка",
                colors=[
                    ColorOption("Black", "#0A0A0A", IMG["bomber"]),
                    ColorOption("Charcoal", "#2A2A2A", IMG["runner"]),
                ],
                sizes=["S", "M", "L", "XL"],
                images=[IMG["bomber"]],
                tags=["outerwear"],
            ),
            SupplierProduct(
                sku="BAST-SNK-08",
                name="Кроссовки Street Pulse",
                brand="PULSE",
                category_slug="shoes",
                price_rub=11990,
                compare_at=13990,
                description="Городские кроссовки на пенной подошве. Сетка + синтетика, цепкий протектор.",
                composition="Текстиль / резина",
                colors=[
                    ColorOption("White", "#F8F8F8", IMG["sneaker_white"]),
                    ColorOption("Black", "#111111", IMG["sneaker_court"]),
                    ColorOption("Volt", "#C8FF00", IMG["sneaker_color"]),
                ],
                sizes=["39", "40", "41", "42", "43", "44", "45"],
                images=[IMG["sneaker_white"]],
                tags=["shoes"],
                featured=True,
            ),
            SupplierProduct(
                sku="BAST-TRAIL-09",
                name="Трейл-кроссовки Ridge",
                brand="NORTH GRID",
                category_slug="shoes",
                price_rub=14990,
                compare_at=None,
                description="Трейл с агрессивным протектором. Защитный носок, шнуровка под петлю.",
                composition="Синтетика / резина",
                colors=[
                    ColorOption("Grey", "#9CA3AF", IMG["trail"]),
                    ColorOption("Orange", "#FF3B00", IMG["sneaker_pair"]),
                ],
                sizes=["40", "41", "42", "43", "44", "45"],
                images=[IMG["trail"]],
                tags=["trail", "shoes"],
            ),
            SupplierProduct(
                sku="BAST-CAP-10",
                name="Кепка Soft Peak",
                brand="BAST",
                category_slug="accessories",
                price_rub=2490,
                compare_at=None,
                description="Шестиклинка с регулировкой. Вышивка логотипа.",
                composition="100% хлопок",
                colors=[
                    ColorOption("Black", "#111111", IMG["cap_street"]),
                    ColorOption("Volt", "#C8FF00", IMG["gym_hall"]),
                ],
                sizes=["ONE"],
                images=[IMG["cap_street"]],
                tags=["cap"],
            ),
            SupplierProduct(
                sku="BAST-SOCK-11",
                name="Носки Crew Triple",
                brand="BAST",
                category_slug="accessories",
                price_rub=1290,
                compare_at=None,
                description="Набор из трёх пар. Усиленная пятка и мысок.",
                composition="80% хлопок, 20% эластан",
                colors=[
                    ColorOption("Black", "#111111", IMG["socks_stack"]),
                    ColorOption("White", "#FFFFFF", IMG["sneaker_box"]),
                ],
                sizes=["ONE"],
                images=[IMG["socks_stack"]],
                tags=["socks"],
            ),
            SupplierProduct(
                sku="BAST-BAG-12",
                name="Сумка Gym Duffel",
                brand="VOID RUN",
                category_slug="accessories",
                price_rub=5490,
                compare_at=6490,
                description="Доффл 35 л. Отделение для обуви, плечевой ремень.",
                composition="Полиэстер 600D",
                colors=[
                    ColorOption("Black", "#111111", IMG["bag_black"]),
                    ColorOption("Olive", "#3F4A2F", IMG["bag_olive"]),
                ],
                sizes=["ONE"],
                images=[IMG["bag_black"]],
                tags=["bag"],
                featured=True,
            ),
            SupplierProduct(
                sku="BAST-TIGHT-13",
                name="Тайтсы Compression Pro",
                brand="PULSE",
                category_slug="bottoms",
                price_rub=4990,
                compare_at=None,
                description="Компрессионные тайтсы до щиколотки. Плоские швы, карман на поясе.",
                composition="78% нейлон, 22% эластан",
                colors=[
                    ColorOption("Black", "#0A0A0A", IMG["fit_stretch"]),
                    ColorOption("Graphite", "#374151", IMG["athlete"]),
                ],
                sizes=["XS", "S", "M", "L", "XL"],
                images=[IMG["fit_stretch"]],
                tags=["training", "compression"],
            ),
            SupplierProduct(
                sku="BAST-VEST-14",
                name="Жилет Packable Heat",
                brand="NORTH GRID",
                category_slug="outerwear",
                price_rub=8990,
                compare_at=None,
                description="Ультралёгкий жилет. Пакуется в карман, подходит под худи.",
                composition="Нейлон / синтетический утеплитель",
                colors=[
                    ColorOption("Black", "#111111", IMG["vest_run"]),
                    ColorOption("Signal", "#FF3B00", IMG["tee_signal"]),
                ],
                sizes=["S", "M", "L", "XL"],
                images=[IMG["vest_run"]],
                tags=["outerwear"],
            ),
            SupplierProduct(
                sku="BAST-BRA-15",
                name="Топ Training Support",
                brand="PULSE",
                category_slug="tops",
                price_rub=3990,
                compare_at=None,
                description="Спортивный топ средней поддержки. Сетка на спине, съёмные чашки.",
                composition="75% нейлон, 25% эластан",
                colors=[
                    ColorOption("Black", "#111111", IMG["top_train"]),
                    ColorOption("White", "#F5F5F5", IMG["athlete"]),
                ],
                sizes=["XS", "S", "M", "L"],
                images=[IMG["top_train"]],
                tags=["training"],
                featured=True,
            ),
            SupplierProduct(
                sku="BAST-CREW-16",
                name="Свитшот Crew Mark",
                brand="BAST",
                category_slug="tops",
                price_rub=6490,
                compare_at=7990,
                description="Классический свитшот без капюшона. Начёс внутри, принт на груди.",
                composition="70% хлопок, 30% полиэстер",
                colors=[
                    ColorOption("Black", "#111111", IMG["hoodie_flat"]),
                    ColorOption("Stone", "#A8A29E", IMG["sweat_cream"]),
                    ColorOption("Navy", "#0B1C2C", IMG["hoodie_grey"]),
                ],
                sizes=["S", "M", "L", "XL"],
                images=[IMG["hoodie_flat"]],
                tags=["crew", "new"],
                featured=True,
            ),
        ]

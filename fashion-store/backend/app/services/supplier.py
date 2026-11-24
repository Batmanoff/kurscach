"""
Catalog supplier — sportswear with licensed stock (Unsplash / Pexels).
No brand-CDN scraping. Coursework uses familiar brand-style product names.
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


def _p(photo_id: int, w: int = 900) -> str:
    return f"https://images.pexels.com/photos/{photo_id}/pexels-photo-{photo_id}.jpeg?auto=compress&cs=tinysrgb&w={w}"


# Verified 200 OK stock (sport / apparel / footwear).
IMG = {
    "hoodie_black": _u("1556821840-3a63f95609a7"),
    "hoodie_flat": _u("1618354691373-d851c5c3a990"),
    "sweat": _u("1620799140408-edc6dcb6d633"),
    "tee_black": _u("1583743814966-8936f5b7be1a"),
    "tee_white": _u("1521572163474-6864f9cf17ab"),
    "tee_signal": _u("1515886657613-9f3515b0c78f"),
    "gym": _u("1517836357463-d25dfeac3438"),
    "athlete": _u("1571019614242-c5c5dee9f50b"),
    "jogger": _u("1552902865-b72c031ac5ea"),
    "bomber": _u("1591047139829-d91aecb6caea"),
    "sneaker_red": _u("1542291026-7eec264c27ff"),
    "sneaker_court": _u("1606107557195-0e29a4b5b4aa"),
    "sneaker_color": _u("1552346154-21d32810aba3"),
    "trail": _u("1460353581641-37baddab0fa2"),
    "sneaker_pair": _u("1600185365926-3a2ce3cdb9eb"),
    "sneaker_classic": _u("1560769629-975ec94e6a86"),
    "bag": _u("1553062407-98eeb64c6a62"),
    "fit": _u("1518611012118-696072aa579a"),
    "rack": _u("1483985988355-763728e1935b"),
    "kitchen_sneaker": _u("1556906781-9a412961c28c"),
    "cap": _u("1521369909029-2afed882baee"),
    "top": _u("1594737625785-a6cbdabd333c"),
    "gym_hall": _u("1534438327276-14e5300c3a48"),
    "weights": _u("1576678927484-cc907957088c"),
    "clothes": _u("1523381210434-271e8be1f52b"),
    "kettle": _u("1556909114-f6e7ad7d3136"),
    "run_track": _u("1571902943202-507ec2618e8f"),
    "pex_sneaker1": _p(2529148),
    "pex_sneaker2": _p(1598505),
    "pex_sneaker3": _p(1478442),
    "pex_train": _p(2294361),
    "pex_yoga": _p(3757376),
    "pex_run": _p(416778),
    "pex_hoodie": _p(6858618),
    "pex_street": _p(7671166),
    "pex_tee": _p(6311392),
    "pex_pants": _p(6311650),
    "pex_jacket": _p(6311575),
    "pex_shorts": _p(6311387),
    "pex_bra": _p(3757942),
    "pex_bag": _p(4753986),
    "pex_gym": _p(2827400),
    "pex_cap": _p(1124468),
}


class DemoSupplierAdapter:
    """Street / sport catalog for Swaga."""

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
                sku="SWG-NK-HOOD-01",
                name="Nike Sportswear Club Fleece Hoodie",
                brand="Nike",
                category_slug="tops",
                price_rub=8990,
                compare_at=10990,
                description="Плотное худи с капюшоном и карманом-кенгуру. Мягкий флис, прямой крой.",
                composition="80% хлопок, 20% полиэстер",
                colors=[
                    ColorOption("Black", "#111111", IMG["hoodie_black"]),
                    ColorOption("Grey", "#6B7280", IMG["pex_hoodie"]),
                    ColorOption("Volt", "#C8FF00", IMG["sweat"]),
                ],
                sizes=["S", "M", "L", "XL", "XXL"],
                images=[IMG["hoodie_black"]],
                tags=["new", "hoodie"],
                featured=True,
            ),
            SupplierProduct(
                sku="SWG-AD-TEE-02",
                name="Adidas Essentials 3-Stripes Tee",
                brand="Adidas",
                category_slug="tops",
                price_rub=3490,
                compare_at=None,
                description="Классическая футболка с тремя полосками. Лёгкий хлопок, повседневный крой.",
                composition="100% хлопок",
                colors=[
                    ColorOption("Black", "#0A0A0A", IMG["tee_black"]),
                    ColorOption("White", "#F5F5F5", IMG["tee_white"]),
                    ColorOption("Signal", "#FF3B00", IMG["tee_signal"]),
                ],
                sizes=["XS", "S", "M", "L", "XL"],
                images=[IMG["tee_black"]],
                tags=["tee"],
                featured=True,
            ),
            SupplierProduct(
                sku="SWG-PU-LS-03",
                name="Puma Train Cloudspun Longsleeve",
                brand="Puma",
                category_slug="tops",
                price_rub=4990,
                compare_at=None,
                description="Тренировочный лонгслив с мягкой посадкой. Для зала и улицы.",
                composition="92% полиэстер, 8% эластан",
                colors=[
                    ColorOption("Black", "#111111", IMG["gym"]),
                    ColorOption("Navy", "#0B1C2C", IMG["athlete"]),
                ],
                sizes=["S", "M", "L", "XL"],
                images=[IMG["gym"]],
                tags=["training"],
            ),
            SupplierProduct(
                sku="SWG-NK-JOG-04",
                name="Nike Tech Fleece Joggers",
                brand="Nike",
                category_slug="bottoms",
                price_rub=7990,
                compare_at=9490,
                description="Зауженные джоггеры Tech Fleece. Карманы на молнии, манжеты.",
                composition="68% хлопок, 32% полиэстер",
                colors=[
                    ColorOption("Black", "#111111", IMG["jogger"]),
                    ColorOption("Grey", "#4B5563", IMG["pex_pants"]),
                ],
                sizes=["S", "M", "L", "XL"],
                images=[IMG["jogger"]],
                tags=["bottoms"],
                featured=True,
            ),
            SupplierProduct(
                sku="SWG-AD-SHORT-05",
                name="Adidas Own the Run Shorts",
                brand="Adidas",
                category_slug="bottoms",
                price_rub=3990,
                compare_at=None,
                description="Беговые шорты с внутренними шортами и карманом на поясе.",
                composition="100% полиэстер",
                colors=[
                    ColorOption("Black", "#111111", IMG["pex_shorts"]),
                    ColorOption("Blue", "#1D4ED8", IMG["run_track"]),
                ],
                sizes=["S", "M", "L", "XL"],
                images=[IMG["pex_shorts"]],
                tags=["running"],
            ),
            SupplierProduct(
                sku="SWG-NB-WIND-06",
                name="New Balance Athletics Windbreaker",
                brand="New Balance",
                category_slug="outerwear",
                price_rub=10990,
                compare_at=12990,
                description="Лёгкая ветровка с капюшоном. Водоотталкивающая ткань, пакуется в карман.",
                composition="100% нейлон",
                colors=[
                    ColorOption("Black", "#111111", IMG["bomber"]),
                    ColorOption("Orange", "#FF3B00", IMG["pex_jacket"]),
                ],
                sizes=["S", "M", "L", "XL"],
                images=[IMG["bomber"]],
                tags=["outerwear", "new"],
                featured=True,
            ),
            SupplierProduct(
                sku="SWG-PU-BOMB-07",
                name="Puma T7 Track Jacket",
                brand="Puma",
                category_slug="outerwear",
                price_rub=11990,
                compare_at=None,
                description="Классический track-jacket T7. Молния по центру, контрастные полосы.",
                composition="Полиэстер / подкладка",
                colors=[
                    ColorOption("Black", "#0A0A0A", IMG["pex_street"]),
                    ColorOption("Red", "#B91C1C", IMG["pex_jacket"]),
                ],
                sizes=["S", "M", "L", "XL"],
                images=[IMG["pex_street"]],
                tags=["outerwear"],
            ),
            SupplierProduct(
                sku="SWG-NK-SNK-08",
                name="Nike Air Zoom Pegasus 41",
                brand="Nike",
                category_slug="shoes",
                price_rub=14990,
                compare_at=16990,
                description="Ежедневные беговые кроссовки с пеной React и Zoom Air.",
                composition="Текстиль / резина",
                colors=[
                    ColorOption("Black", "#111111", IMG["sneaker_court"]),
                    ColorOption("White", "#F8F8F8", IMG["pex_sneaker1"]),
                    ColorOption("Volt", "#C8FF00", IMG["sneaker_color"]),
                ],
                sizes=["39", "40", "41", "42", "43", "44", "45"],
                images=[IMG["sneaker_court"]],
                tags=["shoes", "running"],
                featured=True,
            ),
            SupplierProduct(
                sku="SWG-AD-UB-09",
                name="Adidas Ultraboost 5",
                brand="Adidas",
                category_slug="shoes",
                price_rub=18990,
                compare_at=None,
                description="Амортизация Boost и верх из Primeknit. Для города и длинных пробежек.",
                composition="Текстиль / резина",
                colors=[
                    ColorOption("Black", "#111111", IMG["pex_sneaker2"]),
                    ColorOption("Grey", "#9CA3AF", IMG["trail"]),
                ],
                sizes=["40", "41", "42", "43", "44", "45"],
                images=[IMG["pex_sneaker2"]],
                tags=["shoes"],
            ),
            SupplierProduct(
                sku="SWG-NB-574-10",
                name="New Balance 574 Core",
                brand="New Balance",
                category_slug="shoes",
                price_rub=12990,
                compare_at=14990,
                description="Классика 574 с замшей и сеткой. Комфортная колодка ENCAP.",
                composition="Замша / текстиль / резина",
                colors=[
                    ColorOption("Grey", "#9CA3AF", IMG["sneaker_classic"]),
                    ColorOption("Navy", "#0B1C2C", IMG["pex_sneaker3"]),
                    ColorOption("Red", "#B91C1C", IMG["sneaker_red"]),
                ],
                sizes=["40", "41", "42", "43", "44", "45"],
                images=[IMG["sneaker_classic"]],
                tags=["shoes", "lifestyle"],
                featured=True,
            ),
            SupplierProduct(
                sku="SWG-PU-RSX-11",
                name="Puma RS-X Efekt",
                brand="Puma",
                category_slug="shoes",
                price_rub=11990,
                compare_at=None,
                description="Массивная подошва RS и сетчатый верх. Акцент на street-силуэт.",
                composition="Текстиль / синтетика / резина",
                colors=[
                    ColorOption("White", "#F8F8F8", IMG["sneaker_pair"]),
                    ColorOption("Black", "#111111", IMG["kitchen_sneaker"]),
                ],
                sizes=["40", "41", "42", "43", "44"],
                images=[IMG["sneaker_pair"]],
                tags=["shoes"],
            ),
            SupplierProduct(
                sku="SWG-NK-CAP-12",
                name="Nike Heritage86 Cap",
                brand="Nike",
                category_slug="accessories",
                price_rub=2490,
                compare_at=None,
                description="Шестиклинка с регулируемой застёжкой и вышитым логотипом.",
                composition="100% хлопок",
                colors=[
                    ColorOption("Black", "#111111", IMG["cap"]),
                    ColorOption("White", "#F5F5F5", IMG["pex_cap"]),
                ],
                sizes=["ONE"],
                images=[IMG["cap"]],
                tags=["cap"],
            ),
            SupplierProduct(
                sku="SWG-AD-BAG-13",
                name="Adidas Essentials Duffel Bag",
                brand="Adidas",
                category_slug="accessories",
                price_rub=5490,
                compare_at=6490,
                description="Доффл для зала. Отделение для обуви, регулируемый ремень.",
                composition="Полиэстер 600D",
                colors=[
                    ColorOption("Black", "#111111", IMG["bag"]),
                    ColorOption("Navy", "#0B1C2C", IMG["pex_bag"]),
                ],
                sizes=["ONE"],
                images=[IMG["bag"]],
                tags=["bag"],
                featured=True,
            ),
            SupplierProduct(
                sku="SWG-NK-TIGHT-14",
                name="Nike Pro Dri-FIT Tights",
                brand="Nike",
                category_slug="bottoms",
                price_rub=5490,
                compare_at=None,
                description="Компрессионные тайтсы Pro. Плоские швы, карман на поясе.",
                composition="78% нейлон, 22% эластан",
                colors=[
                    ColorOption("Black", "#0A0A0A", IMG["fit"]),
                    ColorOption("Graphite", "#374151", IMG["pex_yoga"]),
                ],
                sizes=["XS", "S", "M", "L", "XL"],
                images=[IMG["fit"]],
                tags=["training"],
            ),
            SupplierProduct(
                sku="SWG-AD-BRA-15",
                name="Adidas Training Medium Support Bra",
                brand="Adidas",
                category_slug="tops",
                price_rub=4290,
                compare_at=None,
                description="Топ средней поддержки. Сетка и плоские швы для тренировок.",
                composition="75% нейлон, 25% эластан",
                colors=[
                    ColorOption("Black", "#111111", IMG["top"]),
                    ColorOption("Pink", "#F472B6", IMG["pex_bra"]),
                ],
                sizes=["XS", "S", "M", "L"],
                images=[IMG["top"]],
                tags=["training"],
                featured=True,
            ),
            SupplierProduct(
                sku="SWG-NB-CREW-16",
                name="New Balance Athletics Crew Sweatshirt",
                brand="New Balance",
                category_slug="tops",
                price_rub=6990,
                compare_at=8490,
                description="Свитшот без капюшона с начёсом. Принт Athletics на груди.",
                composition="70% хлопок, 30% полиэстер",
                colors=[
                    ColorOption("Black", "#111111", IMG["hoodie_flat"]),
                    ColorOption("Stone", "#A8A29E", IMG["sweat"]),
                    ColorOption("Navy", "#0B1C2C", IMG["pex_tee"]),
                ],
                sizes=["S", "M", "L", "XL"],
                images=[IMG["hoodie_flat"]],
                tags=["crew", "new"],
                featured=True,
            ),
            SupplierProduct(
                sku="SWG-OW-LACE-17",
                name="Off-White Arrow Shoelaces",
                brand="Off-White",
                category_slug="accessories",
                price_rub=4990,
                compare_at=5990,
                description="Плоские шнурки с фирменной стрелкой. Подходят для большинства кроссовок, длина 140 см.",
                composition="100% полиэстер",
                colors=[
                    ColorOption(
                        "White",
                        "#F5F5F5",
                        "/static/img/off-white-shoelaces.png",
                    ),
                    ColorOption(
                        "Black",
                        "#111111",
                        "/static/img/off-white-shoelaces.png",
                    ),
                ],
                sizes=["140cm"],
                images=["/static/img/off-white-shoelaces.png"],
                tags=["laces", "accessories", "easter_snurki"],
                featured=True,
            ),
        ]

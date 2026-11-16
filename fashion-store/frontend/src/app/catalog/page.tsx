"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { ProductCard } from "@/components/ProductCard";
import { api, type Product } from "@/lib/api";

export default function CatalogPage() {
  const params = useSearchParams();
  const [items, setItems] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Array<{ slug: string; name: string }>>([]);
  const [q, setQ] = useState("");
  const [sort, setSort] = useState("newest");
  const category = params.get("category") || "";

  useEffect(() => {
    api.categories().then((r) => setCategories(r.items)).catch(() => undefined);
  }, []);

  useEffect(() => {
    api
      .products({ category: category || undefined, q: q || undefined, sort, per_page: 48 })
      .then((r) => setItems(r.items))
      .catch(() => setItems([]));
  }, [category, q, sort]);

  return (
    <div className="container-page py-12">
      <div className="mb-10 flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-[11px] uppercase tracking-[0.2em] text-muted">Каталог</p>
          <h1 className="mt-2 font-display text-4xl">Вся коллекция</h1>
        </div>
        <div className="flex flex-wrap gap-3">
          <input
            className="input max-w-xs"
            placeholder="Поиск"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
          <select className="input max-w-[180px]" value={sort} onChange={(e) => setSort(e.target.value)}>
            <option value="newest">Новинки</option>
            <option value="price_asc">Цена ↑</option>
            <option value="price_desc">Цена ↓</option>
          </select>
        </div>
      </div>

      <div className="mb-8 flex flex-wrap gap-3">
        <a
          href="/catalog"
          className={`text-[11px] uppercase tracking-[0.16em] ${!category ? "text-ink" : "text-muted"}`}
        >
          Все
        </a>
        {categories.map((c) => (
          <a
            key={c.slug}
            href={`/catalog?category=${c.slug}`}
            className={`text-[11px] uppercase tracking-[0.16em] ${
              category === c.slug ? "text-ink" : "text-muted"
            }`}
          >
            {c.name}
          </a>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-x-5 gap-y-10 md:grid-cols-3 lg:grid-cols-4">
        {items.map((p, i) => (
          <ProductCard key={p.id} product={p} index={i} />
        ))}
      </div>
      {!items.length && <p className="py-20 text-center text-muted">Товары не найдены</p>}
    </div>
  );
}

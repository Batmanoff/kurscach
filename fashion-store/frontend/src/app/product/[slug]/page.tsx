"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { api, formatRub, type Product } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function ProductPage() {
  const { slug } = useParams<{ slug: string }>();
  const { token } = useAuth();
  const router = useRouter();
  const [product, setProduct] = useState<Product | null>(null);
  const [color, setColor] = useState<string>("");
  const [size, setSize] = useState<string>("");
  const [msg, setMsg] = useState("");

  useEffect(() => {
    if (!slug) return;
    api.product(slug).then((r) => {
      setProduct(r.product);
      const first = r.product.variants?.[0];
      if (first) {
        setColor(first.color);
        setSize(first.size);
      }
    });
  }, [slug]);

  const colors = useMemo(
    () => Array.from(new Set((product?.variants || []).map((v) => v.color))),
    [product]
  );
  const sizes = useMemo(
    () =>
      Array.from(
        new Set((product?.variants || []).filter((v) => v.color === color).map((v) => v.size))
      ),
    [product, color]
  );
  const variant = product?.variants?.find((v) => v.color === color && v.size === size);

  async function addToCart() {
    if (!token) {
      router.push("/login");
      return;
    }
    if (!variant) return;
    try {
      await api.addToCart(token, variant.id, 1);
      setMsg("Добавлено в корзину");
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "Ошибка");
    }
  }

  async function toggleFav() {
    if (!token || !product) {
      router.push("/login");
      return;
    }
    try {
      await api.addFavorite(token, product.id);
      setMsg("В избранном");
    } catch (e) {
      setMsg(e instanceof Error ? e.message : "Ошибка");
    }
  }

  if (!product) {
    return <div className="container-page py-20 text-muted">Загрузка…</div>;
  }

  return (
    <div className="container-page grid gap-10 py-12 lg:grid-cols-2">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="aspect-[3/4] overflow-hidden bg-mist"
      >
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={product.images?.[0]}
          alt={product.name}
          className="h-full w-full object-cover"
        />
      </motion.div>
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
        <p className="text-[11px] uppercase tracking-[0.2em] text-muted">{product.brand}</p>
        <h1 className="mt-3 font-display text-4xl">{product.name}</h1>
        <p className="mt-4 text-lg">{formatRub(variant?.price_rub ?? product.base_price_rub)}</p>
        <p className="mt-6 max-w-lg text-sm leading-relaxed text-muted">{product.description}</p>
        {product.composition && (
          <p className="mt-4 text-xs uppercase tracking-[0.14em] text-muted">
            Состав: {product.composition}
          </p>
        )}

        <div className="mt-8">
          <p className="label">Цвет</p>
          <div className="flex flex-wrap gap-2">
            {colors.map((c) => (
              <button
                key={c}
                onClick={() => setColor(c)}
                className={`border px-3 py-2 text-xs ${color === c ? "border-ink" : "border-ink/20"}`}
              >
                {c}
              </button>
            ))}
          </div>
        </div>

        <div className="mt-6">
          <p className="label">Размер</p>
          <div className="flex flex-wrap gap-2">
            {sizes.map((s) => (
              <button
                key={s}
                onClick={() => setSize(s)}
                className={`min-w-12 border px-3 py-2 text-xs ${size === s ? "border-ink bg-ink text-paper" : "border-ink/20"}`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        <p className="mt-4 text-xs text-muted">
          {variant?.in_stock ? `В наличии: ${variant.stock}` : "Нет в наличии"}
        </p>

        <div className="mt-8 flex flex-wrap gap-3">
          <button className="btn" onClick={addToCart} disabled={!variant?.in_stock}>
            В корзину
          </button>
          <button className="btn-outline" onClick={toggleFav}>
            В избранное
          </button>
        </div>
        {msg && <p className="mt-4 text-sm text-accent">{msg}</p>}
      </motion.div>
    </div>
  );
}

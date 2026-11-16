"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { ProductCard } from "@/components/ProductCard";
import { api, type Product } from "@/lib/api";

export default function HomePage() {
  const [featured, setFeatured] = useState<Product[]>([]);

  useEffect(() => {
    api.products({ featured: 1, per_page: 8 }).then((r) => setFeatured(r.items)).catch(() => setFeatured([]));
  }, []);

  return (
    <>
      <section className="relative min-h-[88vh] overflow-hidden">
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage:
              "linear-gradient(90deg, rgba(20,20,20,0.55), rgba(20,20,20,0.15)), url(https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=1800&q=80)",
          }}
        />
        <div className="container-page relative flex min-h-[88vh] flex-col justify-end pb-20 pt-32 text-paper">
          <motion.p
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="font-display text-5xl tracking-brand md:text-7xl"
          >
            ATELIER
          </motion.p>
          <motion.h1
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.1 }}
            className="mt-6 max-w-xl font-display text-3xl font-medium leading-tight md:text-5xl"
          >
            Сезон тишины и точного кроя
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="mt-5 max-w-md text-sm text-paper/80"
          >
            Минималистичная коллекция для города. Оплата СБП через ЮKassa.
          </motion.p>
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.3 }}
            className="mt-10 flex flex-wrap gap-4"
          >
            <Link href="/catalog" className="btn border-paper bg-paper text-ink hover:bg-transparent hover:text-paper">
              Смотреть каталог
            </Link>
            <Link href="/catalog?category=outerwear" className="btn-outline border-paper/50 text-paper hover:bg-paper hover:text-ink">
              Верхняя одежда
            </Link>
          </motion.div>
        </div>
      </section>

      <section className="container-page py-20">
        <div className="mb-10 flex items-end justify-between gap-4">
          <div>
            <p className="text-[11px] uppercase tracking-[0.2em] text-muted">Избранное</p>
            <h2 className="mt-2 font-display text-3xl md:text-4xl">Новая подборка</h2>
          </div>
          <Link href="/catalog" className="text-[11px] uppercase tracking-[0.18em] text-muted hover:text-ink">
            Весь каталог
          </Link>
        </div>
        <div className="grid grid-cols-2 gap-x-5 gap-y-10 md:grid-cols-4">
          {featured.map((p, i) => (
            <ProductCard key={p.id} product={p} index={i} />
          ))}
        </div>
      </section>
    </>
  );
}

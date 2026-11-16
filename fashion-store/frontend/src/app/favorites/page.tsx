"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ProductCard } from "@/components/ProductCard";
import { api, type Product } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function FavoritesPage() {
  const { token, loading } = useAuth();
  const router = useRouter();
  const [items, setItems] = useState<Product[]>([]);

  useEffect(() => {
    if (loading) return;
    if (!token) {
      router.push("/login");
      return;
    }
    api
      .favorites(token)
      .then((r) => setItems(r.items.map((i) => i.product).filter(Boolean)))
      .catch(() => setItems([]));
  }, [token, loading, router]);

  return (
    <div className="container-page py-12">
      <h1 className="font-display text-4xl">Избранное</h1>
      <div className="mt-10 grid grid-cols-2 gap-x-5 gap-y-10 md:grid-cols-4">
        {items.map((p, i) => (
          <ProductCard key={p.id} product={p} index={i} />
        ))}
      </div>
      {!items.length && <p className="mt-10 text-muted">Пока пусто</p>}
    </div>
  );
}

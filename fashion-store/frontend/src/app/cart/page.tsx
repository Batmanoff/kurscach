"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, formatRub, type Cart } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function CartPage() {
  const { token, loading } = useAuth();
  const router = useRouter();
  const [cart, setCart] = useState<Cart | null>(null);

  useEffect(() => {
    if (loading) return;
    if (!token) {
      router.push("/login");
      return;
    }
    api.cart(token).then((r) => setCart(r.cart)).catch(() => setCart(null));
  }, [token, loading, router]);

  async function updateQty(itemId: number, quantity: number) {
    if (!token) return;
    const r = await api.updateCartItem(token, itemId, quantity);
    setCart(r.cart);
  }

  if (!cart) return <div className="container-page py-20 text-muted">Загрузка корзины…</div>;

  return (
    <div className="container-page py-12">
      <h1 className="font-display text-4xl">Корзина</h1>
      {!cart.items.length ? (
        <p className="mt-8 text-muted">
          Пусто. <Link href="/catalog">Перейти в каталог</Link>
        </p>
      ) : (
        <div className="mt-10 grid gap-10 lg:grid-cols-[1fr_320px]">
          <div className="space-y-6">
            {cart.items.map((item) => (
              <div key={item.id} className="flex gap-5 border-b border-ink/10 pb-6">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={item.product.images?.[0]}
                  alt={item.product.name}
                  className="h-28 w-24 object-cover bg-mist"
                />
                <div className="flex-1">
                  <p className="text-[10px] uppercase tracking-[0.18em] text-muted">{item.product.brand}</p>
                  <Link href={`/product/${item.product.slug}`} className="mt-1 block text-sm">
                    {item.product.name}
                  </Link>
                  <p className="mt-1 text-xs text-muted">
                    {item.variant.color} · {item.variant.size}
                  </p>
                  <div className="mt-3 flex items-center gap-3">
                    <button className="btn-outline !px-3 !py-1" onClick={() => updateQty(item.id, item.quantity - 1)}>
                      −
                    </button>
                    <span className="text-sm">{item.quantity}</span>
                    <button className="btn-outline !px-3 !py-1" onClick={() => updateQty(item.id, item.quantity + 1)}>
                      +
                    </button>
                  </div>
                </div>
                <p className="text-sm">{formatRub(item.line_total_rub)}</p>
              </div>
            ))}
          </div>
          <aside className="h-fit border border-ink/10 bg-white/50 p-6">
            <p className="text-[11px] uppercase tracking-[0.18em] text-muted">Итого</p>
            <p className="mt-3 font-display text-3xl">{formatRub(cart.subtotal_rub)}</p>
            <Link href="/checkout" className="btn mt-6 w-full">
              Оформить
            </Link>
          </aside>
        </div>
      )}
    </div>
  );
}

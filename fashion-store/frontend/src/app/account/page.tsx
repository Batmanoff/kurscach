"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, formatRub, type Order } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function AccountPage() {
  const { user, token, loading } = useAuth();
  const router = useRouter();
  const [orders, setOrders] = useState<Order[]>([]);

  useEffect(() => {
    if (loading) return;
    if (!token) {
      router.push("/login");
      return;
    }
    api.myOrders(token).then((r) => setOrders(r.items)).catch(() => setOrders([]));
  }, [token, loading, router]);

  if (!user) return <div className="container-page py-20 text-muted">Загрузка…</div>;

  return (
    <div className="container-page py-12">
      <h1 className="font-display text-4xl">Кабинет</h1>
      <p className="mt-3 text-sm text-muted">
        {user.full_name} · {user.email} · {user.role}
      </p>
      <h2 className="mt-12 text-[11px] uppercase tracking-[0.2em]">Заказы</h2>
      <div className="mt-6 space-y-4">
        {orders.map((o) => (
          <div key={o.public_id} className="border border-ink/10 bg-white/40 p-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <p className="text-sm">{o.public_id.slice(0, 8)}</p>
              <p className="text-xs uppercase tracking-[0.14em] text-muted">{o.status}</p>
            </div>
            <p className="mt-2 text-sm">{formatRub(o.total_rub)}</p>
            <ul className="mt-3 space-y-1 text-xs text-muted">
              {o.items.map((i) => (
                <li key={i.id}>
                  {i.product_name} · {i.size}/{i.color} × {i.quantity}
                </li>
              ))}
            </ul>
          </div>
        ))}
        {!orders.length && <p className="text-muted">Заказов пока нет</p>}
      </div>
    </div>
  );
}

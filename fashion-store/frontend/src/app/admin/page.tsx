"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, formatRub, type Order, type Product } from "@/lib/api";
import { useAuth } from "@/lib/auth";

const STATUSES = [
  "pending_payment",
  "paid",
  "processing",
  "shipped",
  "delivered",
  "cancelled",
  "refunded",
];

export default function AdminPage() {
  const { user, token, loading } = useAuth();
  const router = useRouter();
  const [dash, setDash] = useState<Record<string, unknown> | null>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const [products, setProducts] = useState<Product[]>([]);

  useEffect(() => {
    if (loading) return;
    if (!token || user?.role !== "admin") {
      router.push("/login");
      return;
    }
    Promise.all([api.adminDashboard(token), api.adminOrders(token), api.adminProducts(token)]).then(
      ([d, o, p]) => {
        setDash(d);
        setOrders(o.items);
        setProducts(p.items);
      }
    );
  }, [token, user, loading, router]);

  async function setStatus(publicId: string, status: string) {
    if (!token) return;
    const r = await api.adminUpdateOrder(token, publicId, status);
    setOrders((prev) => prev.map((o) => (o.public_id === publicId ? r.order : o)));
  }

  if (!dash) return <div className="container-page py-20 text-muted">Админ-панель…</div>;

  return (
    <div className="container-page py-12">
      <h1 className="font-display text-4xl">Admin</h1>
      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          ["Пользователи", dash.users],
          ["Товары", dash.products],
          ["Заказы", dash.orders],
          ["Выручка ₽", formatRub(Number(dash.revenue_paid_rub || 0))],
        ].map(([label, value]) => (
          <div key={String(label)} className="border border-ink/10 bg-white/50 p-5">
            <p className="text-[11px] uppercase tracking-[0.16em] text-muted">{label}</p>
            <p className="mt-2 font-display text-3xl">{String(value)}</p>
          </div>
        ))}
      </div>

      <h2 className="mt-14 text-[11px] uppercase tracking-[0.2em]">Заказы</h2>
      <div className="mt-4 space-y-3">
        {orders.map((o) => (
          <div key={o.public_id} className="flex flex-wrap items-center justify-between gap-3 border border-ink/10 p-4">
            <div>
              <p className="text-sm">{o.public_id.slice(0, 8)} · {formatRub(o.total_rub)}</p>
              <p className="text-xs text-muted">{o.shipping.name} · {o.shipping.city}</p>
            </div>
            <select
              className="input max-w-[200px]"
              value={o.status}
              onChange={(e) => setStatus(o.public_id, e.target.value)}
            >
              {STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
        ))}
      </div>

      <h2 className="mt-14 text-[11px] uppercase tracking-[0.2em]">Товары ({products.length})</h2>
      <div className="mt-4 overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="text-[11px] uppercase tracking-[0.14em] text-muted">
            <tr>
              <th className="py-2">Название</th>
              <th>Бренд</th>
              <th>Цена</th>
              <th>SKU</th>
            </tr>
          </thead>
          <tbody>
            {products.map((p) => (
              <tr key={p.id} className="border-t border-ink/10">
                <td className="py-3">{p.name}</td>
                <td>{p.brand}</td>
                <td>{formatRub(p.base_price_rub)}</td>
                <td className="text-xs text-muted">{p.variants?.[0]?.sku || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";

export default function CheckoutSuccessPage() {
  const params = useSearchParams();
  const order = params.get("order");

  return (
    <div className="container-page py-24 text-center">
      <p className="text-[11px] uppercase tracking-[0.2em] text-muted">Оплата</p>
      <h1 className="mt-3 font-display text-4xl">Заказ принят</h1>
      {order && <p className="mt-4 text-sm text-muted">Номер: {order}</p>}
      <p className="mx-auto mt-4 max-w-md text-sm text-muted">
        Как только ЮKassa (или mock) подтвердит платёж, статус станет paid.
      </p>
      <div className="mt-10 flex justify-center gap-4">
        <Link href="/account" className="btn">
          Мои заказы
        </Link>
        <Link href="/catalog" className="btn-outline">
          В каталог
        </Link>
      </div>
    </div>
  );
}

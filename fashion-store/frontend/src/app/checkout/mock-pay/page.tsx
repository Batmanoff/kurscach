"use client";

import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function MockPayPage() {
  const params = useSearchParams();
  const { token } = useAuth();
  const order = params.get("order") || "";
  const payment = params.get("payment") || "";
  const ret = params.get("return") || "/checkout/success";
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");

  async function confirm() {
    if (!token || !payment) {
      setError("Нужна авторизация");
      return;
    }
    try {
      await api.mockConfirm(token, payment);
      setDone(true);
      window.location.href = `${ret}${ret.includes("?") ? "&" : "?"}order=${order}`;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка");
    }
  }

  return (
    <div className="container-page max-w-lg py-20">
      <p className="text-[11px] uppercase tracking-[0.2em] text-muted">Mock bank app</p>
      <h1 className="mt-3 font-display text-4xl">СБП (тестовый режим)</h1>
      <p className="mt-4 text-sm text-muted">
        Ключи ЮKassa не заданы. Это имитация банковского приложения для локальной разработки.
      </p>
      <p className="mt-6 text-xs">Order: {order}</p>
      <p className="text-xs">Payment: {payment}</p>
      {error && <p className="mt-4 text-sm text-red-700">{error}</p>}
      <button className="btn mt-8 w-full" onClick={confirm} disabled={done}>
        Подтвердить оплату
      </button>
      <Link href="/checkout" className="btn-outline mt-3 block w-full text-center">
        Назад
      </Link>
    </div>
  );
}

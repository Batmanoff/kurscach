"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { QRCodeSVG } from "qrcode.react";
import { api, formatRub, type Payment } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function CheckoutPage() {
  const { token, user, loading } = useAuth();
  const router = useRouter();
  const [payment, setPayment] = useState<Payment | null>(null);
  const [orderId, setOrderId] = useState("");
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    shipping_name: "",
    shipping_phone: "+7",
    shipping_city: "Москва",
    shipping_address: "",
    shipping_postal: "",
    coupon_code: "WELCOME10",
  });

  useEffect(() => {
    if (loading) return;
    if (!token) router.push("/login");
    if (user?.full_name) setForm((f) => ({ ...f, shipping_name: user.full_name }));
  }, [token, loading, router, user]);

  useEffect(() => {
    if (!token || !payment?.provider_payment_id || payment.status === "succeeded") return;
    const id = setInterval(async () => {
      try {
        const r = await api.paymentStatus(token, payment.provider_payment_id);
        setStatus(r.order_status);
        setPayment(r.payment);
        if (r.order_status === "paid" || r.payment.status === "succeeded") {
          router.push(`/checkout/success?order=${orderId}`);
        }
      } catch {
        /* ignore poll errors */
      }
    }, 3000);
    return () => clearInterval(id);
  }, [token, payment, orderId, router]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (!token) return;
    setError("");
    try {
      const { order } = await api.createOrder(token, form);
      setOrderId(order.public_id);
      const pay = await api.payOrder(token, order.public_id);
      setPayment(pay.payment);
      setStatus(pay.order.status);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка оформления");
    }
  }

  return (
    <div className="container-page py-12">
      <h1 className="font-display text-4xl">Оформление</h1>
      {!payment ? (
        <form onSubmit={onSubmit} className="mt-10 grid max-w-xl gap-4">
          {(
            [
              ["shipping_name", "Получатель"],
              ["shipping_phone", "Телефон"],
              ["shipping_city", "Город"],
              ["shipping_address", "Адрес"],
              ["shipping_postal", "Индекс"],
              ["coupon_code", "Промокод"],
            ] as const
          ).map(([key, label]) => (
            <div key={key}>
              <label className="label">{label}</label>
              <input
                className="input"
                value={form[key]}
                onChange={(e) => setForm({ ...form, [key]: e.target.value })}
                required={key !== "coupon_code" && key !== "shipping_postal"}
              />
            </div>
          ))}
          {error && <p className="text-sm text-red-700">{error}</p>}
          <button className="btn mt-2" type="submit">
            Создать заказ и оплатить СБП
          </button>
        </form>
      ) : (
        <div className="mt-10 grid max-w-2xl gap-8 md:grid-cols-2">
          <div className="border border-ink/10 bg-white/60 p-6">
            <p className="text-[11px] uppercase tracking-[0.18em] text-muted">СБП QR</p>
            <div className="mt-6 flex justify-center bg-white p-4">
              <QRCodeSVG value={payment.qr_url || payment.confirmation_url || payment.provider_payment_id} size={200} />
            </div>
            <p className="mt-4 text-center text-sm text-muted">
              {formatRub(payment.amount_rub)} · {payment.provider === "mock" ? "MOCK" : "ЮKassa"}
            </p>
          </div>
          <div className="space-y-4">
            <p className="text-sm text-muted">
              Заказ <span className="text-ink">{orderId.slice(0, 8)}</span>
            </p>
            <p className="text-sm">Статус оплаты: {payment.status}</p>
            <p className="text-sm">Статус заказа: {status || "pending_payment"}</p>
            {payment.confirmation_url && (
              <a className="btn w-full" href={payment.confirmation_url} target="_blank" rel="noreferrer">
                Открыть банк / СБП
              </a>
            )}
            {payment.provider === "mock" && token && (
              <button
                className="btn-outline w-full"
                onClick={async () => {
                  const r = await api.mockConfirm(token, payment.provider_payment_id);
                  setPayment(r.payment);
                  setStatus(r.order.status);
                  router.push(`/checkout/success?order=${r.order.public_id}`);
                }}
              >
                Симулировать успешную оплату
              </button>
            )}
            <p className="text-xs text-muted">
              Статус берётся с сервера (webhook / API). Клиентский «успех» не принимается.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

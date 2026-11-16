import Link from "next/link";

export function Footer() {
  return (
    <footer className="mt-24 border-t border-ink/10">
      <div className="container-page grid gap-10 py-14 md:grid-cols-3">
        <div>
          <p className="font-display text-lg tracking-brand">ATELIER</p>
          <p className="mt-3 max-w-xs text-sm text-muted">
            Премиальный fashion e-commerce для России. Оплата через СБП / ЮKassa.
          </p>
        </div>
        <div className="text-sm text-muted">
          <p className="mb-3 text-[11px] uppercase tracking-[0.18em] text-ink">Магазин</p>
          <div className="flex flex-col gap-2">
            <Link href="/catalog">Каталог</Link>
            <Link href="/cart">Корзина</Link>
            <Link href="/account">Заказы</Link>
          </div>
        </div>
        <div className="text-sm text-muted">
          <p className="mb-3 text-[11px] uppercase tracking-[0.18em] text-ink">Сервис</p>
          <p>Доставка по РФ · Возврат 14 дней</p>
          <p className="mt-2">Поддержка: support@atelier.local</p>
        </div>
      </div>
    </footer>
  );
}

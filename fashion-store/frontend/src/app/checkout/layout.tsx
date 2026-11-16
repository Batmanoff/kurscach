import { Suspense } from "react";

export default function CheckoutLayout({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<div className="container-page py-20 text-muted">Загрузка…</div>}>{children}</Suspense>;
}

import { Suspense } from "react";

export default function CatalogLayout({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<div className="container-page py-20 text-muted">Загрузка каталога…</div>}>{children}</Suspense>;
}

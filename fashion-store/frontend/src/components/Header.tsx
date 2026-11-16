"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";
import { useAuth } from "@/lib/auth";

const links = [
  { href: "/catalog", label: "Каталог" },
  { href: "/favorites", label: "Избранное" },
  { href: "/cart", label: "Корзина" },
];

export function Header() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const store = process.env.NEXT_PUBLIC_STORE_NAME || "ATELIER";

  return (
    <header className="sticky top-0 z-40 border-b border-ink/10 bg-paper/80 backdrop-blur-md">
      <div className="container-page flex h-16 items-center justify-between gap-6">
        <nav className="hidden items-center gap-6 md:flex">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={`text-[11px] uppercase tracking-[0.2em] transition ${
                pathname?.startsWith(l.href) ? "text-ink" : "text-muted hover:text-ink"
              }`}
            >
              {l.label}
            </Link>
          ))}
        </nav>

        <Link href="/" className="absolute left-1/2 -translate-x-1/2">
          <motion.span
            initial={{ opacity: 0, y: -6 }}
            animate={{ opacity: 1, y: 0 }}
            className="font-display text-xl tracking-brand text-ink md:text-2xl"
          >
            {store}
          </motion.span>
        </Link>

        <div className="ml-auto flex items-center gap-4 text-[11px] uppercase tracking-[0.18em]">
          {user?.role === "admin" && (
            <Link href="/admin" className="text-muted hover:text-ink">
              Admin
            </Link>
          )}
          {user ? (
            <>
              <Link href="/account" className="text-muted hover:text-ink">
                {user.full_name.split(" ")[0]}
              </Link>
              <button onClick={logout} className="text-muted hover:text-ink">
                Выйти
              </button>
            </>
          ) : (
            <Link href="/login" className="text-muted hover:text-ink">
              Войти
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}

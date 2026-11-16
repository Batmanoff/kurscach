"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("demo@atelier.dev");
  const [password, setPassword] = useState("Demo123!");
  const [error, setError] = useState("");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await login(email, password);
      router.push("/account");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка входа");
    }
  }

  return (
    <div className="container-page flex justify-center py-20">
      <form onSubmit={onSubmit} className="w-full max-w-md space-y-5">
        <h1 className="font-display text-4xl">Вход</h1>
        <p className="text-sm text-muted">Демо: demo@atelier.dev / Demo123!</p>
        <div>
          <label className="label">Email</label>
          <input className="input" value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <div>
          <label className="label">Пароль</label>
          <input
            className="input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        {error && <p className="text-sm text-red-700">{error}</p>}
        <button className="btn w-full" type="submit">
          Войти
        </button>
        <p className="text-sm text-muted">
          Нет аккаунта? <Link href="/register">Регистрация</Link>
        </p>
      </form>
    </div>
  );
}

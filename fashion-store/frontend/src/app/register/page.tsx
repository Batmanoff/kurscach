"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { useAuth } from "@/lib/auth";

export default function RegisterPage() {
  const { register } = useAuth();
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    try {
      await register(fullName, email, password);
      router.push("/catalog");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка регистрации");
    }
  }

  return (
    <div className="container-page flex justify-center py-20">
      <form onSubmit={onSubmit} className="w-full max-w-md space-y-5">
        <h1 className="font-display text-4xl">Регистрация</h1>
        <div>
          <label className="label">Имя</label>
          <input className="input" value={fullName} onChange={(e) => setFullName(e.target.value)} required />
        </div>
        <div>
          <label className="label">Email</label>
          <input className="input" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </div>
        <div>
          <label className="label">Пароль</label>
          <input
            className="input"
            type="password"
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        {error && <p className="text-sm text-red-700">{error}</p>}
        <button className="btn w-full" type="submit">
          Создать аккаунт
        </button>
        <p className="text-sm text-muted">
          Уже есть аккаунт? <Link href="/login">Войти</Link>
        </p>
      </form>
    </div>
  );
}

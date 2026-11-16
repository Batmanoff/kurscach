const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000/api";

export type User = {
  id: number;
  email: string;
  full_name: string;
  phone?: string | null;
  role: string;
};

export type ProductVariant = {
  id: number;
  sku: string;
  size: string;
  color: string;
  color_hex?: string | null;
  stock: number;
  price_rub: number;
  in_stock: boolean;
};

export type Product = {
  id: number;
  slug: string;
  name: string;
  brand: string;
  description?: string;
  composition?: string;
  care?: string;
  base_price_rub: number;
  compare_at_price_rub?: number | null;
  currency: string;
  images: string[];
  tags: string[];
  is_featured: boolean;
  in_stock?: boolean;
  variants?: ProductVariant[];
  category?: { id: number; slug: string; name: string } | null;
};

export type Cart = {
  id: number;
  items: Array<{
    id: number;
    variant_id: number;
    quantity: number;
    unit_price_rub: number;
    line_total_rub: number;
    variant: ProductVariant;
    product: { id: number; slug: string; name: string; brand: string; images: string[] };
  }>;
  items_count: number;
  subtotal_rub: number;
  currency: string;
};

export type Payment = {
  id: number;
  order_id: number;
  provider: string;
  provider_payment_id: string;
  status: string;
  amount_rub: number;
  currency: string;
  confirmation_url?: string | null;
  qr_url?: string | null;
};

export type Order = {
  id: number;
  public_id: string;
  status: string;
  total_rub: number;
  subtotal_rub: number;
  discount_rub: number;
  shipping_rub: number;
  currency: string;
  coupon_code?: string | null;
  shipping: {
    name: string;
    phone: string;
    city: string;
    address: string;
    postal?: string | null;
  };
  items: Array<{
    id: number;
    product_name: string;
    sku: string;
    size: string;
    color: string;
    quantity: number;
    unit_price_rub: number;
    line_total_rub: number;
  }>;
  payments?: Payment[];
  created_at?: string;
};

function authHeaders(token?: string | null): HeadersInit {
  const headers: HeadersInit = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;
  return headers;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { ...authHeaders(), ...(options.headers || {}) },
    cache: "no-store",
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const message = data?.error || data?.message || `HTTP ${res.status}`;
    throw new Error(message);
  }
  return data as T;
}

export const api = {
  health: () => request<{ status: string; payments: string }>("/health"),
  products: (params: Record<string, string | number | undefined> = {}) => {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== "") qs.set(k, String(v));
    });
    const q = qs.toString();
    return request<{ items: Product[]; total: number; page: number; pages: number }>(
      `/products${q ? `?${q}` : ""}`
    );
  },
  categories: () => request<{ items: Array<{ id: number; slug: string; name: string }> }>("/products/categories"),
  product: (slug: string) => request<{ product: Product }>(`/products/${slug}`),
  register: (body: { email: string; password: string; full_name: string; phone?: string }) =>
    request<{ user: User; access_token: string }>("/auth/register", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  login: (body: { email: string; password: string }) =>
    request<{ user: User; access_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  me: (token: string) =>
    request<{ user: User }>("/auth/me", { headers: authHeaders(token) }),
  cart: (token: string) =>
    request<{ cart: Cart }>("/cart", { headers: authHeaders(token) }),
  addToCart: (token: string, variant_id: number, quantity = 1) =>
    request<{ cart: Cart }>("/cart/items", {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ variant_id, quantity }),
    }),
  updateCartItem: (token: string, itemId: number, quantity: number) =>
    request<{ cart: Cart }>(`/cart/items/${itemId}`, {
      method: "PATCH",
      headers: authHeaders(token),
      body: JSON.stringify({ quantity }),
    }),
  removeCartItem: (token: string, itemId: number) =>
    request<{ cart: Cart }>(`/cart/items/${itemId}`, {
      method: "DELETE",
      headers: authHeaders(token),
    }),
  favorites: (token: string) =>
    request<{ items: Array<{ product: Product }> }>("/favorites", { headers: authHeaders(token) }),
  addFavorite: (token: string, product_id: number) =>
    request("/favorites", {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ product_id }),
    }),
  removeFavorite: (token: string, product_id: number) =>
    request(`/favorites/${product_id}`, { method: "DELETE", headers: authHeaders(token) }),
  createOrder: (
    token: string,
    body: {
      shipping_name: string;
      shipping_phone: string;
      shipping_city: string;
      shipping_address: string;
      shipping_postal?: string;
      coupon_code?: string;
      comment?: string;
    }
  ) =>
    request<{ order: Order }>("/orders", {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify(body),
    }),
  payOrder: (token: string, publicId: string) =>
    request<{ order: Order; payment: Payment }>(`/orders/${publicId}/pay`, {
      method: "POST",
      headers: authHeaders(token),
    }),
  createPayment: (token: string, order_public_id: string) =>
    request<{ payment: Payment; order: Order }>("/payments/create", {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ order_public_id }),
    }),
  paymentStatus: (token: string, providerPaymentId: string) =>
    request<{ payment: Payment; order_status: string }>(`/payments/${providerPaymentId}/status`, {
      headers: authHeaders(token),
    }),
  mockConfirm: (token: string, provider_payment_id: string) =>
    request<{ payment: Payment; order: Order }>("/payments/mock/confirm", {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({ provider_payment_id }),
    }),
  myOrders: (token: string) =>
    request<{ items: Order[] }>("/orders", { headers: authHeaders(token) }),
  adminDashboard: (token: string) =>
    request<Record<string, unknown>>("/admin/dashboard", { headers: authHeaders(token) }),
  adminOrders: (token: string) =>
    request<{ items: Order[] }>("/admin/orders", { headers: authHeaders(token) }),
  adminUpdateOrder: (token: string, publicId: string, status: string) =>
    request<{ order: Order }>(`/admin/orders/${publicId}`, {
      method: "PATCH",
      headers: authHeaders(token),
      body: JSON.stringify({ status }),
    }),
  adminProducts: (token: string) =>
    request<{ items: Product[] }>("/admin/products", { headers: authHeaders(token) }),
};

export function formatRub(value: number): string {
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency: "RUB",
    maximumFractionDigits: 0,
  }).format(value);
}

export { API_URL };

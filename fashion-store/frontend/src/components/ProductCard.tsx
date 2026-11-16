"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { formatRub, type Product } from "@/lib/api";

export function ProductCard({ product, index = 0 }: { product: Product; index?: number }) {
  const image = product.images?.[0];
  return (
    <motion.article
      initial={{ opacity: 0, y: 18 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-40px" }}
      transition={{ duration: 0.45, delay: index * 0.04 }}
      className="group"
    >
      <Link href={`/product/${product.slug}`} className="block">
        <div className="relative aspect-[3/4] overflow-hidden bg-mist">
          {image ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={image}
              alt={product.name}
              className="h-full w-full object-cover transition duration-700 group-hover:scale-[1.03]"
            />
          ) : (
            <div className="flex h-full items-center justify-center text-xs uppercase tracking-widest text-muted">
              No image
            </div>
          )}
        </div>
        <div className="mt-4 space-y-1">
          <p className="text-[10px] uppercase tracking-[0.2em] text-muted">{product.brand}</p>
          <h3 className="text-sm">{product.name}</h3>
          <div className="flex items-baseline gap-3 pt-1">
            <span className="text-sm">{formatRub(product.base_price_rub)}</span>
            {product.compare_at_price_rub ? (
              <span className="text-xs text-muted line-through">
                {formatRub(product.compare_at_price_rub)}
              </span>
            ) : null}
          </div>
        </div>
      </Link>
    </motion.article>
  );
}

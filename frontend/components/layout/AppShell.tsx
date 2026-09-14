"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

import { NAV_ITEMS } from "@/lib/navigation";

function isActive(pathname: string, href: string): boolean {
  if (href === "/") {
    return pathname === "/";
  }
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const isHome = pathname === "/";

  return (
    <div className="min-h-screen">
      <header className="border-b-2 border-border bg-surface">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
          <Link href="/" className="font-display text-2xl tracking-tight">
            fold
          </Link>

          <button
            type="button"
            className="border-2 border-border bg-surface px-3 py-1 text-sm font-bold uppercase sm:hidden"
            aria-expanded={mobileOpen}
            aria-controls="primary-navigation"
            onClick={() => setMobileOpen((value) => !value)}
          >
            Menu
          </button>

          <nav
            id="primary-navigation"
            className={`${mobileOpen ? "absolute left-4 right-4 top-14 z-20 block border-2 border-border bg-surface p-3" : "hidden"} sm:static sm:block sm:border-0 sm:p-0`}
            aria-label="Primary"
          >
            <ul className="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:gap-x-5">
              {NAV_ITEMS.filter((item) => item.href !== "/").map((item) => {
                const active = isActive(pathname, item.href);
                return (
                  <li key={item.href}>
                    <Link
                      href={item.href}
                      aria-current={active ? "page" : undefined}
                      className={`text-sm font-bold uppercase tracking-wide ${
                        active ? "text-accent" : "text-foreground hover:text-accent"
                      }`}
                      onClick={() => setMobileOpen(false)}
                    >
                      {item.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </nav>
        </div>
      </header>

      {isHome ? (
        children
      ) : (
        <>
          <main className="page-rise mx-auto max-w-6xl px-4 py-8 sm:px-6">
            {children}
          </main>
          <footer className="mx-auto max-w-6xl border-t-2 border-border px-4 py-6 text-xs text-muted sm:px-6">
            Historical simulation only. No claim of future performance.
          </footer>
        </>
      )}
    </div>
  );
}

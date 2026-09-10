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

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[16rem_1fr]">
      <aside
        className="border-b border-border bg-surface lg:border-b-0 lg:border-r"
        aria-label="Primary"
      >
        <div className="flex items-center justify-between px-4 py-4 lg:block lg:px-5 lg:py-6">
          <div>
            <p className="text-[0.7rem] font-semibold uppercase tracking-[0.16em] text-muted">
              Quant Research
            </p>
            <h1 className="mt-1 text-base font-semibold tracking-tight">
              LSTM Platform
            </h1>
          </div>
          <button
            type="button"
            className="rounded-md border border-border px-3 py-1.5 text-sm lg:hidden"
            aria-expanded={mobileOpen}
            aria-controls="primary-navigation"
            onClick={() => setMobileOpen((value) => !value)}
          >
            Menu
          </button>
        </div>

        <nav
          id="primary-navigation"
          className={`${mobileOpen ? "block" : "hidden"} border-t border-border px-2 py-3 lg:block lg:border-t-0 lg:px-3`}
          aria-label="Research sections"
        >
          <ul className="space-y-1">
            {NAV_ITEMS.map((item) => {
              const active = isActive(pathname, item.href);
              return (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    aria-current={active ? "page" : undefined}
                    className={`block rounded-md px-3 py-2 transition-colors ${
                      active
                        ? "bg-accent-muted text-accent"
                        : "text-foreground hover:bg-surface-muted"
                    }`}
                    onClick={() => setMobileOpen(false)}
                  >
                    <span className="block text-sm font-medium">{item.label}</span>
                    <span className="mt-0.5 block text-xs text-muted">
                      {item.description}
                    </span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
      </aside>

      <div className="min-w-0">
        <header className="border-b border-border bg-surface px-4 py-3 lg:px-8">
          <p className="text-sm text-muted">
            Historical research only. Not investment advice.
          </p>
        </header>
        <main className="px-4 py-6 lg:px-8 lg:py-8">{children}</main>
      </div>
    </div>
  );
}

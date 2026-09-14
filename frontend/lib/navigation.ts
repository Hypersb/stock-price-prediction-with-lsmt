export type NavItem = {
  href: string;
  label: string;
};

export const NAV_ITEMS: NavItem[] = [
  { href: "/", label: "Home" },
  { href: "/market", label: "Market" },
  { href: "/features", label: "Features" },
  { href: "/models", label: "Models" },
  { href: "/experiments", label: "Experiments" },
  { href: "/walk-forward", label: "Walk-forward" },
  { href: "/backtests", label: "Backtests" },
];

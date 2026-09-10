export type NavItem = {
  href: string;
  label: string;
  description: string;
};

export const NAV_ITEMS: NavItem[] = [
  {
    href: "/",
    label: "Overview",
    description: "Research platform summary",
  },
  {
    href: "/market",
    label: "Market",
    description: "Prices and quantitative summary",
  },
  {
    href: "/features",
    label: "Features",
    description: "Engineered feature inspection",
  },
  {
    href: "/models",
    label: "Models",
    description: "Supported model families",
  },
  {
    href: "/experiments",
    label: "Experiments",
    description: "Stored experiment history",
  },
  {
    href: "/walk-forward",
    label: "Walk Forward",
    description: "Temporal validation analytics",
  },
  {
    href: "/backtests",
    label: "Backtests",
    description: "Strategy and risk results",
  },
];

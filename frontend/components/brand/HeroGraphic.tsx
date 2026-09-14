export function HeroGraphic() {
  return (
    <svg
      viewBox="0 0 640 520"
      className="h-auto w-full"
      role="img"
      aria-label="Stylized equity path graphic"
    >
      <rect x="0" y="0" width="640" height="520" fill="#111111" />
      {[80, 160, 240, 320, 400, 480].map((y) => (
        <line
          key={`h-${y}`}
          x1="24"
          x2="616"
          y1={y}
          y2={y}
          stroke="#2a2a2a"
          strokeWidth="1"
        />
      ))}
      {[80, 160, 240, 320, 400, 480, 560].map((x) => (
        <line
          key={`v-${x}`}
          x1={x}
          x2={x}
          y1="24"
          y2="496"
          stroke="#2a2a2a"
          strokeWidth="1"
        />
      ))}
      <path
        className="hero-fill"
        d="M40 360 L110 340 L170 390 L240 250 L300 280 L360 180 L430 210 L500 90 L600 140 L600 480 L40 480 Z"
        fill="#ff2e00"
        fillOpacity="0.85"
      />
      <path
        className="hero-line"
        d="M40 360 L110 340 L170 390 L240 250 L300 280 L360 180 L430 210 L500 90 L600 140"
        fill="none"
        stroke="#f2f2f0"
        strokeWidth="6"
        strokeLinecap="square"
        strokeLinejoin="miter"
      />
      <circle cx="600" cy="140" r="10" fill="#f2f2f0" />
      <rect x="24" y="24" width="14" height="14" fill="#ff2e00" />
      <text
        x="48"
        y="36"
        fill="#f2f2f0"
        fontSize="14"
        fontFamily="ui-monospace, monospace"
      >
        OOS PATH
      </text>
    </svg>
  );
}

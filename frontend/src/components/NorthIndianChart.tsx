import { D1House, D1ChartPlanet } from "../api/kpClient";

type HousePlacement = {
  x: number;
  y: number;
  align?: "left" | "center" | "right";
};

const housePlacements: Record<number, HousePlacement> = {
  1: { x: 50, y: 18, align: "center" },
  2: { x: 27, y: 15, align: "center" },
  3: { x: 5, y: 25, align: "left" },
  4: { x: 28, y: 50, align: "center" },
  5: { x: 7, y: 67, align: "left" },
  6: { x: 27, y: 83, align: "center" },
  7: { x: 50, y: 70, align: "center" },
  8: { x: 73, y: 83, align: "center" },
  9: { x: 87, y: 75, align: "right" },
  10: { x: 72, y: 50, align: "center" },
  11: { x: 90, y: 20, align: "right" },
  12: { x: 73, y: 10, align: "center" }
};

const stateSymbols: Array<[keyof D1ChartPlanet["state_flags"], string]> = [
  ["retrograde", "*"],
  ["combust", "^"],
  ["exalted", "↑"],
  ["debilitated", "↓"]
];

function roundedDegree(degreeDecimal: number) {
  const rounded = Math.round(degreeDecimal);
  return rounded === 30 ? 0 : rounded;
}

function planetText(planet: D1ChartPlanet) {
  const symbols = stateSymbols
    .filter(([key]) => planet.state_flags[key])
    .map(([, symbol]) => symbol)
    .join("");

  return `${planet.short_name}${symbols ? ` ${symbols}` : ""} ${roundedDegree(
    planet.degree_decimal
  )}°`;
}

function HouseContent({ house }: { house: D1House }) {
  const placement = housePlacements[house.house_number];
  const translateX =
    placement.align === "left"
      ? "0"
      : placement.align === "right"
        ? "-100%"
        : "-50%";

  return (
    <div
      className="absolute grid max-w-[31%] gap-1 text-center"
      style={{
        left: `${placement.x}%`,
        top: `${placement.y}%`,
        textAlign: placement.align ?? "center",
        transform: `translate(${translateX}, -50%)`
      }}
    >
      <div className="text-[11px] font-semibold leading-none text-[#6b5a4b] sm:text-xs">
        {house.sign_number}
      </div>
      <div className="grid gap-0.5 text-[11px] leading-tight text-[#1f3f60] sm:text-[13px]">
        {house.planets.map((planet) => (
          <div
            className="truncate font-semibold"
            key={`${planet.short_name}-${planet.absolute_longitude}`}
            title={`${planet.name} ${planet.degree}`}
          >
            {planetText(planet)}
          </div>
        ))}
      </div>
    </div>
  );
}

export function NorthIndianChart({ houses }: { houses: D1House[] }) {
  return (
    <div className="mx-auto w-full max-w-[560px]">
      <div className="relative aspect-square w-full overflow-hidden rounded-lg border border-[#b9a989] bg-[#fffdf7] shadow-sm">
        <svg
          aria-hidden="true"
          className="absolute inset-0 h-full w-full text-[#6f6254]"
          focusable="false"
          viewBox="0 0 100 100"
        >
          <rect
            fill="none"
            height="96"
            rx="2"
            stroke="currentColor"
            strokeWidth="0.8"
            width="96"
            x="2"
            y="2"
          />
          <path
            d="M2 2 L50 50 L2 98 M98 2 L50 50 L98 98 M50 2 L98 50 L50 98 L2 50 Z M98 2 L50 50 M2 98 L50 50"
            fill="none"
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="0.8"
          />
        </svg>

        {houses.map((house) => (
          <HouseContent house={house} key={house.house_number} />
        ))}
      </div>

      <div className="mt-3 grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-[#5d6876] sm:grid-cols-4">
        <span>* Retrograde</span>
        <span>^ Combust</span>
        <span>↑ Exalted</span>
        <span>↓ Debilitated</span>
      </div>
    </div>
  );
}

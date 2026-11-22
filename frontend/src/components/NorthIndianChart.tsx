import { KeyboardEvent, useState } from "react";

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
  9: { x: 90, y: 70, align: "right" },
  10: { x: 72, y: 50, align: "center" },
  11: { x: 90, y: 20, align: "right" },
  12: { x: 73, y: 10, align: "center" }
};

const houseNumberPlacements: Record<number, HousePlacement> = {
  1: { x: 50, y: 45, align: "center" },
  2: { x: 26, y: 22, align: "center" },
  3: { x: 22, y: 26, align: "center" },
  4: { x: 45, y: 50, align: "center" },
  5: { x: 20, y: 72, align: "center" },
  6: { x: 26, y: 77, align: "center" },
  7: { x: 50, y: 53, align: "center" },
  8: { x: 74, y: 77, align: "center" },
  9: { x: 78, y: 74, align: "center" },
  10: { x: 53, y: 50, align: "center" },
  11: { x: 77, y: 26, align: "center" },
  12: { x: 74, y: 22, align: "center" }
};

const houseRegions: Record<number, string> = {
  1: "50,2 74,26 50,50 26,26",
  2: "2,2 50,2 26,26",
  3: "2,2 26,26 2,50",
  4: "2,50 26,26 50,50 26,74",
  5: "2,50 26,74 2,98",
  6: "2,98 26,74 50,98",
  7: "50,50 74,74 50,98 26,74",
  8: "50,98 74,74 98,98",
  9: "98,50 98,98 74,74",
  10: "50,50 74,26 98,50 74,74",
  11: "98,2 98,50 74,26",
  12: "50,2 98,2 74,26"
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

function planetStateText(planet: D1ChartPlanet) {
  const symbols = stateSymbols
    .filter(([key]) => planet.state_flags[key])
    .map(([, symbol]) => symbol)
    .join("");

  return `${planet.short_name}${symbols ? ` ${symbols}` : ""}`;
}

function planetText(planet: D1ChartPlanet) {
  return `${planetStateText(planet)} ${roundedDegree(
    planet.degree_decimal
  )}°`;
}

function HouseContent({
  house,
  transitPlanets = [],
  isInteractive = false
}: {
  house: D1House;
  transitPlanets?: D1ChartPlanet[];
  isInteractive?: boolean;
}) {
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
        pointerEvents: isInteractive ? "none" : undefined,
        top: `${placement.y}%`,
        textAlign: placement.align ?? "center",
        transform: `translate(${translateX}, -50%)`
      }}
    >
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
      {transitPlanets.length > 0 && (
        <div className="mt-1 flex flex-wrap justify-center gap-1">
          {transitPlanets.map((planet) => (
            <span
              className="inline-grid min-h-7 min-w-7 place-items-center rounded-full bg-[#b42318] px-1.5 text-[9px] font-bold leading-none text-white shadow-sm sm:min-h-8 sm:min-w-8 sm:text-[10px]"
              key={`transit-${planet.short_name}-${planet.absolute_longitude}`}
              title={`Transit ${planet.name}`}
            >
              {planetStateText(planet)}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

function HouseNumberLabel({
  house,
  isInteractive = false
}: {
  house: D1House;
  isInteractive?: boolean;
}) {
  const placement = houseNumberPlacements[house.house_number];

  return (
    <div
      className="absolute grid h-5 w-5 place-items-center text-[11px] font-bold leading-none text-[#6b5a4b] sm:text-xs"
      style={{
        left: `${placement.x}%`,
        pointerEvents: isInteractive ? "none" : undefined,
        top: `${placement.y}%`,
        transform: "translate(-50%, -50%)"
      }}
    >
      {house.sign_number}
    </div>
  );
}

export function NorthIndianChart({
  houses,
  transitPlanetsByHouse,
  onHouseClick
}: {
  houses: D1House[];
  transitPlanetsByHouse?: Record<number, D1ChartPlanet[]>;
  onHouseClick?: (house: D1House) => void;
}) {
  const [hoveredHouseNumber, setHoveredHouseNumber] = useState<number | null>(
    null
  );
  const isInteractive = Boolean(onHouseClick);
  const houseByNumber = new Map(houses.map((house) => [house.house_number, house]));

  function handleHouseKeyDown(
    event: KeyboardEvent<SVGPolygonElement>,
    house: D1House
  ) {
    if (event.key !== "Enter" && event.key !== " ") {
      return;
    }

    event.preventDefault();
    onHouseClick?.(house);
  }

  return (
    <div className="mx-auto w-full max-w-[560px]">
      <div className="relative aspect-square w-full overflow-hidden rounded-lg border border-[#b9a989] bg-[#fffdf7] shadow-sm">
        <svg
          aria-hidden={isInteractive ? undefined : "true"}
          className="absolute inset-0 h-full w-full text-[#6f6254]"
          focusable="false"
          viewBox="0 0 100 100"
        >
          {isInteractive &&
            Object.entries(houseRegions).map(([houseNumberText, points]) => {
              const houseNumber = Number(houseNumberText);
              const house = houseByNumber.get(houseNumber);
              if (!house) {
                return null;
              }

              const isHovered = hoveredHouseNumber === houseNumber;

              return (
                <polygon
                  aria-label={`Open house ${houseNumber} significators`}
                  className="cursor-pointer outline-none transition-colors"
                  fill={isHovered ? "rgba(244, 196, 82, 0.38)" : "transparent"}
                  key={houseNumber}
                  points={points}
                  role="button"
                  stroke="transparent"
                  strokeWidth="0"
                  tabIndex={0}
                  onClick={() => onHouseClick?.(house)}
                  onFocus={() => setHoveredHouseNumber(houseNumber)}
                  onKeyDown={(event) => handleHouseKeyDown(event, house)}
                  onMouseEnter={() => setHoveredHouseNumber(houseNumber)}
                  onMouseLeave={() => setHoveredHouseNumber(null)}
                />
              );
            })}
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
          <div key={house.house_number}>
            <HouseNumberLabel house={house} isInteractive={isInteractive} />
            <HouseContent
              house={house}
              isInteractive={isInteractive}
              transitPlanets={transitPlanetsByHouse?.[house.house_number]}
            />
          </div>
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

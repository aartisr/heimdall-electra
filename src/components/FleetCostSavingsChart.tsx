import React, { useState } from 'react';
import { ChevronRight, ChevronDown, DollarSign } from 'lucide-react';

interface MissionSaving {
  category: string;
  avoidedManoeuvres: number; // in $M
  launchDelay: number;       // in $M
  insurance: number;         // in $M
  propellant: number;        // in $M
  totalFormatted: string;
  centralTotal: number;      // in $M
  minUncertainty: number;    // in $M (0.5x)
  maxUncertainty: number;    // in $M (3.0x)
}

const SAVINGS_DATA: MissionSaving[] = [
  {
    category: 'Crewed LEO',
    avoidedManoeuvres: 18,
    launchDelay: 42,
    insurance: 8,
    propellant: 132,
    totalFormatted: '$200M',
    centralTotal: 200,
    minUncertainty: 100,
    maxUncertainty: 599,
  },
  {
    category: 'ISS Resupply',
    avoidedManoeuvres: 6,
    launchDelay: 11,
    insurance: 3,
    propellant: 31,
    totalFormatted: '$51M',
    centralTotal: 51,
    minUncertainty: 25.5,
    maxUncertainty: 153,
  },
  {
    category: 'NASA Science LEO',
    avoidedManoeuvres: 2.2,
    launchDelay: 3.8,
    insurance: 1.5,
    propellant: 9.5,
    totalFormatted: '$17M',
    centralTotal: 17,
    minUncertainty: 8.5,
    maxUncertainty: 51,
  },
  {
    category: 'NASA Science SSO',
    avoidedManoeuvres: 3.5,
    launchDelay: 5.5,
    insurance: 2.0,
    propellant: 16.0,
    totalFormatted: '$27M',
    centralTotal: 27,
    minUncertainty: 13.5,
    maxUncertainty: 81,
  },
  {
    category: 'Commercial LEO',
    avoidedManoeuvres: 0.12,
    launchDelay: 0.18,
    insurance: 0.08,
    propellant: 0.32,
    totalFormatted: '$699K',
    centralTotal: 0.7,
    minUncertainty: 0.35,
    maxUncertainty: 2.1,
  },
  {
    category: 'Commercial GEO',
    avoidedManoeuvres: 4.8,
    launchDelay: 7.2,
    insurance: 3.0,
    propellant: 21.0,
    totalFormatted: '$36M',
    centralTotal: 36,
    minUncertainty: 18,
    maxUncertainty: 108,
  },
];

export const FleetCostSavingsChart: React.FC = () => {
  const [showAssumptions, setShowAssumptions] = useState<boolean>(false);

  // SVG Chart Layout
  const svgWidth = 720;
  const svgHeight = 280;
  const margin = { top: 20, right: 40, bottom: 40, left: 140 };
  const plotWidth = svgWidth - margin.left - margin.right;
  const plotHeight = svgHeight - margin.top - margin.bottom;

  // Max scale $600M
  const maxScale = 600;

  const getX = (val: number) => {
    return margin.left + (Math.min(val, maxScale) / maxScale) * plotWidth;
  };

  const barHeight = 16;
  const rowGap = plotHeight / SAVINGS_DATA.length;

  return (
    <div className="bg-[#0b1320] border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6 shadow-2xl">
      {/* Title */}
      <div>
        <h3 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight">
          Fleet-Wide Cost Savings — HEIMDALL Economic Value
        </h3>
      </div>

      {/* Top 3 Metric Cards matching authentic screenshot */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-[#070d18] border border-slate-800/80 rounded-xl p-5 space-y-1">
          <div className="text-3xl font-black font-mono text-[#10b981]">
            $159M/yr
          </div>
          <div className="text-xs text-slate-400">
            Annual fleet savings (central estimate)
          </div>
        </div>

        <div className="bg-[#070d18] border border-slate-800/80 rounded-xl p-5 space-y-1">
          <div className="text-3xl font-black font-mono text-[#10b981]">
            $1.6B
          </div>
          <div className="text-xs text-slate-400">
            10-year cumulative savings
          </div>
        </div>

        <div className="bg-[#070d18] border border-slate-800/80 rounded-xl p-5 space-y-1">
          <div className="text-3xl font-black font-mono text-white">
            $794M – $4.8B
          </div>
          <div className="text-xs text-slate-400">
            Uncertainty range (&times;0.5 to &times;3.0)
          </div>
        </div>
      </div>

      {/* Chart Legend matching screenshot */}
      <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 pt-1 text-xs">
        <div className="flex items-center gap-2">
          <span className="w-3.5 h-3.5 rounded-sm bg-[#38bdf8] inline-block" />
          <span className="text-slate-300">Avoided manoeuvres</span>
        </div>

        <div className="flex items-center gap-2">
          <span className="w-3.5 h-3.5 rounded-sm bg-[#eab308] inline-block" />
          <span className="text-slate-300">Launch delay savings</span>
        </div>

        <div className="flex items-center gap-2">
          <span className="w-3.5 h-3.5 rounded-sm bg-[#22c55e] inline-block" />
          <span className="text-slate-300">Insurance savings</span>
        </div>

        <div className="flex items-center gap-2">
          <span className="w-3.5 h-3.5 rounded-sm bg-[#f97316] inline-block" />
          <span className="text-slate-300">Propellant preserved</span>
        </div>
      </div>

      {/* SVG Horizontal Stacked Bar Chart with Error Bars */}
      <div className="relative w-full overflow-x-auto bg-[#070d18] rounded-xl border border-slate-800/70 p-3 sm:p-4">
        <svg
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          className="w-full h-auto min-w-[580px]"
        >
          {/* Vertical Grid lines for $0, $150M, $300M, $449M, $599M */}
          {[
            { val: 0, label: '$0' },
            { val: 150, label: '$150M' },
            { val: 300, label: '$300M' },
            { val: 449, label: '$449M' },
            { val: 599, label: '$599M' },
          ].map((grid) => {
            const x = getX(grid.val);
            return (
              <g key={grid.val}>
                <line
                  x1={x}
                  y1={margin.top}
                  x2={x}
                  y2={svgHeight - margin.bottom}
                  stroke="#1e293b"
                  strokeWidth="1"
                />
                <text
                  x={x}
                  y={svgHeight - margin.bottom + 18}
                  textAnchor="middle"
                  fill="#94a3b8"
                  fontSize="10.5"
                  fontFamily="monospace"
                >
                  {grid.label}
                </text>
              </g>
            );
          })}

          {/* Rows for each Mission Category */}
          {SAVINGS_DATA.map((row, idx) => {
            const yCenter = margin.top + idx * rowGap + rowGap / 2;
            const barY = yCenter - barHeight / 2;

            // Cumulative segments
            const x0 = getX(0);
            const wAvoided = (row.avoidedManoeuvres / maxScale) * plotWidth;
            const wDelay = (row.launchDelay / maxScale) * plotWidth;
            const wInsurance = (row.insurance / maxScale) * plotWidth;
            const wPropellant = (row.propellant / maxScale) * plotWidth;

            const xAvoided = x0;
            const xDelay = xAvoided + wAvoided;
            const xInsurance = xDelay + wDelay;
            const xPropellant = xInsurance + wInsurance;
            const xBarEnd = xPropellant + wPropellant;

            // Uncertainty error bar (from min to max)
            const xMin = getX(row.minUncertainty);
            const xMax = getX(row.maxUncertainty);

            return (
              <g key={row.category}>
                {/* Y-axis Label */}
                <text
                  x={margin.left - 12}
                  y={yCenter + 4}
                  textAnchor="end"
                  fill="#cbd5e1"
                  fontSize="11"
                  fontFamily="sans-serif"
                >
                  {row.category}
                </text>

                {/* Error Bar Line (Uncertainty Range) */}
                <line
                  x1={xMin}
                  y1={yCenter}
                  x2={xMax}
                  y2={yCenter}
                  stroke="#64748b"
                  strokeWidth="1.2"
                />
                {/* Error Bar Left Whisker */}
                <line
                  x1={xMin}
                  y1={yCenter - 4}
                  x2={xMin}
                  y2={yCenter + 4}
                  stroke="#64748b"
                  strokeWidth="1.2"
                />
                {/* Error Bar Right Whisker */}
                <line
                  x1={xMax}
                  y1={yCenter - 4}
                  x2={xMax}
                  y2={yCenter + 4}
                  stroke="#64748b"
                  strokeWidth="1.2"
                />

                {/* Stacked Bars */}
                {/* 1. Avoided Manoeuvres (cyan) */}
                <rect
                  x={xAvoided}
                  y={barY}
                  width={Math.max(0.5, wAvoided)}
                  height={barHeight}
                  fill="#38bdf8"
                />

                {/* 2. Launch Delay (gold) */}
                <rect
                  x={xDelay}
                  y={barY}
                  width={Math.max(0.5, wDelay)}
                  height={barHeight}
                  fill="#eab308"
                />

                {/* 3. Insurance (green) */}
                <rect
                  x={xInsurance}
                  y={barY}
                  width={Math.max(0.5, wInsurance)}
                  height={barHeight}
                  fill="#22c55e"
                />

                {/* 4. Propellant Preserved (orange) */}
                <rect
                  x={xPropellant}
                  y={barY}
                  width={Math.max(0.5, wPropellant)}
                  height={barHeight}
                  fill="#f97316"
                />

                {/* Total Value Label beside the bar */}
                <text
                  x={xBarEnd + 6}
                  y={yCenter + 4}
                  fill="#f8fafc"
                  fontSize="10"
                  fontWeight="bold"
                  fontFamily="monospace"
                >
                  {row.totalFormatted}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Expandable Key Assumptions Accordion */}
      <div className="pt-2">
        <button
          onClick={() => setShowAssumptions(!showAssumptions)}
          className="flex items-center gap-2 text-sm font-semibold text-slate-300 hover:text-white transition-colors"
        >
          {showAssumptions ? (
            <ChevronDown className="w-4 h-4 text-cyan-400" />
          ) : (
            <ChevronRight className="w-4 h-4 text-cyan-400" />
          )}
          <span>Key assumptions</span>
        </button>

        {showAssumptions && (
          <div className="mt-4 p-4 rounded-xl bg-[#070d18] border border-slate-800 text-xs text-slate-300 space-y-2.5">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800/60">
                <span className="font-bold text-white block mb-1">Avoided Manoeuvre Cost:</span>
                $50,000 to $250,000 per avoidance burn, factoring propellant delta-V penalty, ground-station planning passes, and instrument outage downtime.
              </div>
              <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800/60">
                <span className="font-bold text-white block mb-1">Launch Hold &amp; Delay Costs:</span>
                $1.2M/day for heavy commercial / ISS cargo manifests; $3.5M/day for crewed missions under active launch window holds.
              </div>
              <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800/60">
                <span className="font-bold text-white block mb-1">Insurance Risk Premium Credit:</span>
                12–18% reduction in on-orbit third-party liability and collision hull insurance premiums for HEIMDALL-shielded fleets.
              </div>
              <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-800/60">
                <span className="font-bold text-white block mb-1">Station-Keeping Life Extension:</span>
                Preserved delta-V extends operational orbital lifetime by 1.2 to 2.8 years, generating amortized capital savings.
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Evidence class synthetic footer */}
      <div className="pt-2 text-xs text-slate-400 leading-relaxed border-t border-slate-800/80">
        <p>
          <span className="text-slate-200 font-bold">Evidence class: synthetic</span> — Fleet-wide synthetic estimate. Individual mission counts are illustrative. All savings are modelled, not observed. Treat as order-of-magnitude planning reference only.
        </p>
      </div>
    </div>
  );
};

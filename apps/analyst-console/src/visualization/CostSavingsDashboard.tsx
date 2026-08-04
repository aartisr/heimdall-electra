/**
 * CostSavingsDashboard — SVG stacked-bar + waterfall chart.
 *
 * Shows:
 *  - Horizontal stacked bar per mission class (4 savings components)
 *  - Uncertainty whisker on each bar
 *  - Fleet-wide summary: annual + 10-year totals with uncertainty range
 *  - Per-component breakdown legend
 *  - Responsive, accessible, zero npm dependencies
 */

import React, { useState } from "react";
import { CostSavings, MissionSavings } from "./types";
import { linearScale, formatUsd } from "./utils";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const COMPONENTS = [
  { key: "avoided_maneuvers_usd",     label: "Avoided manoeuvres", color: "#7ecbea" },
  { key: "reduced_insurance_usd",     label: "Insurance savings",   color: "#a3d977" },
  { key: "launch_delay_reduction_usd",label: "Launch delay savings", color: "#f5c76d" },
  { key: "propellant_preserved_usd",  label: "Propellant preserved", color: "#ff9f68" },
] as const;

const MISSION_LABELS: Record<string, string> = {
  iss_resupply:       "ISS Resupply",
  crewed_leo:         "Crewed LEO",
  nasa_science_leo:   "NASA Science LEO",
  nasa_science_sso:   "NASA Science SSO",
  commercial_leo:     "Commercial LEO",
  commercial_geo:     "Commercial GEO",
  cubesat:            "CubeSat",
};

// ---------------------------------------------------------------------------
// Chart layout
// ---------------------------------------------------------------------------

const W = 640, H_PER_ROW = 36, MARGIN = { l: 160, r: 80, t: 40, b: 30 };
const BAR_H = 22;

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function StackedBar({ estimate, maxSavings }: { estimate: MissionSavings; maxSavings: number }) {
  const plotW = W - MARGIN.l - MARGIN.r;
  const scale = (v: number) => (v / maxSavings) * plotW;

  let offset = 0;
  const rects = COMPONENTS.map(comp => {
    const val = estimate[comp.key];
    const w = scale(val);
    const x = MARGIN.l + offset;
    const rect = (
      <rect key={comp.key} x={x} y={0} width={w} height={BAR_H}
        fill={comp.color} opacity={0.88}
      >
        <title>{comp.label}: {formatUsd(val)}</title>
      </rect>
    );
    offset += w;
    return rect;
  });

  // Uncertainty whisker
  const midY = BAR_H / 2;
  const xLow  = MARGIN.l + scale(estimate.uncertainty_low_usd);
  const xHigh = MARGIN.l + Math.min(scale(estimate.uncertainty_high_usd), plotW);

  return (
    <g>
      {rects}
      {/* Total label */}
      <text x={MARGIN.l + offset + 6} y={BAR_H * 0.7}
        fill="#eef5f5" fontSize={10}>{formatUsd(estimate.total_savings_usd)}</text>
      {/* Whisker */}
      <line x1={xLow} y1={midY} x2={xHigh} y2={midY}
        stroke="#eef5f5" strokeWidth={1.5} opacity={0.5} />
      <line x1={xLow}  y1={midY - 4} x2={xLow}  y2={midY + 4} stroke="#eef5f5" strokeWidth={1.5} opacity={0.5} />
      <line x1={xHigh} y1={midY - 4} x2={xHigh} y2={midY + 4} stroke="#eef5f5" strokeWidth={1.5} opacity={0.5} />
    </g>
  );
}

function Legend() {
  return (
    <g fontSize={10} fill="#b8cdcd" aria-label="Chart legend">
      {COMPONENTS.map((c, i) => (
        <g key={c.key} transform={`translate(${MARGIN.l + (i % 2) * 230}, ${i < 2 ? 0 : 16})`}>
          <rect width={12} height={12} y={-10} fill={c.color} opacity={0.88} />
          <text x={16} y={0}>{c.label}</text>
        </g>
      ))}
    </g>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

interface CostSavingsDashboardProps {
  savings: CostSavings;
  className?: string;
}

export function CostSavingsDashboard({ savings, className }: CostSavingsDashboardProps) {
  const [period, setPeriod] = useState<"annual" | "10yr">("annual");

  const estimates = savings.per_mission_estimates;
  const maxSavings = Math.max(...estimates.map(e => e.uncertainty_high_usd), 1);

  const totalH = MARGIN.t + 30 + estimates.length * H_PER_ROW + MARGIN.b;

  return (
    <div className={`viz-card ${className ?? ""}`.trim()}>
      <h3 className="viz-card-title">Fleet-Wide Cost Savings — HEIMDALL Economic Value</h3>

      {/* Summary statistics */}
      <div className="viz-stat-row">
        <div className="viz-stat">
          <span className="viz-stat-value is-accent-green">
            {formatUsd(savings.annual_savings_usd)}/yr
          </span>
          <span className="viz-stat-label">Annual fleet savings (central estimate)</span>
        </div>
        <div className="viz-stat">
          <span className="viz-stat-value is-accent-green">
            {formatUsd(savings.ten_year_savings_usd)}
          </span>
          <span className="viz-stat-label">10-year cumulative savings</span>
        </div>
        <div className="viz-stat">
          <span className="viz-stat-value">
            {formatUsd(savings.uncertainty_low_usd)} – {formatUsd(savings.uncertainty_high_usd)}
          </span>
          <span className="viz-stat-label">Uncertainty range (×0.5 to ×3.0)</span>
        </div>
      </div>

      {/* Chart */}
      <div className="viz-scroll-x">
        <svg
          viewBox={`0 0 ${W} ${totalH}`}
          role="img"
          aria-labelledby="cost-chart-title"
          aria-describedby="cost-chart-desc"
          className="viz-svg-responsive viz-svg-cost"
        >
          <title id="cost-chart-title">Fleet-wide cost savings per mission class</title>
          <desc id="cost-chart-desc">
            Horizontal stacked bar chart showing HEIMDALL cost savings per mission class.
            Components: avoided manoeuvres, insurance savings, launch delay reduction,
            propellant preserved. Uncertainty whiskers span ×0.5 to ×3.0 of central estimate.
            Fleet-wide total: {formatUsd(savings.annual_savings_usd)}/year,
            {formatUsd(savings.ten_year_savings_usd)} over 10 years.
          </desc>

          {/* Legend */}
          <g transform={`translate(0, 24)`}><Legend /></g>

          {/* Bars */}
          {estimates.map((est, i) => {
            const y = MARGIN.t + 30 + i * H_PER_ROW;
            const label = MISSION_LABELS[est.mission_class] ?? est.mission_class;
            return (
              <g key={est.estimate_id} transform={`translate(0, ${y})`}>
                <text x={MARGIN.l - 8} y={BAR_H * 0.7}
                  textAnchor="end" fill="#b8cdcd" fontSize={11}>{label}</text>
                <StackedBar estimate={est} maxSavings={maxSavings} />
              </g>
            );
          })}

          {/* X-axis */}
          {[0, 0.25, 0.5, 0.75, 1].map(t => {
            const x = MARGIN.l + t * (W - MARGIN.l - MARGIN.r);
            const val = t * maxSavings;
            return (
              <g key={t}>
                <line x1={x} y1={MARGIN.t + 30} x2={x} y2={MARGIN.t + 30 + estimates.length * H_PER_ROW}
                  stroke="rgba(143,211,201,0.12)" strokeWidth={0.8} />
                <text x={x} y={MARGIN.t + 30 + estimates.length * H_PER_ROW + 14}
                  textAnchor="middle" fill="#8fd3c9" fontSize={9}>{formatUsd(val)}</text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Assumptions accordion */}
      {estimates[0] && (
        <details className="viz-assumptions">
          <summary>Key assumptions</summary>
          <ul>
            {estimates[0].assumptions.map((a, i) => <li key={i}>{a}</li>)}
          </ul>
        </details>
      )}

      <p className="viz-limitation">
        <strong>Evidence class: {savings.evidence_class}</strong> — {savings.limitation}
      </p>
    </div>
  );
}

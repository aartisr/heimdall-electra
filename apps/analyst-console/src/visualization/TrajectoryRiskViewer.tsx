// @ts-nocheck

/**
 * TrajectoryRiskViewer — SVG altitude × inclination risk heatmap.
 *
 * Shows:
 *  - Colour heatmap: log₁₀(debris flux) per altitude×inclination cell
 *  - Green overlay: safe launch corridors (below risk threshold)
 *  - Scatter: reference launch profile risk scores
 *  - Toggle: "full population" vs "tracked only" flux view
 *  - Colour scale legend
 *
 * Design: pure SVG + React, responsive via viewBox, keyboard accessible.
 */

import React, { useState } from "react";
import { RiskField, RiskFieldCell, SafeCorridor, ProfileScore } from "./types";
import { linearScale, heatmapColor, formatProbability } from "./utils";

// ---------------------------------------------------------------------------
// Chart dimensions
// ---------------------------------------------------------------------------

const CHART = { w: 640, h: 380, ml: 70, mr: 80, mt: 30, mb: 55 } as const;
const PW = CHART.w - CHART.ml - CHART.mr;
const PH = CHART.h - CHART.mt - CHART.mb;

const INC_MIN = 0,  INC_MAX = 180;
const ALT_MIN = 200, ALT_MAX = 2000;
const FLUX_LOG_MIN = -14, FLUX_LOG_MAX = -6;

const RISK_LEVEL_COLORS: Record<string, string> = {
  very_low:  "#247969",
  low:       "#a3d977",
  moderate:  "#f5c76d",
  high:      "#ff9f68",
  very_high: "#c0392b",
};

function xPos(inc: number) {
  return CHART.ml + linearScale(inc, INC_MIN, INC_MAX) * PW;
}
function yPos(alt: number) {
  return CHART.mt + (1 - linearScale(alt, ALT_MIN, ALT_MAX)) * PH;
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function HeatmapCells({ cells, useFullFlux }: { cells: RiskFieldCell[]; useFullFlux: boolean }) {
  const cellW = PW / 18;
  const cellH = PH / 18;

  return (
    <g aria-label="Risk heatmap cells">
      {cells.map((cell, i) => {
        const flux = useFullFlux ? cell.flux_full : cell.flux_tracked;
        const logFlux = flux > 0 ? Math.log10(flux) : FLUX_LOG_MIN;
        const t = linearScale(logFlux, FLUX_LOG_MIN, FLUX_LOG_MAX);
        const color = heatmapColor(t);
        const x = xPos(cell.inclination_deg) - cellW / 2;
        const y = yPos(cell.altitude_km) - cellH / 2;
        return (
          <rect key={i} x={x} y={y} width={cellW} height={cellH}
            fill={color} opacity={0.85}
          >
            <title>
              Alt {cell.altitude_km.toFixed(0)} km, Inc {cell.inclination_deg.toFixed(0)}°
              — flux {flux.toExponential(1)} /m²/yr
              — dark risk {(cell.dark_risk_fraction * 100).toFixed(0)}%
            </title>
          </rect>
        );
      })}
    </g>
  );
}

function SafeCorridorLayer({ corridors }: { corridors: SafeCorridor[] }) {
  return (
    <g aria-label="Safe launch corridors">
      {corridors.map(c => {
        const x = xPos(c.inclination_min_deg);
        const y = yPos(c.altitude_max_km);
        const w = xPos(c.inclination_max_deg) - x;
        const h = yPos(c.altitude_min_km) - y;
        if (w <= 0 || h <= 0) return null;
        return (
          <rect key={c.corridor_id} x={x} y={y} width={w} height={Math.abs(h)}
            fill="none" stroke="#5df5d4" strokeWidth={1.5} opacity={0.7}
          >
            <title>
              Safe corridor: P_collision &lt; {c.max_collision_probability.toExponential(1)}
              (margin ×{c.risk_margin_factor.toFixed(0)})
            </title>
          </rect>
        );
      })}
    </g>
  );
}

function ProfileScatterLayer({ scores }: { scores: ProfileScore[] }) {
  return (
    <g aria-label="Launch profile risk scores">
      {scores.map(score => {
        // We don't have inclination on the score, use a rough mapping from profile_id
        const INC_MAP: Record<string, number> = {
          "iss-resupply-400km": 51.6,
          "sun-sync-600km": 97.8,
          "leo-megaconstellation-550km": 53,
          "polar-science-800km": 98.6,
          "debris-belt-crossing-750km": 86.4,
        };
        const ALT_MAP: Record<string, number> = {
          "iss-resupply-400km": 400,
          "sun-sync-600km": 600,
          "leo-megaconstellation-550km": 550,
          "polar-science-800km": 800,
          "debris-belt-crossing-750km": 750,
        };
        const inc = INC_MAP[score.profile_id] ?? 90;
        const alt = ALT_MAP[score.profile_id] ?? 500;
        const cx = xPos(inc);
        const cy = yPos(alt);
        const color = RISK_LEVEL_COLORS[score.risk_level] ?? "#888";
        const label = score.profile_id.split("-").slice(0, 2).join(" ");
        return (
          <g key={score.profile_id}>
            <circle cx={cx} cy={cy} r={7} fill={color} stroke="#091617" strokeWidth={1.5}>
              <title>
                {score.profile_id}
                — P={formatProbability(score.cumulative_collision_probability)}
                — dark risk {(score.dark_risk_fraction * 100).toFixed(0)}%
                — level: {score.risk_level}
              </title>
            </circle>
            <text x={cx + 9} y={cy + 4} fill="#eef5f5" fontSize={8}>{label}</text>
          </g>
        );
      })}
    </g>
  );
}

function ColorScaleLegend() {
  const steps = 20;
  const bh = PH / steps;
  return (
    <g aria-label="Colour scale legend">
      {Array.from({ length: steps }, (_, i) => {
        const t = 1 - i / steps;
        const y = CHART.mt + (i / steps) * PH;
        return <rect key={i} x={CHART.ml + PW + 6} y={y} width={16} height={bh + 1} fill={heatmapColor(t)} />;
      })}
      <text x={CHART.ml + PW + 26} y={CHART.mt + 8}   fill="#8fd3c9" fontSize={9} textAnchor="start">High flux</text>
      <text x={CHART.ml + PW + 26} y={CHART.mt + PH}   fill="#8fd3c9" fontSize={9} textAnchor="start">Low flux</text>
      {/* Safe corridor legend */}
      <rect x={CHART.ml + PW + 6} y={CHART.mt + PH / 2} width={16} height={12} fill="none" stroke="#5df5d4" strokeWidth={1.5} />
      <text x={CHART.ml + PW + 26} y={CHART.mt + PH / 2 + 9} fill="#5df5d4" fontSize={9}>Safe corridor</text>
    </g>
  );
}

function AxisLabels() {
  const incs = [0, 30, 60, 90, 120, 150, 180];
  const alts = [200, 500, 800, 1000, 1400, 2000];
  return (
    <g fill="#8fd3c9" fontSize={10} aria-hidden="true">
      {incs.map(i => (
        <text key={i} x={xPos(i)} y={CHART.mt + PH + 14} textAnchor="middle">{i}°</text>
      ))}
      {alts.map(a => (
        <text key={a} x={CHART.ml - 6} y={yPos(a) + 3} textAnchor="end">{a}</text>
      ))}
      <text x={CHART.ml + PW / 2} y={CHART.h - 8} textAnchor="middle" fontSize={11}>Orbital inclination (°)</text>
      <text transform={`translate(14,${CHART.mt + PH / 2}) rotate(-90)`} textAnchor="middle" fontSize={11}>Altitude (km)</text>
    </g>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

interface TrajectoryRiskViewerProps {
  riskField: RiskField;
  className?: string;
}

export function TrajectoryRiskViewer({ riskField, className }: TrajectoryRiskViewerProps) {
  const [useFullFlux, setUseFullFlux] = useState(true);

  const totalDark = riskField.profile_scores.length > 0
    ? riskField.profile_scores.reduce((s, p) => s + p.dark_risk_fraction, 0) / riskField.profile_scores.length
    : 0;

  return (
    <div className={`viz-card ${className ?? ""}`.trim()}>
      <h3 className="viz-card-title">Trajectory Risk Field — Safe Launch Corridors</h3>

      <div className="viz-stat-row">
        <div className="viz-stat">
          <span className="viz-stat-value is-accent-teal">{riskField.safe_corridors.length}</span>
          <span className="viz-stat-label">Safe corridors identified</span>
        </div>
        <div className="viz-stat">
          <span className="viz-stat-value is-accent-orange">{(totalDark * 100).toFixed(0)}%</span>
          <span className="viz-stat-label">Average dark risk fraction (radar-invisible)</span>
        </div>
        <div className="viz-stat">
          <span className="viz-stat-value">{riskField.profile_scores.length}</span>
          <span className="viz-stat-label">Reference launch profiles scored</span>
        </div>
      </div>

      <div className="viz-toggle-row" role="group" aria-label="Flux display toggle">
        <button
          type="button"
          className={`toggle-btn ${useFullFlux ? "active" : ""}`}
          onClick={() => setUseFullFlux(true)}
        >Full population (HEIMDALL)</button>
        <button
          type="button"
          className={`toggle-btn ${!useFullFlux ? "active" : ""}`}
          onClick={() => setUseFullFlux(false)}
        >Tracked only (radar)</button>
      </div>

      <div className="viz-scroll-x">
        <svg
          viewBox={`0 0 ${CHART.w} ${CHART.h}`}
          role="img"
          aria-labelledby="risk-chart-title"
          aria-describedby="risk-chart-desc"
          className="viz-svg-responsive viz-svg-risk"
        >
          <title id="risk-chart-title">Trajectory risk heatmap — altitude vs inclination</title>
          <desc id="risk-chart-desc">
            Heatmap showing debris flux density by orbital altitude (Y, 200–2000 km)
            and inclination (X, 0–180°). Green bordered rectangles mark safe corridors.
            Coloured circles show scored launch profiles.
          </desc>

          {/* Background */}
          <rect x={CHART.ml} y={CHART.mt} width={PW} height={PH} fill="#102223" />

          <HeatmapCells cells={riskField.risk_field} useFullFlux={useFullFlux} />
          <SafeCorridorLayer corridors={riskField.safe_corridors} />
          <ProfileScatterLayer scores={riskField.profile_scores} />
          <AxisLabels />
          <ColorScaleLegend />
        </svg>
      </div>

      <p className="viz-limitation">
        <strong>Evidence class: {riskField.evidence_class}</strong> — {riskField.limitation}
      </p>
    </div>
  );
}

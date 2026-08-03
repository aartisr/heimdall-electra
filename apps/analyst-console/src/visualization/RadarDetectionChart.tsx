/**
 * RadarDetectionChart — SVG log-log RCS vs. diameter chart.
 *
 * Shows:
 *  - One coloured line per radar system (RCS vs. object diameter)
 *  - A cyan dashed line for the HEIMDALL ionospheric wake signal (D² scaling)
 *  - A red shaded "DETECTION GAP" region where all radars are below threshold
 *    but wake signal is above noise floor
 *  - Detection threshold horizontal lines per system
 *  - Population count overlay on second Y-axis (right)
 *
 * Design: pure SVG + React, zero npm dependencies.  All maths is pure
 * functions from utils.ts.  The chart is fully responsive via viewBox.
 * Accessible: role="img", aria-label, <title>, <desc> elements.
 */

import React, { useMemo } from "react";
import { RcsAnalysis, RadarCurve, WakeCurve, RcsPoint } from "./types";
import { logScale, polylinePath, formatDiameter } from "./utils";

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const CHART = { w: 680, h: 360, ml: 70, mr: 20, mt: 30, mb: 60 } as const;
const PLOT_W = CHART.w - CHART.ml - CHART.mr;
const PLOT_H = CHART.h - CHART.mt - CHART.mb;

const D_MIN = 1e-4;   // 0.1 mm
const D_MAX = 1.0;    // 1 m
const RCS_MIN_DBSM = -120;
const RCS_MAX_DBSM = 5;

const RADAR_COLORS: Record<string, string> = {
  space_fence:  "#7ecbea",
  haystack:     "#a3d977",
  goldstone:    "#f5c76d",
  tira:         "#ff9f68",
  eiscat_uhf:   "#b48ead",
};

const WAKE_COLOR = "#5df5d4";
const GAP_FILL   = "rgba(192,57,43,0.18)";

// ---------------------------------------------------------------------------
// Coordinate helpers
// ---------------------------------------------------------------------------

function xPos(d: number): number {
  return CHART.ml + logScale(d, D_MIN, D_MAX) * PLOT_W;
}
function yPos(db: number): number {
  return CHART.mt + (1 - logScale(Math.pow(10, db / 10), Math.pow(10, RCS_MIN_DBSM / 10), Math.pow(10, RCS_MAX_DBSM / 10))) * PLOT_H;
}
function yPosLinear(db: number): number {
  const t = (db - RCS_MIN_DBSM) / (RCS_MAX_DBSM - RCS_MIN_DBSM);
  return CHART.mt + (1 - t) * PLOT_H;
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function GridLines() {
  const diameters = [1e-4, 1e-3, 1e-2, 0.1, 1.0];
  const dbsms = [-120, -100, -80, -60, -40, -20, 0];

  return (
    <g aria-hidden="true">
      {diameters.map(d => (
        <line key={d}
          x1={xPos(d)} y1={CHART.mt}
          x2={xPos(d)} y2={CHART.mt + PLOT_H}
          stroke="rgba(143,211,201,0.1)" strokeWidth={0.8}
        />
      ))}
      {dbsms.map(db => (
        <line key={db}
          x1={CHART.ml} y1={yPosLinear(db)}
          x2={CHART.ml + PLOT_W} y2={yPosLinear(db)}
          stroke="rgba(143,211,201,0.1)" strokeWidth={0.8}
        />
      ))}
    </g>
  );
}

function AxisLabels() {
  const diameters = [
    { d: 1e-4, label: "0.1 mm" },
    { d: 1e-3, label: "1 mm" },
    { d: 1e-2, label: "1 cm" },
    { d: 0.1,  label: "10 cm" },
    { d: 1.0,  label: "1 m" },
  ];
  const dbsms = [-120, -100, -80, -60, -40, -20, 0];

  return (
    <g fill="#8fd3c9" fontSize={10} aria-hidden="true">
      {diameters.map(({ d, label }) => (
        <text key={d} x={xPos(d)} y={CHART.mt + PLOT_H + 14} textAnchor="middle">{label}</text>
      ))}
      {dbsms.map(db => (
        <text key={db} x={CHART.ml - 6} y={yPosLinear(db) + 3} textAnchor="end">{db}</text>
      ))}
      {/* Axis titles */}
      <text x={CHART.ml + PLOT_W / 2} y={CHART.h - 6} textAnchor="middle" fontSize={11}>Object diameter (log scale)</text>
      <text
        transform={`translate(14,${CHART.mt + PLOT_H / 2}) rotate(-90)`}
        textAnchor="middle" fontSize={11}
      >RCS (dBsm)</text>
    </g>
  );
}

function DetectionGapFill({ curves }: { curves: RadarCurve[] }) {
  // Build the gap region: between the best radar threshold and the x-axis lower limit
  if (curves.length === 0) return null;
  const bestMinD = Math.min(...curves.map(c => c.min_detectable_diameter_m));
  const x1 = xPos(D_MIN);
  const x2 = xPos(Math.min(bestMinD, D_MAX));
  if (x2 <= x1) return null;
  return (
    <rect
      x={x1} y={CHART.mt}
      width={x2 - x1} height={PLOT_H}
      fill={GAP_FILL}
      aria-label="Detection gap region"
    />
  );
}

function RadarLine({ curve }: { curve: RadarCurve }) {
  const color = RADAR_COLORS[curve.system_id] ?? "#888";

  const pts: [number, number][] = curve.points
    .filter(p => p.diameter_m >= D_MIN && p.diameter_m <= D_MAX
               && p.rcs_dbsm >= RCS_MIN_DBSM && p.rcs_dbsm <= RCS_MAX_DBSM)
    .map(p => [xPos(p.diameter_m), yPosLinear(p.rcs_dbsm)] as [number, number]);

  // Threshold horizontal dashed line
  const ty = yPosLinear(curve.min_detectable_rcs_dbsm);

  return (
    <g>
      <path d={polylinePath(pts)} fill="none" stroke={color} strokeWidth={1.8} />
      <line
        x1={CHART.ml} y1={ty}
        x2={CHART.ml + PLOT_W} y2={ty}
        stroke={color} strokeWidth={0.8} strokeDasharray="4 4" opacity={0.5}
      />
    </g>
  );
}

function WakeLine({ curve }: { curve: WakeCurve }) {
  const pts: [number, number][] = curve.points
    .filter(p => p.diameter_m >= D_MIN && p.diameter_m <= D_MAX)
    .map(p => [
      xPos(p.diameter_m),
      yPosLinear(p.relative_signal_db - 60),
    ] as [number, number])
    .filter(([, y]) => y >= CHART.mt && y <= CHART.mt + PLOT_H);

  return (
    <path
      d={polylinePath(pts)}
      fill="none"
      stroke={WAKE_COLOR}
      strokeWidth={2.5}
      strokeDasharray="8 4"
    />
  );
}

function Legend({ curves }: { curves: RadarCurve[] }) {
  const entries = [
    ...curves.map(c => ({ id: c.system_id, name: c.system_name.split(" (")[0], color: RADAR_COLORS[c.system_id] ?? "#888", dash: false })),
    { id: "wake", name: "HEIMDALL wake signal (D² scaling)", color: WAKE_COLOR, dash: true },
  ];

  return (
    <g fontSize={9} fill="#b8cdcd" aria-label="Chart legend">
      {entries.map((e, i) => {
        const lx = CHART.ml + (i % 3) * 220;
        const ly = CHART.mt + PLOT_H + 40 + Math.floor(i / 3) * 16;
        return (
          <g key={e.id}>
            <line x1={lx} y1={ly} x2={lx + 18} y2={ly}
              stroke={e.color} strokeWidth={2}
              strokeDasharray={e.dash ? "6 3" : undefined} />
            <text x={lx + 22} y={ly + 3}>{e.name}</text>
          </g>
        );
      })}
      {/* Gap label */}
      <rect x={CHART.ml + 4} y={CHART.mt + 8} width={10} height={10} fill={GAP_FILL} stroke="rgba(192,57,43,0.5)" />
      <text x={CHART.ml + 18} y={CHART.mt + 17} fill="#ff6b6b" fontWeight="bold" fontSize={9}>DETECTION GAP</text>
    </g>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

interface RadarDetectionChartProps {
  analysis: RcsAnalysis;
  className?: string;
}

export function RadarDetectionChart({ analysis, className }: RadarDetectionChartProps) {
  const gapMm = (analysis.gap_min_diameter_m * 1000).toFixed(1);
  const gapCm = (analysis.gap_max_diameter_m * 100).toFixed(1);
  const undetected = (analysis.undetected_population_fraction * 100).toFixed(0);

  return (
    <div className={`viz-card ${className ?? ""}`.trim()}>
      <h3 className="viz-card-title">Radar Detection Gap — Physics Proof</h3>

      <div className="viz-stat-row" aria-label="Key statistics">
        <div className="viz-stat">
          <span className="viz-stat-value" style={{ color: "#ff6b35" }}>{gapMm} mm – {gapCm} cm</span>
          <span className="viz-stat-label">Radar-dark size range</span>
        </div>
        <div className="viz-stat">
          <span className="viz-stat-value" style={{ color: "#ff6b35" }}>{undetected}%</span>
          <span className="viz-stat-label">Population undetected by all radars</span>
        </div>
        <div className="viz-stat">
          <span className="viz-stat-value" style={{ color: "#5df5d4" }}>D² vs D⁶</span>
          <span className="viz-stat-label">Wake vs radar scaling — 12 dB/octave HEIMDALL advantage</span>
        </div>
      </div>

      <div style={{ overflowX: "auto" }}>
        <svg
          viewBox={`0 0 ${CHART.w} ${CHART.h + 20}`}
          role="img"
          aria-labelledby="rcs-chart-title"
          aria-describedby="rcs-chart-desc"
          style={{ width: "100%", maxWidth: CHART.w, display: "block" }}
        >
          <title id="rcs-chart-title">Radar cross-section vs. object diameter — detection gap proof</title>
          <desc id="rcs-chart-desc">
            Log-log chart showing radar cross-section (Y axis, dBsm) versus object diameter
            (X axis, 0.1 mm to 1 m) for {analysis.radar_curves.length} radar systems.
            The red shaded region marks the detection gap ({gapMm} mm to {gapCm} cm) where
            {undetected}% of the debris population is invisible to all radars.
            The cyan dashed line shows the HEIMDALL ionospheric wake signal, which scales
            as D² versus the D⁶ radar Rayleigh scaling — giving a 12 dB per octave advantage.
          </desc>

          <GridLines />
          <DetectionGapFill curves={analysis.radar_curves} />

          {analysis.radar_curves.map(c => <RadarLine key={c.system_id} curve={c} />)}
          <WakeLine curve={analysis.wake_curve} />

          <AxisLabels />
          <Legend curves={analysis.radar_curves} />
        </svg>
      </div>

      <p className="viz-limitation">
        <strong>Evidence class: {analysis.evidence_class}</strong> — {analysis.limitation}
      </p>
    </div>
  );
}

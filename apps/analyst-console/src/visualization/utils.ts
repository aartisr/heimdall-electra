/**
 * Shared math utilities for visualization rendering.
 * All functions are pure, stateless, and side-effect-free.
 */

// ---------------------------------------------------------------------------
// Number formatting
// ---------------------------------------------------------------------------

export function formatUsd(value: number): string {
  if (value >= 1e9) return `$${(value / 1e9).toFixed(1)}B`;
  if (value >= 1e6) return `$${(value / 1e6).toFixed(0)}M`;
  if (value >= 1e3) return `$${(value / 1e3).toFixed(0)}K`;
  return `$${value.toFixed(0)}`;
}

export function formatCount(value: number): string {
  if (value >= 1e9) return `${(value / 1e9).toFixed(1)}B`;
  if (value >= 1e6) return `${(value / 1e6).toFixed(0)}M`;
  if (value >= 1e3) return `${(value / 1e3).toFixed(0)}K`;
  return `${value}`;
}

export function formatDiameter(m: number): string {
  if (m < 0.001) return `${(m * 1000).toFixed(1)} mm`;
  if (m < 0.1)   return `${(m * 100).toFixed(1)} cm`;
  return `${m.toFixed(2)} m`;
}

export function formatProbability(p: number): string {
  if (p === 0) return "0";
  if (p < 1e-6) return p.toExponential(1);
  if (p < 0.001) return `${(p * 1e6).toFixed(0)} ppm`;
  return `${(p * 100).toFixed(2)}%`;
}

// ---------------------------------------------------------------------------
// Scale utilities
// ---------------------------------------------------------------------------

/** Map a value in [domainMin, domainMax] to [0, 1]. */
export function linearScale(value: number, domainMin: number, domainMax: number): number {
  if (domainMax === domainMin) return 0;
  return (value - domainMin) / (domainMax - domainMin);
}

/** Map a value in log domain [domainMin, domainMax] to [0, 1]. */
export function logScale(value: number, domainMin: number, domainMax: number): number {
  if (value <= 0 || domainMin <= 0 || domainMax <= 0) return 0;
  const logMin = Math.log10(domainMin);
  const logMax = Math.log10(domainMax);
  if (logMax === logMin) return 0;
  return (Math.log10(value) - logMin) / (logMax - logMin);
}

/** Clamp a value to [min, max]. */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

// ---------------------------------------------------------------------------
// Colour utilities
// ---------------------------------------------------------------------------

export interface RGBA { r: number; g: number; b: number; a: number; }

export function hexToRgba(hex: string, alpha = 1): RGBA {
  const c = hex.replace("#", "");
  return {
    r: parseInt(c.slice(0, 2), 16),
    g: parseInt(c.slice(2, 4), 16),
    b: parseInt(c.slice(4, 6), 16),
    a: alpha,
  };
}

export function rgbaString({ r, g, b, a }: RGBA): string {
  return `rgba(${r},${g},${b},${a.toFixed(3)})`;
}

/** Interpolate between two hex colours at fraction t ∈ [0, 1]. */
export function interpolateColor(hex1: string, hex2: string, t: number): string {
  const c1 = hexToRgba(hex1);
  const c2 = hexToRgba(hex2);
  return rgbaString({
    r: Math.round(c1.r + (c2.r - c1.r) * t),
    g: Math.round(c1.g + (c2.g - c1.g) * t),
    b: Math.round(c1.b + (c2.b - c1.b) * t),
    a: 1,
  });
}

/** Map a normalised [0, 1] value to a red→yellow→green heatmap colour. */
export function heatmapColor(t: number): string {
  const clamped = clamp(t, 0, 1);
  if (clamped < 0.5) return interpolateColor("#247969", "#f5c76d", clamped * 2);
  return interpolateColor("#f5c76d", "#c0392b", (clamped - 0.5) * 2);
}

// ---------------------------------------------------------------------------
// SVG path helpers
// ---------------------------------------------------------------------------

export function svgMoveTo(x: number, y: number): string { return `M${x},${y}`; }
export function svgLineTo(x: number, y: number): string { return `L${x},${y}`; }

export function polylinePath(points: [number, number][]): string {
  if (points.length === 0) return "";
  return points.map(([x, y], i) => (i === 0 ? svgMoveTo(x, y) : svgLineTo(x, y))).join(" ");
}

// ---------------------------------------------------------------------------
// Coordinate projections for globe
// ---------------------------------------------------------------------------

/** Convert orbital parameters to Cartesian on a unit sphere. */
export function orbitalToCartesian(
  altitudeKm: number,
  inclinationDeg: number,
  raanDeg: number,
  earthRadiusKm = 6371,
): { x: number; y: number; z: number } {
  const r = (earthRadiusKm + altitudeKm) / earthRadiusKm; // normalised
  const inc = (inclinationDeg * Math.PI) / 180;
  const raan = (raanDeg * Math.PI) / 180;
  return {
    x: r * Math.sin(inc) * Math.cos(raan),
    y: r * Math.cos(inc),
    z: r * Math.sin(inc) * Math.sin(raan),
  };
}

/** Orthographic projection: (x, y, z) on unit sphere → (cx, cy) on canvas. */
export function orthographicProject(
  x: number, y: number, z: number,
  rotY: number,   // camera rotation around Y axis (radians)
  cx: number, cy: number, scale: number,
): { px: number; py: number; visible: boolean } {
  // Rotate around Y axis
  const cosR = Math.cos(rotY);
  const sinR = Math.sin(rotY);
  const rx = x * cosR - z * sinR;
  const rz = x * sinR + z * cosR;

  return {
    px: cx + rx * scale,
    py: cy - y  * scale,
    visible: rz >= 0,  // only render front hemisphere
  };
}

// ---------------------------------------------------------------------------
// Seeded pseudo-random (deterministic sampling)
// ---------------------------------------------------------------------------

export class SeededRandom {
  private seed: number;
  constructor(seed: number) { this.seed = seed; }

  next(): number {
    this.seed = (this.seed * 1664525 + 1013904223) & 0xffffffff;
    return (this.seed >>> 0) / 0xffffffff;
  }
}

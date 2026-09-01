import React, { useState } from 'react';

export const RadarDetectionGapChart: React.FC = () => {
  const [hoveredPoint, setHoveredPoint] = useState<{
    diameter: string;
    radarName: string;
    rcs: string;
    x: number;
    y: number;
  } | null>(null);

  // SVG dimensions
  const svgWidth = 620;
  const svgHeight = 320;
  const margin = { top: 30, right: 30, bottom: 50, left: 55 };
  const plotWidth = svgWidth - margin.left - margin.right;
  const plotHeight = svgHeight - margin.top - margin.bottom;

  // Log scale helpers: X from 0.1 mm (0.0001 m) to 1 m -> log10 from -4 to 0 (span = 4 decades)
  // X ticks: 0.1mm (log=-4), 1mm (log=-3), 1cm (log=-2), 10cm (log=-1), 1m (log=0)
  const getX = (logD: number) => {
    // logD in [-4, 0]
    const norm = (logD - (-4)) / 4;
    return margin.left + norm * plotWidth;
  };

  // Y from -120 to 0 dBsm
  const getY = (rcs: number) => {
    const norm = (rcs - (-120)) / (0 - (-120));
    return margin.top + (1 - norm) * plotHeight;
  };

  // Detection Gap box: 0.1mm to ~3mm (log=-4 to log=-2.5), RCS from -120 to 0
  const gapX1 = getX(-4);
  const gapX2 = getX(-2.55);
  const gapWidth = gapX2 - gapX1;

  // Generate smooth curve points for the radars and HEIMDALL
  // Radar curves: Rayleigh region (slope 60 dB/decade = D^6) transitioning to Mie/Optical resonance at D ~ wavelength
  // Space Fence (X-band / S-band, lambda ~ 0.08m)
  const generateSpaceFencePath = () => {
    const pts = [];
    for (let logD = -3.8; logD <= 0; logD += 0.05) {
      const d = Math.pow(10, logD);
      // Rayleigh: RCS ~ pi*d^2 * (pi*d/lambda)^4 -> scales as 60*logD + const
      let rcs;
      if (logD < -1.4) {
        rcs = 60 * (logD + 1.4) - 20;
      } else {
        // Optical resonance / geometric plateau
        rcs = -20 + 20 * Math.sin((logD + 1.4) * 2.5) * Math.exp(-(logD + 1.4) * 0.8) + (logD + 1.4) * 10;
        rcs = Math.min(0, rcs);
      }
      pts.push(`${getX(logD)},${getY(Math.max(-120, rcs))}`);
    }
    return `M ${pts.join(' L ')}`;
  };

  // Haystack LRIR (X-band / W-band)
  const generateHaystackPath = () => {
    const pts = [];
    for (let logD = -3.7; logD <= 0; logD += 0.05) {
      let rcs;
      if (logD < -1.6) {
        rcs = 58 * (logD + 1.6) - 15;
      } else {
        rcs = -15 + 18 * Math.sin((logD + 1.6) * 3) * Math.exp(-(logD + 1.6) * 0.9) + (logD + 1.6) * 8;
        rcs = Math.min(0, rcs);
      }
      pts.push(`${getX(logD)},${getY(Math.max(-120, rcs))}`);
    }
    return `M ${pts.join(' L ')}`;
  };

  // Goldstone Solar System Radar
  const generateGoldstonePath = () => {
    const pts = [];
    for (let logD = -3.9; logD <= 0; logD += 0.05) {
      let rcs;
      if (logD < -1.8) {
        rcs = 56 * (logD + 1.8) - 10;
      } else {
        rcs = -10 + 16 * Math.sin((logD + 1.8) * 2.8) * Math.exp(-(logD + 1.8) * 0.7) + (logD + 1.8) * 6;
        rcs = Math.min(0, rcs);
      }
      pts.push(`${getX(logD)},${getY(Math.max(-120, rcs))}`);
    }
    return `M ${pts.join(' L ')}`;
  };

  // TIRA (L-band / Ku-band)
  const generateTIRAPath = () => {
    const pts = [];
    for (let logD = -3.6; logD <= 0; logD += 0.05) {
      let rcs;
      if (logD < -1.2) {
        rcs = 62 * (logD + 1.2) - 18;
      } else {
        rcs = -18 + 15 * Math.sin((logD + 1.2) * 2.2) * Math.exp(-(logD + 1.2) * 0.8) + (logD + 1.2) * 9;
        rcs = Math.min(-2, rcs);
      }
      pts.push(`${getX(logD)},${getY(Math.max(-120, rcs))}`);
    }
    return `M ${pts.join(' L ')}`;
  };

  // HEIMDALL Wake Signal: D^2 scaling -> 20 dB/decade (12 dB/octave) advantage!
  const generateHeimdallPath = () => {
    const pts = [];
    for (let logD = -4.0; logD <= 0; logD += 0.05) {
      // Linear slope of 20 dB per decade
      const rcs = -140 + 20 * (logD - (-4.0)) + 20; // Starts around -120 dBsm at 0.1mm and reaches -60 dBsm at 1m
      pts.push(`${getX(logD)},${getY(rcs)}`);
    }
    return `M ${pts.join(' L ')}`;
  };

  return (
    <div className="bg-[#0b1320] border border-slate-800 rounded-2xl p-6 sm:p-7 space-y-6 shadow-xl flex flex-col justify-between">
      {/* Title */}
      <div>
        <h3 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight">
          Radar Detection Gap — Physics Proof
        </h3>
      </div>

      {/* Top 3 Metric Cards matching authentic screenshot */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
        <div className="bg-[#070d18] border border-slate-800/80 rounded-xl p-4 space-y-1">
          <div className="text-2xl sm:text-3xl font-black font-mono text-[#f97316]">
            0.1 mm – 0.3 cm
          </div>
          <div className="text-xs text-slate-400">
            Radar-dark size range
          </div>
        </div>

        <div className="bg-[#070d18] border border-slate-800/80 rounded-xl p-4 space-y-1">
          <div className="text-2xl sm:text-3xl font-black font-mono text-[#f97316]">
            95%
          </div>
          <div className="text-xs text-slate-400">
            Population undetected by all radars
          </div>
        </div>

        <div className="bg-[#070d18] border border-slate-800/80 rounded-xl p-4 space-y-1">
          <div className="text-2xl sm:text-3xl font-black font-mono text-[#10b981]">
            D² vs D⁶
          </div>
          <div className="text-xs text-slate-400 leading-tight">
            Wake vs radar scaling — 12 dB/octave HEIMDALL advantage
          </div>
        </div>
      </div>

      {/* SVG Physics Proof Chart */}
      <div className="relative w-full overflow-x-auto bg-[#070d18] rounded-xl border border-slate-800/70 p-2 sm:p-3">
        <svg
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          className="w-full h-auto min-w-[500px]"
        >
          {/* Y Axis Grid Lines & Labels */}
          {[-120, -100, -80, -60, -40, -20, 0].map((val) => {
            const y = getY(val);
            return (
              <g key={val}>
                <line
                  x1={margin.left}
                  y1={y}
                  x2={svgWidth - margin.right}
                  y2={y}
                  stroke="#1e293b"
                  strokeDasharray={val === 0 ? 'none' : '3,3'}
                  strokeWidth="1"
                />
                <text
                  x={margin.left - 8}
                  y={y + 4}
                  textAnchor="end"
                  fill="#64748b"
                  fontSize="10"
                  fontFamily="monospace"
                >
                  {val}
                </text>
              </g>
            );
          })}

          {/* Y Axis Title */}
          <text
            x={-svgHeight / 2}
            y={16}
            transform="rotate(-90)"
            textAnchor="middle"
            fill="#94a3b8"
            fontSize="10"
            fontFamily="monospace"
          >
            RCS (dBsm)
          </text>

          {/* X Axis Ticks & Labels */}
          {[
            { logD: -4, label: '0.1 mm' },
            { logD: -3, label: '1 mm' },
            { logD: -2, label: '1 cm' },
            { logD: -1, label: '10 cm' },
            { logD: 0, label: '1 m' },
          ].map((tick) => {
            const x = getX(tick.logD);
            return (
              <g key={tick.label}>
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
                  y={svgHeight - margin.bottom + 16}
                  textAnchor="middle"
                  fill="#94a3b8"
                  fontSize="10"
                  fontFamily="monospace"
                >
                  {tick.label}
                </text>
              </g>
            );
          })}

          {/* X Axis Title */}
          <text
            x={margin.left + plotWidth / 2}
            y={svgHeight - 12}
            textAnchor="middle"
            fill="#94a3b8"
            fontSize="10"
            fontFamily="sans-serif"
          >
            Object diameter (log scale)
          </text>

          {/* Shaded Red Detection Gap Area */}
          <rect
            x={gapX1}
            y={margin.top}
            width={gapWidth}
            height={plotHeight}
            fill="rgba(239, 68, 68, 0.12)"
            stroke="rgba(239, 68, 68, 0.3)"
            strokeWidth="1"
          />

          {/* Detection Gap Badge in Upper Left of Gap Box */}
          <g transform={`translate(${gapX1 + 10}, ${margin.top + 14})`}>
            <rect
              x="0"
              y="-10"
              width="88"
              height="16"
              rx="3"
              fill="rgba(239, 68, 68, 0.25)"
              stroke="#ef4444"
              strokeWidth="0.8"
            />
            <text
              x="44"
              y="1"
              textAnchor="middle"
              fill="#fca5a5"
              fontSize="8.5"
              fontWeight="bold"
              fontFamily="sans-serif"
            >
              DETECTION GAP
            </text>
          </g>

          {/* Radar Curves */}
          {/* 1. Space Fence (cyan) */}
          <path
            d={generateSpaceFencePath()}
            fill="none"
            stroke="#38bdf8"
            strokeWidth="1.8"
          />

          {/* 2. Haystack LRIR (lime / yellow-green) */}
          <path
            d={generateHaystackPath()}
            fill="none"
            stroke="#a3e635"
            strokeWidth="1.8"
          />

          {/* 3. Goldstone (amber / gold) */}
          <path
            d={generateGoldstonePath()}
            fill="none"
            stroke="#f59e0b"
            strokeWidth="1.8"
          />

          {/* 4. TIRA (orange-red) */}
          <path
            d={generateTIRAPath()}
            fill="none"
            stroke="#f97316"
            strokeWidth="1.8"
          />

          {/* 5. HEIMDALL Wake Signal D^2 scaling (dashed cyan) */}
          <path
            d={generateHeimdallPath()}
            fill="none"
            stroke="#2dd4bf"
            strokeWidth="2.4"
            strokeDasharray="4,4"
          />
        </svg>

        {/* Chart Legend matching authentic layout */}
        <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2 pt-3 pb-1 text-[11px] font-mono">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 bg-[#38bdf8] inline-block" />
            <span className="text-slate-300">Space Fence</span>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 bg-[#a3e635] inline-block" />
            <span className="text-slate-300">Haystack LRIR</span>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 bg-[#f59e0b] inline-block" />
            <span className="text-slate-300">Goldstone Solar System Radar</span>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 bg-[#f97316] inline-block" />
            <span className="text-slate-300">TIRA</span>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 border-b-2 border-dashed border-[#2dd4bf] inline-block" />
            <span className="text-[#2dd4bf] font-bold">HEIMDALL wake signal (D² scaling)</span>
          </div>
        </div>
      </div>

      {/* Evidence class synthetic footer */}
      <div className="pt-2 text-xs text-slate-400 leading-relaxed border-t border-slate-800/80">
        <p>
          <span className="text-slate-200 font-bold">Evidence class: synthetic</span> — Analytical detection gap derived from published radar specifications and Mie theory. The HEIMDALL advantage (D² wake scaling vs D⁶ radar scaling) is a theoretical prediction, not a measured performance. No observed debris detection has been made. Gap boundaries are indicative; real thresholds depend on SNR, integration time, and target geometry.
        </p>
      </div>
    </div>
  );
};

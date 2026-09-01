import React, { useState } from 'react';

interface MissionProfile {
  name: string;
  inc: number;
  alt: number;
  description: string;
  fluxHeimdall: number; // /m^2/yr
  fluxTracked: number;
  darkFraction: number; // %
}

const MISSIONS: MissionProfile[] = [
  {
    name: 'iss resupply',
    inc: 51.6,
    alt: 420,
    description: 'Commercial Cargo & Crewed ISS trajectory',
    fluxHeimdall: 4.8e-4,
    fluxTracked: 1.2e-5,
    darkFraction: 97.5,
  },
  {
    name: 'leo megaconstellation',
    inc: 53.0,
    alt: 550,
    description: 'Starlink / Kuiper operational altitude shell',
    fluxHeimdall: 8.2e-4,
    fluxTracked: 2.1e-5,
    darkFraction: 97.4,
  },
  {
    name: 'debris belt',
    inc: 88.0,
    alt: 780,
    description: 'Fengyun-1C & Iridium/Cosmos debris concentration',
    fluxHeimdall: 2.9e-3,
    fluxTracked: 8.4e-5,
    darkFraction: 97.1,
  },
  {
    name: 'sun sync',
    inc: 97.8,
    alt: 600,
    description: 'Earth Observation / SSO standard insertion',
    fluxHeimdall: 1.4e-3,
    fluxTracked: 3.8e-5,
    darkFraction: 97.3,
  },
  {
    name: 'polar science',
    inc: 98.2,
    alt: 800,
    description: 'Meteorological & environmental polar orbits',
    fluxHeimdall: 2.1e-3,
    fluxTracked: 6.2e-5,
    darkFraction: 97.0,
  },
];

export const TrajectoryRiskFieldChart: React.FC = () => {
  const [viewMode, setViewMode] = useState<'heimdall' | 'tracked'>('heimdall');
  const [selectedMission, setSelectedMission] = useState<MissionProfile | null>(null);

  // SVG dimensions
  const svgWidth = 620;
  const svgHeight = 320;
  const margin = { top: 25, right: 75, bottom: 45, left: 55 };
  const plotWidth = svgWidth - margin.left - margin.right;
  const plotHeight = svgHeight - margin.top - margin.bottom;

  // X: Inclination 0 to 180 deg
  const getX = (inc: number) => {
    return margin.left + (inc / 180) * plotWidth;
  };

  // Y: Altitude from 200 to 2000 km (linear or piecewise as on chart)
  const getY = (alt: number) => {
    const norm = (alt - 200) / (2000 - 200);
    return margin.top + (1 - norm) * plotHeight;
  };

  return (
    <div className="bg-[#0b1320] border border-slate-800 rounded-2xl p-6 sm:p-7 space-y-6 shadow-xl flex flex-col justify-between">
      {/* Title */}
      <div>
        <h3 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight">
          Trajectory Risk Field — Safe Launch Corridors
        </h3>
      </div>

      {/* Top 3 Metric Cards matching authentic screenshot */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
        <div className="bg-[#070d18] border border-slate-800/80 rounded-xl p-4 space-y-1">
          <div className="text-2xl sm:text-3xl font-black font-mono text-white">
            0
          </div>
          <div className="text-xs text-slate-400">
            Safe corridors identified
          </div>
        </div>

        <div className="bg-[#070d18] border border-slate-800/80 rounded-xl p-4 space-y-1">
          <div className="text-2xl sm:text-3xl font-black font-mono text-[#f97316]">
            100%
          </div>
          <div className="text-xs text-slate-400 leading-tight">
            Average dark risk fraction (radar-invisible)
          </div>
        </div>

        <div className="bg-[#070d18] border border-slate-800/80 rounded-xl p-4 space-y-1">
          <div className="text-2xl sm:text-3xl font-black font-mono text-white">
            5
          </div>
          <div className="text-xs text-slate-400">
            Reference launch profiles scored
          </div>
        </div>
      </div>

      {/* Mode Switcher Toggle Pills */}
      <div className="flex items-center gap-2.5">
        <button
          onClick={() => setViewMode('heimdall')}
          className={`px-4 py-1.5 rounded-full text-xs font-bold transition-all ${
            viewMode === 'heimdall'
              ? 'bg-slate-800 text-white border border-slate-600 shadow-md'
              : 'bg-[#070d18] text-slate-400 border border-slate-800 hover:text-slate-200'
          }`}
        >
          Full population (HEIMDALL)
        </button>

        <button
          onClick={() => setViewMode('tracked')}
          className={`px-4 py-1.5 rounded-full text-xs font-bold transition-all ${
            viewMode === 'tracked'
              ? 'bg-slate-800 text-white border border-slate-600 shadow-md'
              : 'bg-[#070d18] text-slate-400 border border-slate-800 hover:text-slate-200'
          }`}
        >
          Tracked only (radar)
        </button>
      </div>

      {/* 2D Risk Field Heatmap SVG */}
      <div className="relative w-full overflow-x-auto bg-[#070d18] rounded-xl border border-slate-800/70 p-2 sm:p-3">
        <svg
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          className="w-full h-auto min-w-[500px]"
        >
          <defs>
            {/* Heatmap vertical gradient: High flux in LEO debris bands */}
            <linearGradient id="heimdallHeatmap" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#b91c1c" stopOpacity="0.85" />
              <stop offset="35%" stopColor="#dc2626" stopOpacity="0.9" />
              <stop offset="70%" stopColor="#c2410c" stopOpacity="0.9" />
              <stop offset="100%" stopColor="#9a3412" stopOpacity="0.85" />
            </linearGradient>

            <linearGradient id="trackedHeatmap" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#7f1d1d" stopOpacity="0.5" />
              <stop offset="35%" stopColor="#991b1b" stopOpacity="0.6" />
              <stop offset="70%" stopColor="#854d0e" stopOpacity="0.6" />
              <stop offset="100%" stopColor="#14532d" stopOpacity="0.7" />
            </linearGradient>

            {/* Colorbar legend gradient */}
            <linearGradient id="colorbarGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#dc2626" />
              <stop offset="30%" stopColor="#ea580c" />
              <stop offset="60%" stopColor="#eab308" />
              <stop offset="85%" stopColor="#10b981" />
              <stop offset="100%" stopColor="#047857" />
            </linearGradient>
          </defs>

          {/* Heatmap background rectangle */}
          <rect
            x={margin.left}
            y={margin.top}
            width={plotWidth}
            height={plotHeight}
            fill={viewMode === 'heimdall' ? 'url(#heimdallHeatmap)' : 'url(#trackedHeatmap)'}
            stroke="#1e293b"
            strokeWidth="1"
          />

          {/* Grid lines for Inclination */}
          {[0, 30, 60, 90, 120, 150, 180].map((inc) => {
            const x = getX(inc);
            return (
              <g key={inc}>
                <line
                  x1={x}
                  y1={margin.top}
                  x2={x}
                  y2={svgHeight - margin.bottom}
                  stroke="rgba(0, 0, 0, 0.3)"
                  strokeWidth="1"
                />
                <text
                  x={x}
                  y={svgHeight - margin.bottom + 16}
                  textAnchor="middle"
                  fill="#94a3b8"
                  fontSize="10"
                  fontFamily="sans-serif"
                >
                  {inc}°
                </text>
              </g>
            );
          })}

          {/* Grid lines for Altitude */}
          {[
            { alt: 2000, label: '2000' },
            { alt: 1400, label: '1400' },
            { alt: 1000, label: '1000' },
            { alt: 800, label: '800' },
            { alt: 500, label: '500' },
            { alt: 200, label: '200' },
          ].map((item) => {
            const y = getY(item.alt);
            return (
              <g key={item.alt}>
                <line
                  x1={margin.left}
                  y1={y}
                  x2={margin.left + plotWidth}
                  y2={y}
                  stroke="rgba(0, 0, 0, 0.25)"
                  strokeWidth="1"
                />
                <text
                  x={margin.left - 8}
                  y={y + 4}
                  textAnchor="end"
                  fill="#94a3b8"
                  fontSize="10"
                  fontFamily="monospace"
                >
                  {item.label}
                </text>
              </g>
            );
          })}

          {/* Axis Titles */}
          <text
            x={-svgHeight / 2}
            y={16}
            transform="rotate(-90)"
            textAnchor="middle"
            fill="#94a3b8"
            fontSize="10"
            fontFamily="sans-serif"
          >
            Altitude (km)
          </text>

          <text
            x={margin.left + plotWidth / 2}
            y={svgHeight - 8}
            textAnchor="middle"
            fill="#94a3b8"
            fontSize="10"
            fontFamily="sans-serif"
          >
            Orbital inclination (°)
          </text>

          {/* Right-side Flux Colorbar Legend */}
          <g transform={`translate(${svgWidth - margin.right + 14}, ${margin.top})`}>
            <rect
              x="0"
              y="0"
              width="10"
              height={plotHeight}
              fill="url(#colorbarGrad)"
              rx="2"
            />
            {/* Colorbar text labels */}
            <text x="16" y="8" fill="#94a3b8" fontSize="8.5" fontFamily="sans-serif">
              High flux
            </text>
            <text x="16" y={plotHeight / 2} fill="#2dd4bf" fontSize="8.5" fontFamily="sans-serif">
              Safe corridor
            </text>
            <text x="16" y={plotHeight - 2} fill="#94a3b8" fontSize="8.5" fontFamily="sans-serif">
              Low flux
            </text>
          </g>

          {/* Plotted Mission Target Markers */}
          {MISSIONS.map((m) => {
            const cx = getX(m.inc);
            const cy = getY(m.alt);
            const isHovered = selectedMission?.name === m.name;

            return (
              <g
                key={m.name}
                className="cursor-pointer group"
                onClick={() => setSelectedMission(m)}
              >
                {/* Marker Circle */}
                <circle
                  cx={cx}
                  cy={cy}
                  r={isHovered ? 6.5 : 5}
                  fill="#f97316"
                  stroke="#ffffff"
                  strokeWidth="1.5"
                  className="transition-all"
                />

                {/* Label next to circle matching screenshot */}
                <text
                  x={cx + 8}
                  y={cy + 3.5}
                  fill="#ffffff"
                  fontSize="9.5"
                  fontWeight="bold"
                  fontFamily="sans-serif"
                  style={{ textShadow: '0 1px 3px rgba(0,0,0,0.9)' }}
                >
                  {m.name}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Evidence class synthetic footer */}
      <div className="pt-2 text-xs text-slate-400 leading-relaxed border-t border-slate-800/80">
        <p>
          <span className="text-slate-200 font-bold">Evidence class: synthetic</span> — Model-based flux computation using synthetic power-law population. Actual collision probability requires validated flux data from real observations. Results are for comparative analysis only. Safe corridors are not operationally certified launch windows.
        </p>
      </div>
    </div>
  );
};

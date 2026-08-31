import React, { useState } from 'react';
import { INITIAL_CONJUNCTIONS } from '../data/mockData';
import { ConjunctionEvent } from '../types';
import { Satellite, AlertTriangle, ShieldAlert, Sliders, RefreshCw, BarChart3, Info } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export const ConjunctionTab: React.FC = () => {
  const [selectedConjunction, setSelectedConjunction] = useState<ConjunctionEvent>(INITIAL_CONJUNCTIONS[0]);
  const [customMissKm, setCustomMissKm] = useState<number>(selectedConjunction.missDistanceKm);
  const [primarySigmaM, setPrimarySigmaM] = useState<number>(50);

  // Calculate probability of collision based on miss distance & sigma
  // P_c ~ exp( - (r_miss^2) / (2 * sigma^2) ) / (2 * pi * sigma^2) * Area
  const computePc = (missKm: number, sigmaM: number) => {
    const rM = missKm * 1000;
    const areaM2 = 20; // 20 m2 combined Hard Body Radius squared area
    const sigma2 = sigmaM * sigmaM;
    const exponent = -(rM * rM) / (2 * sigma2);
    const pc = (areaM2 / (2 * Math.PI * sigma2)) * Math.exp(exponent);
    return Math.min(Math.max(pc, 1e-8), 0.95);
  };

  const currentPc = computePc(customMissKm, primarySigmaM);

  // Generate curve data for Recharts chart
  const curveData = Array.from({ length: 30 }, (_, i) => {
    const distKm = Number((0.05 + i * 0.15).toFixed(2));
    const pcVal = computePc(distKm, primarySigmaM);
    return {
      distKm,
      collisionProbability: pcVal,
      logPc: Math.log10(pcVal + 1e-12),
    };
  });

  const getRiskBadge = (pc: number) => {
    if (pc > 0.001) return { label: 'CRITICAL', color: 'bg-red-950 border-red-700 text-red-400' };
    if (pc > 0.0001) return { label: 'HIGH', color: 'bg-amber-950 border-amber-700 text-amber-400' };
    if (pc > 0.00001) return { label: 'MEDIUM', color: 'bg-yellow-950 border-yellow-700 text-yellow-400' };
    return { label: 'LOW', color: 'bg-emerald-950 border-emerald-700 text-emerald-400' };
  };

  const riskInfo = getRiskBadge(currentPc);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-5 rounded-xl">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <Satellite className="w-5 h-5 text-cyan-400" />
            <h2 className="text-lg font-bold text-slate-100">Satellite Conjunction Risk Calculator</h2>
          </div>
          <p className="text-xs text-slate-400">
            2D Gaussian probability of collision ($P_c$) integration under covariance uncertainty & orbital state propagation.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Conjunction Selector & Details */}
        <div className="space-y-4">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Conjunction Warnings</h3>
          <div className="space-y-2">
            {INITIAL_CONJUNCTIONS.map((event) => (
              <button
                key={event.id}
                onClick={() => {
                  setSelectedConjunction(event);
                  setCustomMissKm(event.missDistanceKm);
                }}
                className={`w-full text-left p-3.5 rounded-xl border transition-all ${
                  selectedConjunction.id === event.id
                    ? 'bg-slate-800 border-cyan-500/60 shadow-lg shadow-cyan-950/30'
                    : 'bg-slate-900 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex justify-between items-start mb-1">
                  <span className="text-xs font-mono font-semibold text-slate-400">{event.id}</span>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                    event.riskLevel === 'CRITICAL' ? 'bg-red-950 border-red-700 text-red-400' :
                    event.riskLevel === 'HIGH' ? 'bg-amber-950 border-amber-700 text-amber-400' :
                    'bg-slate-950 border-slate-700 text-slate-300'
                  }`}>
                    {event.riskLevel}
                  </span>
                </div>
                <div className="text-sm font-bold text-slate-100">{event.primaryObject}</div>
                <div className="text-xs text-slate-400">vs {event.secondaryObject}</div>
                <div className="mt-2 flex justify-between text-[11px] text-slate-500 font-mono">
                  <span>TCA: {new Date(event.tca).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  <span>{event.missDistanceKm} km</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Right 2 cols: Interactive Simulator & Charts */}
        <div className="lg:col-span-2 space-y-6">
          {/* Controls & Computed Result Card */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-5">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center border-b border-slate-800 pb-4 gap-3">
              <div>
                <span className="text-xs font-mono text-cyan-400">{selectedConjunction.id}</span>
                <h3 className="text-base font-bold text-slate-50">
                  {selectedConjunction.primaryObject} &times; {selectedConjunction.secondaryObject}
                </h3>
              </div>
              <div className={`px-3 py-1 rounded-lg border text-xs font-bold font-mono ${riskInfo.color}`}>
                RISK LEVEL: {riskInfo.label}
              </div>
            </div>

            {/* Parameter Sliders */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-slate-950/70 p-4 rounded-lg border border-slate-800">
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-300 font-medium">Miss Distance (km):</span>
                  <span className="font-mono text-cyan-400 font-bold">{customMissKm.toFixed(2)} km</span>
                </div>
                <input
                  type="range"
                  min="0.05"
                  max="5.0"
                  step="0.05"
                  value={customMissKm}
                  onChange={(e) => setCustomMissKm(parseFloat(e.target.value))}
                  className="w-full accent-cyan-400 cursor-pointer"
                />
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-300 font-medium">Position Uncertainty ($\sigma$ in meters):</span>
                  <span className="font-mono text-indigo-400 font-bold">{primarySigmaM} m</span>
                </div>
                <input
                  type="range"
                  min="10"
                  max="200"
                  step="5"
                  value={primarySigmaM}
                  onChange={(e) => setPrimarySigmaM(parseInt(e.target.value))}
                  className="w-full accent-indigo-400 cursor-pointer"
                />
              </div>
            </div>

            {/* Calculated Results Box */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                <span className="text-[11px] text-slate-400 block mb-1">Calculated $P_c$</span>
                <span className="text-lg font-mono font-bold text-cyan-400">
                  {currentPc.toExponential(4)}
                </span>
              </div>
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                <span className="text-[11px] text-slate-400 block mb-1">Relative Speed</span>
                <span className="text-lg font-mono font-bold text-slate-200">
                  {selectedConjunction.relativeVelocityKms} km/s
                </span>
              </div>
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                <span className="text-[11px] text-slate-400 block mb-1">Evidence Class</span>
                <span className="text-xs font-mono font-semibold text-emerald-400 uppercase">
                  {selectedConjunction.evidenceClass}
                </span>
              </div>
            </div>

            {/* Chart */}
            <div className="space-y-2">
              <h4 className="text-xs font-semibold text-slate-300 flex items-center space-x-1.5">
                <BarChart3 className="w-4 h-4 text-cyan-400" />
                <span>$P_c$ Sensitivity Profile vs. Miss Distance (km)</span>
              </h4>
              <div className="h-52 w-full bg-slate-950/60 p-2 rounded-lg border border-slate-800">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={curveData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="pcGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                    <XAxis dataKey="distKm" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                    <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} tickFormatter={(val) => val.toExponential(1)} />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', color: '#f8fafc', fontSize: '12px' }}
                      formatter={(val: number) => [val.toExponential(4), 'Probability of Collision']}
                      labelFormatter={(label) => `Miss Distance: ${label} km`}
                    />
                    <Area type="monotone" dataKey="collisionProbability" stroke="#06b6d4" fillOpacity={1} fill="url(#pcGrad)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

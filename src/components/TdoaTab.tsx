import React, { useState } from 'react';
import { GROUND_STATIONS } from '../data/mockData';
import { GroundStation } from '../types';
import { Radio, Compass, MapPin, Sliders, RefreshCw, Cpu, CheckCircle } from 'lucide-react';

export const TdoaTab: React.FC = () => {
  const [stations, setStations] = useState<GroundStation[]>(GROUND_STATIONS);
  const [selectedTarget, setSelectedTarget] = useState<'DEBRIS-ALPHA' | 'OBJECT-BETA' | 'UNKN-9901'>('DEBRIS-ALPHA');
  const [noiseNs, setNoiseNs] = useState<number>(5);
  const [isSolving, setIsSolving] = useState<boolean>(false);
  const [solvedPos, setSolvedPos] = useState<{ lat: number; lng: number; altKm: number; residualNs: number }>({
    lat: 52.41,
    lng: 12.85,
    altKm: 580,
    residualNs: 1.42,
  });

  const handleSolve = () => {
    setIsSolving(true);
    setTimeout(() => {
      // Simulate non-linear least squares TDOA solution
      const noise = (Math.random() - 0.5) * noiseNs * 0.1;
      setSolvedPos({
        lat: Number((52.41 + noise * 0.05).toFixed(4)),
        lng: Number((12.85 + noise * 0.05).toFixed(4)),
        altKm: Math.round(580 + noise * 2),
        residualNs: Number((1.15 + Math.random() * noiseNs * 0.1).toFixed(2)),
      });
      setIsSolving(false);
    }, 400);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-5 rounded-xl">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <Radio className="w-5 h-5 text-indigo-400" />
            <h2 className="text-lg font-bold text-slate-100">Multi-Node TDOA Kinematic Solver</h2>
          </div>
          <p className="text-xs text-slate-400">
            Hyperbolic Time-Difference-of-Arrival localization solver with sensor delay calibration and noise covariance bounds.
          </p>
        </div>
        <button
          onClick={handleSolve}
          disabled={isSolving}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-slate-50 font-semibold rounded-lg text-xs transition-colors flex items-center space-x-2 shadow-md shrink-0 disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isSolving ? 'animate-spin' : ''}`} />
          <span>{isSolving ? 'Computing Hyperbolas...' : 'Run TDOA Solver'}</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Station Network */}
        <div className="space-y-4">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Ground Station Receiver Network</h3>
          <div className="space-y-3">
            {stations.map((st) => (
              <div key={st.id} className="bg-slate-900 border border-slate-800 p-4 rounded-xl space-y-2">
                <div className="flex justify-between items-start">
                  <div className="flex items-center space-x-2">
                    <MapPin className="w-4 h-4 text-indigo-400" />
                    <span className="text-sm font-bold text-slate-200">{st.name}</span>
                  </div>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${
                    st.status === 'ACTIVE' ? 'bg-emerald-950 border-emerald-700 text-emerald-400' : 'bg-amber-950 border-amber-700 text-amber-400'
                  }`}>
                    {st.status}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-[11px] font-mono text-slate-400">
                  <div>Lat/Lng: {st.lat}°, {st.lng}°</div>
                  <div>Elev: {st.elevationM}m</div>
                  <div>Freq: {st.frequencyGHz} GHz</div>
                  <div>SNR: {st.snrDb} dB</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right 2 cols: Visual Radar Screen & Solution Output */}
        <div className="lg:col-span-2 space-y-6">
          {/* Visual Display */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
            <h3 className="text-sm font-bold text-slate-200 flex items-center space-x-2">
              <Compass className="w-4 h-4 text-cyan-400" />
              <span>Hyperbolic Intersects & Estimated Target Vector</span>
            </h3>

            {/* Radar Canvas representation */}
            <div className="relative h-64 w-full bg-slate-950 rounded-xl border border-slate-800 overflow-hidden flex items-center justify-center">
              {/* Radar Grid Circles */}
              <div className="absolute w-48 h-48 rounded-full border border-indigo-900/40" />
              <div className="absolute w-32 h-32 rounded-full border border-indigo-900/60" />
              <div className="absolute w-16 h-16 rounded-full border border-indigo-900/80" />
              <div className="absolute w-full h-[1px] bg-indigo-950" />
              <div className="absolute h-full w-[1px] bg-indigo-950" />

              {/* Station Dots */}
              <div className="absolute top-10 left-16 flex items-center space-x-1">
                <span className="w-2.5 h-2.5 rounded-full bg-indigo-500 animate-ping" />
                <span className="text-[10px] font-mono text-indigo-300">Boulmer</span>
              </div>
              <div className="absolute top-8 right-20 flex items-center space-x-1">
                <span className="w-2.5 h-2.5 rounded-full bg-indigo-500 animate-ping" />
                <span className="text-[10px] font-mono text-indigo-300">Kiruna</span>
              </div>
              <div className="absolute bottom-12 left-24 flex items-center space-x-1">
                <span className="w-2.5 h-2.5 rounded-full bg-indigo-500 animate-ping" />
                <span className="text-[10px] font-mono text-indigo-300">Svalbard</span>
              </div>

              {/* Solved Target Location */}
              <div className="absolute top-1/2 left-1/2 -translate-x-3 -translate-y-4 flex flex-col items-center">
                <div className="relative">
                  <span className="w-4 h-4 rounded-full bg-cyan-400/30 border border-cyan-400 flex items-center justify-center animate-pulse" />
                  <span className="w-2 h-2 rounded-full bg-cyan-300 absolute inset-1" />
                </div>
                <span className="text-[10px] font-mono font-bold text-cyan-300 bg-slate-900/90 px-1.5 py-0.5 rounded border border-cyan-800/80 mt-1">
                  TARGET: {solvedPos.altKm}km LEO
                </span>
              </div>
            </div>

            {/* Solver Controls */}
            <div className="bg-slate-950/80 p-4 rounded-lg border border-slate-800 space-y-3">
              <div className="flex justify-between text-xs">
                <span className="text-slate-300">Synthetic Clock Jitter Noise (σ_ns):</span>
                <span className="font-mono text-indigo-400 font-bold">{noiseNs} ns</span>
              </div>
              <input
                type="range"
                min="1"
                max="20"
                value={noiseNs}
                onChange={(e) => setNoiseNs(parseInt(e.target.value))}
                className="w-full accent-indigo-400 cursor-pointer"
              />
            </div>

            {/* Solved Vector Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                <span className="text-[11px] text-slate-400 block mb-1">Latitude</span>
                <span className="text-sm font-mono font-bold text-slate-100">{solvedPos.lat}° N</span>
              </div>
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                <span className="text-[11px] text-slate-400 block mb-1">Longitude</span>
                <span className="text-sm font-mono font-bold text-slate-100">{solvedPos.lng}° E</span>
              </div>
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                <span className="text-[11px] text-slate-400 block mb-1">Altitude</span>
                <span className="text-sm font-mono font-bold text-cyan-400">{solvedPos.altKm} km</span>
              </div>
              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                <span className="text-[11px] text-slate-400 block mb-1">TDOA Residual</span>
                <span className="text-sm font-mono font-bold text-emerald-400">{solvedPos.residualNs} ns</span>
              </div>
            </div>

            {/* Orbital Pass Geometry & Doppler Analysis */}
            <div className="bg-slate-950/90 border border-slate-800 rounded-xl p-4 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Cpu className="w-4 h-4 text-cyan-400" />
                  <span className="text-xs font-bold text-slate-200 uppercase tracking-wider">
                    Orbital Pass Doppler & Geometric Dilution of Precision (GDOP)
                  </span>
                </div>
                <span className="text-[10px] font-mono text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-700/60">
                  GDOP: 1.48 (OPTIMAL)
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 font-mono text-[11px]">
                <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800 space-y-1">
                  <div className="text-slate-400 text-[10px]">VHF Doppler Shift (f_0 = 144 MHz)</div>
                  <div className="text-cyan-300 font-bold text-sm">±3.65 kHz</div>
                  <div className="text-slate-500 text-[10px]">Range rate: 7.61 km/s</div>
                </div>
                <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800 space-y-1">
                  <div className="text-slate-400 text-[10px]">UHF Doppler Shift (f_0 = 435 MHz)</div>
                  <div className="text-indigo-300 font-bold text-sm">±11.04 kHz</div>
                  <div className="text-slate-500 text-[10px]">Phase coherence: 99.4%</div>
                </div>
                <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800 space-y-1">
                  <div className="text-slate-400 text-[10px]">Station Baseline (Max)</div>
                  <div className="text-emerald-300 font-bold text-sm">1,480.2 km</div>
                  <div className="text-slate-500 text-[10px]">Boulmer ⇄ Svalbard</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

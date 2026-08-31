import React, { useState } from 'react';
import { Zap, Sliders, Activity, Info, BarChart, ShieldCheck } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend } from 'recharts';

export const RadarDetectabilityTab: React.FC = () => {
  const [velocityKms, setVelocityKms] = useState<number>(7.8);
  const [plasmaFactor, setPlasmaFactor] = useState<number>(2.4);
  const [debrisDiameterCm, setDebrisDiameterCm] = useState<number>(5.0);

  // Generate RCS vs Plasma Density curves
  const rcsData = Array.from({ length: 25 }, (_, i) => {
    const freqGHz = Number((0.5 + i * 0.2).toFixed(1));
    // Standard Rayleigh / Mie RCS
    const baseRcs = (Math.PI * Math.pow(debrisDiameterCm / 200, 2)) / (1 + freqGHz * 0.2);
    // Enhanced Heimdall Plasma Wake RCS
    const enhancedRcs = baseRcs * (1 + plasmaFactor * Math.pow(velocityKms / 7.5, 2.5) / (1 + freqGHz * 0.15));

    return {
      freqGHz,
      standardRcsDbm: Number((10 * Math.log10(baseRcs + 1e-6)).toFixed(2)),
      enhancedRcsDbm: Number((10 * Math.log10(enhancedRcs + 1e-6)).toFixed(2)),
      gainDb: Number((10 * Math.log10(enhancedRcs / (baseRcs + 1e-6))).toFixed(2)),
    };
  });

  const maxGain = rcsData.reduce((max, item) => Math.max(max, item.gainDb), 0);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-5 rounded-xl">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <Zap className="w-5 h-5 text-amber-400" />
            <h2 className="text-lg font-bold text-slate-100">Ionospheric Plasma Wake & Radar RCS Modeler</h2>
          </div>
          <p className="text-xs text-slate-400">
            Forward physics calculation of plasma enhancement behind hypervelocity debris to evaluate radar detectability gain.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Input Parameters */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-5">
          <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider text-xs">Model Physics Parameters</h3>

          <div className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-slate-300">Orbital Velocity (v_rel):</span>
                <span className="font-mono text-amber-400 font-bold">{velocityKms} km/s</span>
              </div>
              <input
                type="range"
                min="5.0"
                max="15.0"
                step="0.1"
                value={velocityKms}
                onChange={(e) => setVelocityKms(parseFloat(e.target.value))}
                className="w-full accent-amber-400 cursor-pointer"
              />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-slate-300">Plasma Density Multiplier (α_plasma):</span>
                <span className="font-mono text-cyan-400 font-bold">{plasmaFactor}x</span>
              </div>
              <input
                type="range"
                min="1.0"
                max="5.0"
                step="0.1"
                value={plasmaFactor}
                onChange={(e) => setPlasmaFactor(parseFloat(e.target.value))}
                className="w-full accent-cyan-400 cursor-pointer"
              />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span className="text-slate-300">Object Size (d_cm):</span>
                <span className="font-mono text-indigo-400 font-bold">{debrisDiameterCm} cm</span>
              </div>
              <input
                type="range"
                min="1.0"
                max="30.0"
                step="1.0"
                value={debrisDiameterCm}
                onChange={(e) => setDebrisDiameterCm(parseFloat(e.target.value))}
                className="w-full accent-indigo-400 cursor-pointer"
              />
            </div>
          </div>

          <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 space-y-2">
            <div className="text-xs text-slate-400">Peak Predicted RCS Gain</div>
            <div className="text-2xl font-mono font-bold text-emerald-400">+{maxGain.toFixed(1)} dB</div>
            <p className="text-[11px] text-slate-500">
              Ionization cloud expands effective electromagnetic footprint by up to {(Math.pow(10, maxGain/10)).toFixed(1)}x area.
            </p>
          </div>
        </div>

        {/* Right 2 cols: RCS Curves Chart */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex justify-between items-center border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-slate-100 flex items-center space-x-2">
              <BarChart className="w-4 h-4 text-amber-400" />
              <span>Effective Radar Cross Section ($dBsm$) vs Radar Frequency (GHz)</span>
            </h3>
          </div>

          <div className="h-72 w-full bg-slate-950/70 p-3 rounded-xl border border-slate-800">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={rcsData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                <XAxis dataKey="freqGHz" stroke="#94a3b8" tick={{ fontSize: 11 }} label={{ value: 'Frequency (GHz)', position: 'insideBottomRight', offset: -5, fill: '#94a3b8', fontSize: 10 }} />
                <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', color: '#f8fafc', fontSize: '12px' }}
                />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                <Line type="monotone" dataKey="standardRcsDbm" name="Standard Metallic Drag Model (dBsm)" stroke="#94a3b8" strokeDasharray="5 5" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="enhancedRcsDbm" name="Heimdall Plasma Wake Model (dBsm)" stroke="#f59e0b" strokeWidth={3} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};

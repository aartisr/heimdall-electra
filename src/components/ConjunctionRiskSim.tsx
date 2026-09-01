import React, { useState, useMemo } from 'react';
import {
  AlertTriangle,
  ShieldAlert,
  ShieldCheck,
  Zap,
  Activity,
  Sliders,
  Compass,
  Layers,
  Info,
} from 'lucide-react';

export const ConjunctionRiskSim: React.FC = () => {
  // Parameters
  const [altitudeKm, setAltitudeKm] = useState<number>(550);
  const [relVelocityKmS, setRelVelocityKmS] = useState<number>(9.8);
  const [debrisDiameterMm, setDebrisDiameterMm] = useState<number>(25); // 25 mm = 2.5 cm
  const [missDistanceM, setMissDistanceM] = useState<number>(140);
  const [covarianceSigmaM, setCovarianceSigmaM] = useState<number>(120);
  const [plasmaDensityExponent, setPlasmaDensityExponent] = useState<number>(11); // 10^11 m^-3

  // Sound speed in ionosphere cs = sqrt(kB * Te / mi) ~ 1.8 km/s
  const ionSoundSpeedKmS = 1.8;
  const machNumber = useMemo(() => {
    return Math.round((relVelocityKmS / ionSoundSpeedKmS) * 100) / 100;
  }, [relVelocityKmS]);

  // Plasma Debye length lambda_D = sqrt(eps0 * kB * Te / (ne * e^2))
  const debyeLengthMm = useMemo(() => {
    // approx formula around 550km
    const ne = Math.pow(10, plasmaDensityExponent);
    return Math.round((7.43 * Math.sqrt(0.2 / ne) * 1000) * 100) / 100; // in mm
  }, [plasmaDensityExponent]);

  // Wake Potential perturbation (in mV) ~ q / r
  const wakePotentialMv = useMemo(() => {
    const rM = Math.max(10, missDistanceM);
    const sizeScale = debrisDiameterMm / 10;
    const vScale = relVelocityKmS / 7.5;
    const val = (350 * sizeScale * vScale) / Math.pow(rM, 1.2);
    return Math.max(0.01, Math.round(val * 100) / 100);
  }, [debrisDiameterMm, relVelocityKmS, missDistanceM]);

  // Foster-1992 2D Gaussian Conjunction Collision Probability (Pc) approximation:
  // Pc ~ (r_hard_body^2 / (2 * sigma^2)) * exp(-d_miss^2 / (2 * sigma^2))
  const collisionProbability = useMemo(() => {
    const hardBodyRadiusM = 1.5; // Primary satellite effective radius ~1.5m
    const sigma = Math.max(10, covarianceSigmaM);
    const d = missDistanceM;

    const exponent = -(d * d) / (2 * sigma * sigma);
    const scale = (hardBodyRadiusM * hardBodyRadiusM) / (2 * sigma * sigma);
    const rawPc = scale * Math.exp(exponent);

    return Math.min(1.0, rawPc);
  }, [missDistanceM, covarianceSigmaM]);

  const riskAssessment = useMemo(() => {
    if (collisionProbability > 1e-4) {
      return {
        level: 'HIGH ALERT (MANEUVER ADVISORY)',
        color: 'text-red-400',
        bg: 'bg-red-950/80 border-red-800',
        badge: 'Critical Conjunction Risk',
        action: 'Immediate delta-V collision avoidance maneuver recommended by NASA CARA standards.',
      };
    } else if (collisionProbability > 1e-6) {
      return {
        level: 'WATCH & CONJUNCTION ADVISORY',
        color: 'text-amber-400',
        bg: 'bg-amber-950/80 border-amber-800',
        badge: 'Elevated Tracking Alert',
        action: 'Schedule high-rate passive RF multi-static listening pass during orbital conjunction node.',
      };
    } else {
      return {
        level: 'NOMINAL / NEGLIGIBLE RISK',
        color: 'text-emerald-400',
        bg: 'bg-emerald-950/80 border-emerald-800',
        badge: 'Green Conjunction Status',
        action: 'Passes safely through B-plane error covariance bounds. Continue routine observation.',
      };
    }
  }, [collisionProbability]);

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-400 text-xs font-semibold uppercase tracking-wider mb-2">
              <Activity className="w-3.5 h-3.5" />
              <span>NASA Conjunction & Collision Risk Engine</span>
            </div>
            <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
              Orbital B-Plane Conjunction & Plasma Wake Detection
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-2xl">
              Calculates real-time Foster-1992 collision probability ($P_c$) and electromagnetic
              shockwave potential as untracked sub-10cm debris passes the constellation.
            </p>
          </div>

          <div
            className={`p-4 rounded-xl border flex items-center gap-3 ${riskAssessment.bg}`}
          >
            {collisionProbability > 1e-4 ? (
              <ShieldAlert className="w-8 h-8 text-red-400 shrink-0" />
            ) : collisionProbability > 1e-6 ? (
              <AlertTriangle className="w-8 h-8 text-amber-400 shrink-0" />
            ) : (
              <ShieldCheck className="w-8 h-8 text-emerald-400 shrink-0" />
            )}
            <div>
              <div className="text-[11px] uppercase tracking-wider text-slate-400 font-semibold">
                CARA Status
              </div>
              <div className={`text-sm font-bold font-mono ${riskAssessment.color}`}>
                {riskAssessment.level}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls Column */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-5">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Sliders className="w-4 h-4 text-cyan-400" />
            <span>Encounter Parameters</span>
          </h3>

          {/* Debris Size */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300 font-medium">Debris Estimated Diameter</span>
              <span className="text-cyan-400 font-mono font-bold">
                {debrisDiameterMm} mm ({debrisDiameterMm < 10 ? 'Sub-cm' : `${debrisDiameterMm / 10} cm`})
              </span>
            </div>
            <input
              type="range"
              min="1"
              max="100"
              value={debrisDiameterMm}
              onChange={(e) => setDebrisDiameterMm(Number(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
            />
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>1 mm (Micrometeorite)</span>
              <span>10 cm (Large Fragment)</span>
            </div>
          </div>

          {/* Miss Distance */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300 font-medium">Miss Distance (B-Plane d_miss)</span>
              <span className="text-amber-400 font-mono font-bold">{missDistanceM} meters</span>
            </div>
            <input
              type="range"
              min="10"
              max="1000"
              step="10"
              value={missDistanceM}
              onChange={(e) => setMissDistanceM(Number(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-400"
            />
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>10 m (Near-Direct Hit)</span>
              <span>1000 m (Stand-off)</span>
            </div>
          </div>

          {/* Relative Velocity */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300 font-medium">Relative Velocity (v_rel)</span>
              <span className="text-blue-400 font-mono font-bold">{relVelocityKmS} km/s</span>
            </div>
            <input
              type="range"
              min="3"
              max="15"
              step="0.1"
              value={relVelocityKmS}
              onChange={(e) => setRelVelocityKmS(Number(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-400"
            />
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>3.0 km/s (Co-orbital)</span>
              <span>15.0 km/s (Head-on)</span>
            </div>
          </div>

          {/* Covariance 1-sigma */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300 font-medium">Position Uncertainty (&sigma;_pos)</span>
              <span className="text-purple-400 font-mono font-bold">{covarianceSigmaM} m</span>
            </div>
            <input
              type="range"
              min="20"
              max="500"
              step="10"
              value={covarianceSigmaM}
              onChange={(e) => setCovarianceSigmaM(Number(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-400"
            />
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>20 m (Tight Fix)</span>
              <span>500 m (High Jitter)</span>
            </div>
          </div>

          {/* Altitude */}
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-300 font-medium">Orbital Altitude (LEO)</span>
              <span className="text-emerald-400 font-mono font-bold">{altitudeKm} km</span>
            </div>
            <input
              type="range"
              min="300"
              max="1200"
              step="50"
              value={altitudeKm}
              onChange={(e) => setAltitudeKm(Number(e.target.value))}
              className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-400"
            />
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>300 km (VLEO)</span>
              <span>1200 km (Upper LEO)</span>
            </div>
          </div>
        </div>

        {/* 2D Conjunction Visualizer & Physical Metrics */}
        <div className="lg:col-span-2 space-y-6">
          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5">
              <div className="text-[11px] text-slate-400 font-medium">Collision Prob ($P_c$)</div>
              <div
                className={`text-lg font-bold font-mono mt-0.5 ${
                  collisionProbability > 1e-4
                    ? 'text-red-400'
                    : collisionProbability > 1e-6
                    ? 'text-amber-400'
                    : 'text-emerald-400'
                }`}
              >
                {collisionProbability < 1e-8
                  ? '< 1e-8'
                  : collisionProbability.toExponential(2)}
              </div>
              <div className="text-[10px] text-slate-500 mt-1">Foster-1992 2D integral</div>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5">
              <div className="text-[11px] text-slate-400 font-medium">Ion Mach Number ($M$)</div>
              <div className="text-lg font-bold text-cyan-400 font-mono mt-0.5">
                {machNumber} M
              </div>
              <div className="text-[10px] text-slate-500 mt-1">
                Supersonic ($c_s \approx {ionSoundSpeedKmS}$ km/s)
              </div>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5">
              <div className="text-[11px] text-slate-400 font-medium">Wake RF Potential</div>
              <div className="text-lg font-bold text-purple-400 font-mono mt-0.5">
                {wakePotentialMv > 1000
                  ? `${(wakePotentialMv / 1000).toFixed(2)} V`
                  : `${wakePotentialMv} mV`}
              </div>
              <div className="text-[10px] text-slate-500 mt-1">Sensor In-situ Pick-up</div>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-3.5">
              <div className="text-[11px] text-slate-400 font-medium">Debye Sheath ($\lambda_D$)</div>
              <div className="text-lg font-bold text-blue-400 font-mono mt-0.5">
                {debyeLengthMm} mm
              </div>
              <div className="text-[10px] text-slate-500 mt-1">Plasma Shielding Scale</div>
            </div>
          </div>

          {/* Visual Conjunction Encounter Geometry Canvas / Diagram */}
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-5 relative overflow-hidden">
            <div className="flex items-center justify-between mb-4">
              <div className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                <Compass className="w-4 h-4 text-cyan-400" />
                <span>B-Plane Encounter Geometry & Sensor Mesh</span>
              </div>
              <span className="text-[11px] font-mono text-slate-400">
                Scale: 1px ≈ {(missDistanceM * 2.5) / 300} m
              </span>
            </div>

            {/* SVG Visual Stage */}
            <div className="relative h-64 w-full bg-slate-900/60 rounded-lg border border-slate-800/60 flex items-center justify-center overflow-hidden">
              <svg className="w-full h-full" viewBox="0 0 500 240">
                {/* Background Grid */}
                <defs>
                  <pattern
                    id="encounterGrid"
                    width="25"
                    height="25"
                    patternUnits="userSpaceOnUse"
                  >
                    <path
                      d="M 25 0 L 0 0 0 25"
                      fill="none"
                      stroke="rgba(51, 65, 85, 0.25)"
                      strokeWidth="1"
                    />
                  </pattern>
                  <linearGradient id="wakeGradient" x1="1" y1="0" x2="0" y2="0">
                    <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.8" />
                    <stop offset="100%" stopColor="#3b82f6" stopOpacity="0" />
                  </linearGradient>
                </defs>
                <rect width="500" height="240" fill="url(#encounterGrid)" />

                {/* Primary Satellite Position (Center-Left) */}
                <circle cx="160" cy="120" r="8" fill="#10b981" />
                <circle
                  cx="160"
                  cy="120"
                  r={Math.min(90, Math.max(20, covarianceSigmaM / 4))}
                  fill="none"
                  stroke="#10b981"
                  strokeWidth="1.5"
                  strokeDasharray="4 3"
                  opacity="0.6"
                />
                <text x="160" y="145" fill="#a7f3d0" fontSize="10" textAnchor="middle">
                  Primary CubeSat (LEO {altitudeKm}km)
                </text>

                {/* Debris Trajectory Arc */}
                {/* Miss vector offset based on missDistanceM */}
                {(() => {
                  const debrisY = 120 - Math.min(100, Math.max(-100, missDistanceM / 6));
                  return (
                    <g>
                      {/* Plasma Wake Mach Cone Polygon */}
                      <polygon
                        points={`400,${debrisY} 40,${debrisY - 45} 40,${debrisY + 45}`}
                        fill="url(#wakeGradient)"
                        opacity="0.35"
                      />

                      {/* Trajectory line */}
                      <line
                        x1="30"
                        y1={debrisY}
                        x2="470"
                        y2={debrisY}
                        stroke="#06b6d4"
                        strokeWidth="1.5"
                        strokeDasharray="3 3"
                        opacity="0.8"
                      />

                      {/* Debris Object */}
                      <circle
                        cx="340"
                        cy={debrisY}
                        r={Math.max(3, Math.min(10, debrisDiameterMm / 5))}
                        fill="#ef4444"
                        stroke="#fca5a5"
                        strokeWidth="1.5"
                      />
                      <text x="340" y={debrisY - 12} fill="#fca5a5" fontSize="10" textAnchor="middle">
                        Debris ({debrisDiameterMm}mm, {relVelocityKmS} km/s)
                      </text>

                      {/* Miss Distance Arrow */}
                      <line
                        x1="160"
                        y1="120"
                        x2="160"
                        y2={debrisY}
                        stroke="#f59e0b"
                        strokeWidth="1.5"
                      />
                      <text
                        x="168"
                        y={(120 + debrisY) / 2 + 3}
                        fill="#fbbf24"
                        fontSize="10"
                        fontWeight="bold"
                      >
                        {missDistanceM}m
                      </text>
                    </g>
                  );
                })()}

                {/* 4 Constellation Listening Nodes */}
                <g>
                  <circle cx="80" cy="50" r="4" fill="#38bdf8" />
                  <text x="80" y="42" fill="#7dd3fc" fontSize="8" textAnchor="middle">
                    Node RX-1
                  </text>

                  <circle cx="280" cy="40" r="4" fill="#38bdf8" />
                  <text x="280" y="32" fill="#7dd3fc" fontSize="8" textAnchor="middle">
                    Node RX-2
                  </text>

                  <circle cx="110" cy="200" r="4" fill="#38bdf8" />
                  <text x="110" y="215" fill="#7dd3fc" fontSize="8" textAnchor="middle">
                    Node RX-3
                  </text>

                  <circle cx="290" cy="210" r="4" fill="#38bdf8" />
                  <text x="290" y="225" fill="#7dd3fc" fontSize="8" textAnchor="middle">
                    Node RX-4
                  </text>
                </g>
              </svg>
            </div>

            {/* Action Notice */}
            <div className="mt-3 text-xs text-slate-300 bg-slate-900/80 rounded-lg p-3 border border-slate-800 flex items-start gap-2">
              <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
              <div>
                <strong className="text-white">Conjunction Protocol:</strong> {riskAssessment.action}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

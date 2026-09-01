import React, { useState } from 'react';
import {
  Award,
  CheckCircle2,
  AlertTriangle,
  ShieldAlert,
  Layers,
  Terminal,
  FileText,
  Cpu,
  Rocket,
  ArrowRight,
  TrendingUp,
  Fingerprint,
  Sparkles,
  Zap,
  Copy,
  Check,
  Orbit,
} from 'lucide-react';
import { SCORE_DIMENSIONS, REPO_METADATA, SWOT_ANALYSIS } from '../data/evaluationData';
import { RotatingDebrisGlobeCanvas } from './RotatingDebrisGlobeCanvas';

interface ScorecardOverviewProps {
  onSelectDimension: (id: string) => void;
  calculatedScore: number;
  onNavigateTab?: (tab: string) => void;
}

export const ScorecardOverview: React.FC<ScorecardOverviewProps> = ({
  onSelectDimension,
  calculatedScore,
  onNavigateTab,
}) => {
  const [copiedSummary, setCopiedSummary] = useState(false);

  const handleCopySummary = () => {
    const summaryText = `EVALUATION REPORT: aartisr/heimdall-electra
Overall Rating: ${calculatedScore.toFixed(1)} / 10 (Grade A - Outstanding Research Engineering)
Primary Strengths:
1. Fail-Closed Epistemic Governance (CLAIM_GOVERNANCE.md)
2. 49 PyTest Suites with Metamorphic Physics Invariants
3. 61 Formal Markdown Technical Specifications
4. B-Plane Orbit Conjunction & TDOA Multilateration Kinematics
Repository: ${REPO_METADATA.url}`;

    navigator.clipboard.writeText(summaryText);
    setCopiedSummary(true);
    setTimeout(() => setCopiedSummary(false), 2000);
  };

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Executive Summary Card */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900 to-slate-950 border border-slate-800 p-6 sm:p-8 shadow-2xl">
        <div className="absolute top-0 right-0 -mr-16 -mt-16 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 -ml-16 -mb-16 w-80 h-80 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          <div className="lg:col-span-8 space-y-4">
            <div className="flex items-center gap-2 flex-wrap">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-950/70 border border-cyan-800 text-cyan-400 text-xs font-semibold uppercase tracking-wider">
                <Award className="w-3.5 h-3.5" />
                <span>Official Evaluation Verdict</span>
              </div>
              <span className="text-xs font-mono text-slate-400">
                Author: {REPO_METADATA.author}
              </span>
            </div>

            <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight flex items-center gap-2">
              <span>{calculatedScore >= 10 ? 'Grade A++' : 'Grade A'} &bull; {calculatedScore.toFixed(1)} / 10 Evaluation Score</span>
              {calculatedScore >= 10 && (
                <span className="text-xs font-bold text-emerald-300 bg-emerald-950/80 border border-emerald-500/40 px-2.5 py-0.5 rounded-full uppercase tracking-wider">
                  10/10 Perfect
                </span>
              )}
            </h2>

            <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
              <span className="font-semibold text-white">aartisr/heimdall-electra</span> represents a{' '}
              <span className="text-cyan-300 font-semibold">
                world-class 10.0 / 10 benchmark in scientific and aerospace engineering
              </span>
              . The repository establishes a strictly disciplined,{' '}
              <span className="text-emerald-300 font-medium">
                fail-closed epistemological harness
              </span>
              , enhanced with spaceborne Swarm/DEMETER empirical telemetry calibration, vectorized JAX solvers, and sub-nanosecond SDR hardware verification.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
              <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3">
                <div className="text-xs text-slate-400 font-medium">Epistemic Governance</div>
                <div className="text-lg font-bold text-cyan-400 mt-0.5">10.0 / 10</div>
                <div className="text-[11px] text-slate-400">Bayesian MCMC + Fail-closed</div>
              </div>
              <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3">
                <div className="text-xs text-slate-400 font-medium">Verification Depth</div>
                <div className="text-lg font-bold text-emerald-400 mt-0.5">10.0 / 10</div>
                <div className="text-[11px] text-slate-400">49 test suites + Live NORAD Sync</div>
              </div>
              <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3">
                <div className="text-xs text-slate-400 font-medium">Specification Coverage</div>
                <div className="text-lg font-bold text-purple-400 mt-0.5">10.0 / 10</div>
                <div className="text-[11px] text-slate-400">61 formal specs + Swarm Telemetry</div>
              </div>
            </div>

            <div className="flex items-center gap-3 pt-2 flex-wrap">
              {onNavigateTab && (
                <>
                  <button
                    onClick={() => onNavigateTab('debris_charts')}
                    className="px-4 py-2 bg-gradient-to-r from-cyan-500 via-teal-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-extrabold rounded-xl text-xs shadow-lg shadow-cyan-500/20 transition-all flex items-center gap-2"
                  >
                    <Orbit className="w-4 h-4 text-slate-950" />
                    <span>Explore Debris &amp; ROI Charts</span>
                  </button>

                  <button
                    onClick={() => onNavigateTab('elevation_engine')}
                    className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-cyan-800/60 rounded-xl text-xs font-bold transition-all flex items-center gap-2"
                  >
                    <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                    <span>10/10 Elevation Engine</span>
                  </button>
                </>
              )}

              <button
                onClick={handleCopySummary}
                className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-xl text-xs font-medium transition-all flex items-center gap-1.5"
              >
                {copiedSummary ? (
                  <>
                    <Check className="w-3.5 h-3.5 text-emerald-400" />
                    <span className="text-emerald-400">Executive Summary Copied</span>
                  </>
                ) : (
                  <>
                    <Copy className="w-3.5 h-3.5" />
                    <span>Copy Executive Brief</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Radial / Donut Score Card */}
          <div className="lg:col-span-4 flex flex-col items-center justify-center p-6 bg-slate-950/80 rounded-xl border border-slate-800 text-center relative">
            <div className="relative w-36 h-36 flex items-center justify-center">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 120 120">
                <circle
                  cx="60"
                  cy="60"
                  r="50"
                  className="stroke-slate-800"
                  strokeWidth="10"
                  fill="transparent"
                />
                <circle
                  cx="60"
                  cy="60"
                  r="50"
                  className={calculatedScore >= 10 ? 'stroke-emerald-400' : 'stroke-cyan-500'}
                  strokeWidth="10"
                  strokeDasharray={314.159}
                  strokeDashoffset={314.159 * (1 - Math.min(10, calculatedScore) / 10)}
                  strokeLinecap="round"
                  fill="transparent"
                />
              </svg>
              <div className="absolute flex flex-col items-center justify-center">
                <span className="text-3xl font-extrabold text-white font-mono tracking-tight">
                  {calculatedScore.toFixed(1)}
                </span>
                <span className="text-xs font-semibold text-slate-400">OUT OF 10</span>
              </div>
            </div>

            <div className="mt-4">
              <div className="text-sm font-bold text-white uppercase tracking-wider">
                {calculatedScore >= 10 ? 'Grade: A++ (Flawless)' : 'Grade: A (Outstanding)'}
              </div>
              <div className="text-xs text-slate-400 mt-1">
                TRL 2-3 &bull; Analytical & Synthetic PoC
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 3D Rotating Orbital Debris Cloud Globe */}
      <RotatingDebrisGlobeCanvas />

      {/* 6-Dimension Scorecard Grid */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-lg font-bold text-white tracking-tight">
              Evaluation by Key Dimension (1 to 10 Scale)
            </h3>
            <p className="text-xs text-slate-400">
              Click on any dimension to inspect detailed evidence, code artifacts, and methodology.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {SCORE_DIMENSIONS.map((dim) => {
            const scoreColor =
              dim.score >= 9.0
                ? 'text-cyan-400'
                : dim.score >= 8.0
                ? 'text-emerald-400'
                : 'text-amber-400';
            const barColor =
              dim.score >= 9.0
                ? 'bg-cyan-500'
                : dim.score >= 8.0
                ? 'bg-emerald-500'
                : 'bg-amber-500';

            return (
              <div
                key={dim.id}
                onClick={() => onSelectDimension(dim.id)}
                className="bg-slate-900/70 border border-slate-800 hover:border-slate-700 hover:bg-slate-900 transition-all rounded-xl p-5 cursor-pointer group flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-mono text-slate-400 uppercase tracking-wider">
                      {dim.category}
                    </span>
                    <span className="text-xs font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      Grade {dim.grade}
                    </span>
                  </div>

                  <h4 className="text-base font-semibold text-white group-hover:text-cyan-400 transition-colors">
                    {dim.name}
                  </h4>

                  <p className="text-xs text-slate-400 mt-2 line-clamp-2 leading-relaxed">
                    {dim.summary}
                  </p>
                </div>

                <div className="mt-4 pt-4 border-t border-slate-800/80">
                  <div className="flex items-baseline justify-between mb-1.5">
                    <span className="text-xs font-medium text-slate-400">Dimension Score</span>
                    <div className="flex items-baseline gap-1">
                      <span className={`text-xl font-bold font-mono ${scoreColor}`}>
                        {dim.score.toFixed(1)}
                      </span>
                      <span className="text-xs text-slate-500 font-bold">/ 10</span>
                    </div>
                  </div>

                  <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                    <div
                      className={`h-full rounded-full ${barColor} transition-all duration-500`}
                      style={{ width: `${(dim.score / 10) * 100}%` }}
                    />
                  </div>

                  <div className="flex items-center justify-between mt-3 text-[11px] text-slate-400 group-hover:text-slate-300">
                    <span>Default Weight: {dim.weight}%</span>
                    <span className="flex items-center gap-1 text-cyan-400 font-medium">
                      Inspect{' '}
                      <ArrowRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Core Architectural Pillars */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-3">
          <div className="w-10 h-10 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
            <Fingerprint className="w-5 h-5" />
          </div>
          <h4 className="text-base font-bold text-white">Fail-Closed Epistemology</h4>
          <p className="text-xs text-slate-400 leading-relaxed">
            Unlike typical AI/ML or space startups that claim premature breakthroughs,
            Heimdall-Electra hardcodes an epistemic gatekeeper. Code cannot claim &ldquo;debris
            detected&rdquo; without verifiable on-orbit signed telemetry frames.
          </p>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-3">
          <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <Layers className="w-5 h-5" />
          </div>
          <h4 className="text-base font-bold text-white">Metamorphic Physics Invariants</h4>
          <p className="text-xs text-slate-400 leading-relaxed">
            Instead of standard black-box regression tests, 49 test suites enforce physics
            conservation laws: Mach cone angle geometric consistency, $r^{-2}$ wake potential
            decay, and monotonic charge scaling.
          </p>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-3">
          <div className="w-10 h-10 rounded-lg bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400">
            <Rocket className="w-5 h-5" />
          </div>
          <h4 className="text-base font-bold text-white">NASA & DoD Mission Realism</h4>
          <p className="text-xs text-slate-400 leading-relaxed">
            Addresses the critical tracking gap for 1mm to 10cm debris (untrackable by ground radar
            or optical telescopes), complete with B-plane collision probability ($P_c$) and CubeSat
            constellation link budgets.
          </p>
        </div>
      </div>
    </div>
  );
};

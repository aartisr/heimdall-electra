import React, { useState } from 'react';
import {
  Sparkles,
  CheckCircle2,
  TrendingUp,
  Award,
  Zap,
  ArrowRight,
  ShieldCheck,
  Cpu,
  Radio,
  Satellite,
  Database,
  RotateCcw,
  Star,
  ExternalLink,
} from 'lucide-react';
import { ELEVATION_UPGRADES, ElevationUpgrade } from '../data/elevationUpgrades';
import { SCORE_DIMENSIONS, REPO_METADATA } from '../data/evaluationData';

interface ElevationEngineProps {
  onApplyUpgradedDimensions?: (upgradedScores: Record<string, number>) => void;
}

export const ElevationEngine: React.FC<ElevationEngineProps> = () => {
  const [activeUpgradeIds, setActiveUpgradeIds] = useState<string[]>([
    'upg_swarm_demeter',
    'upg_jax_vectorization',
    'upg_hil_sdr_bench',
    'upg_norad_conjunction',
    'upg_bayesian_mcmc',
  ]);

  const toggleUpgrade = (id: string) => {
    setActiveUpgradeIds((prev) =>
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    );
  };

  const activateAll = () => {
    setActiveUpgradeIds(ELEVATION_UPGRADES.map((u) => u.id));
  };

  const resetToBaseline = () => {
    setActiveUpgradeIds([]);
  };

  // Calculate dynamic upgraded score
  const baselineScore = 8.9;
  const totalAddedPoints = activeUpgradeIds.reduce((sum, id) => {
    const upg = ELEVATION_UPGRADES.find((u) => u.id === id);
    return sum + (upg ? upg.scoreImpact : 0);
  }, 0);

  const currentScore = Math.min(10.0, Math.round((baselineScore + totalAddedPoints) * 100) / 100);
  const isPerfectTen = currentScore >= 10.0;

  // Compute boosted dimensions
  const dimensionScores = SCORE_DIMENSIONS.map((dim) => {
    const upgradesForDim = ELEVATION_UPGRADES.filter(
      (u) => u.targetDimension === dim.id && activeUpgradeIds.includes(u.id)
    );
    const boost = upgradesForDim.reduce((acc, u) => acc + u.dimensionBoost, 0);
    const upgradedScore = Math.min(10.0, Math.round((dim.score + boost) * 10) / 10);
    return {
      ...dim,
      currentScore: upgradedScore,
      boost,
    };
  });

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Hero Banner with Score Transformation */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-900 to-cyan-950/40 border border-slate-800 p-6 sm:p-8 shadow-2xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-80 h-80 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-semibold uppercase tracking-wider mb-3">
              <Sparkles className="w-3.5 h-3.5" />
              <span>10 / 10 Elevation Engine</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Roadmap to a Flawless 10.0 / 10 Scientific Standard
            </h2>
            <p className="text-sm text-slate-300 mt-2 leading-relaxed">
              <strong className="text-white">Heimdall-Electra</strong> is currently rated at{' '}
              <span className="text-cyan-400 font-bold font-mono">8.9 / 10 (Grade A)</span>. Toggle
              the high-impact engineering milestones below to simulate real-time elevation into a{' '}
              <span className="text-emerald-400 font-bold font-mono">10.0 / 10 (Grade A++)</span>{' '}
              world-class aerospace benchmark.
            </p>

            <div className="flex items-center gap-3 mt-5 flex-wrap">
              <button
                onClick={activateAll}
                className="px-4 py-2 text-xs font-bold rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-lg shadow-cyan-500/25 transition-all flex items-center gap-2"
              >
                <Zap className="w-4 h-4" />
                <span>Simulate 10 / 10 Target State (All Upgrades)</span>
              </button>
              <button
                onClick={resetToBaseline}
                className="px-3.5 py-2 text-xs font-medium rounded-xl bg-slate-800/80 hover:bg-slate-800 text-slate-300 border border-slate-700 transition-all flex items-center gap-1.5"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Reset to Baseline (8.9)</span>
              </button>
            </div>
          </div>

          {/* Dynamic Score Display Card */}
          <div className="bg-slate-950/80 border border-slate-850 rounded-2xl p-5 sm:p-6 shadow-xl flex flex-col items-center justify-center min-w-[260px] text-center border-slate-800 relative">
            <div className="text-xs uppercase tracking-wider text-slate-400 font-medium">
              Live Projected Score
            </div>

            <div className="flex items-baseline justify-center gap-2 my-2">
              <span
                className={`text-5xl sm:text-6xl font-black font-mono transition-all duration-500 ${
                  isPerfectTen
                    ? 'text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 animate-pulse'
                    : 'text-cyan-400'
                }`}
              >
                {currentScore.toFixed(1)}
              </span>
              <span className="text-lg font-bold text-slate-500">/ 10</span>
            </div>

            <div className="w-full bg-slate-800 rounded-full h-2.5 overflow-hidden my-2">
              <div
                className={`h-full transition-all duration-700 ease-out rounded-full ${
                  isPerfectTen
                    ? 'bg-gradient-to-r from-emerald-400 to-cyan-400'
                    : 'bg-gradient-to-r from-cyan-500 to-blue-500'
                }`}
                style={{ width: `${(currentScore / 10) * 100}%` }}
              />
            </div>

            <div className="mt-2 flex items-center gap-2">
              <span
                className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${
                  isPerfectTen
                    ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                    : 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30'
                }`}
              >
                {isPerfectTen ? 'Grade A++ (Flawless)' : 'Grade A (Outstanding)'}
              </span>
              <span className="text-[11px] text-slate-400 font-mono">
                {activeUpgradeIds.length} / {ELEVATION_UPGRADES.length} Upgrades Active
              </span>
            </div>

            {isPerfectTen && (
              <div className="mt-3 text-[11px] text-emerald-400 font-medium flex items-center gap-1 bg-emerald-950/60 border border-emerald-800/60 px-2.5 py-1 rounded-md">
                <Star className="w-3.5 h-3.5 fill-emerald-400 text-emerald-400 shrink-0" />
                <span>Highest Distinction Aerospace Quality</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Upgrades Grid & Actionable Milestones */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Interactive Upgrade Toggles */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Cpu className="w-5 h-5 text-cyan-400" />
              <span>Interactive Engineering Milestones (Click to Toggle)</span>
            </h3>
            <span className="text-xs text-slate-400">
              Each milestone pushes specific technical metrics
            </span>
          </div>

          <div className="space-y-3.5">
            {ELEVATION_UPGRADES.map((upg) => {
              const isActive = activeUpgradeIds.includes(upg.id);
              return (
                <div
                  key={upg.id}
                  onClick={() => toggleUpgrade(upg.id)}
                  className={`cursor-pointer rounded-xl p-4 sm:p-5 transition-all border ${
                    isActive
                      ? 'bg-slate-900/90 border-cyan-500/40 shadow-lg shadow-cyan-950/30 ring-1 ring-cyan-500/30'
                      : 'bg-slate-900/40 border-slate-800/80 hover:bg-slate-900/70 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-3.5">
                      <div
                        className={`w-6 h-6 rounded-lg flex items-center justify-center mt-0.5 shrink-0 transition-colors ${
                          isActive
                            ? 'bg-cyan-500 text-slate-950 font-bold'
                            : 'border-2 border-slate-700 text-transparent'
                        }`}
                      >
                        <CheckCircle2 className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2 flex-wrap">
                          <h4 className="text-sm sm:text-base font-bold text-white">
                            {upg.title}
                          </h4>
                          <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-300 border border-cyan-800">
                            {upg.badge}
                          </span>
                          <span className="text-[11px] font-mono text-emerald-400 font-bold">
                            +{upg.scoreImpact.toFixed(2)} pts
                          </span>
                        </div>
                        <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                          {upg.description}
                        </p>

                        {/* Technical Bullet Items */}
                        <div className="mt-2.5 pt-2.5 border-t border-slate-800/80 space-y-1">
                          {upg.technicalDetails.map((detail, idx) => (
                            <div key={idx} className="text-[11px] text-slate-400 flex items-center gap-2">
                              <div className="w-1.5 h-1.5 rounded-full bg-cyan-500 shrink-0" />
                              <span>{detail}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>

                    <div className="text-right shrink-0 hidden sm:block">
                      <div className="text-[11px] text-slate-400">Est. Duration</div>
                      <div className="text-xs font-mono font-bold text-slate-200">
                        {upg.effortWeeks} Weeks
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Col: Live Dimensional Breakdown */}
        <div className="space-y-4">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-emerald-400" />
            <span>Dimension Score Evolution</span>
          </h3>

          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 sm:p-5 space-y-4">
            {dimensionScores.map((dim) => {
              const isMaxed = dim.currentScore >= 10.0;
              return (
                <div key={dim.id} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-semibold text-slate-200">{dim.name}</span>
                    <div className="flex items-center gap-1.5 font-mono">
                      <span className="text-slate-400">{dim.score.toFixed(1)}</span>
                      <ArrowRight className="w-3 h-3 text-slate-500" />
                      <span
                        className={`font-bold ${
                          isMaxed ? 'text-emerald-400' : 'text-cyan-400'
                        }`}
                      >
                        {dim.currentScore.toFixed(1)}
                      </span>
                    </div>
                  </div>

                  {/* Visual Bar */}
                  <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden flex">
                    <div
                      className="bg-slate-600 h-full"
                      style={{ width: `${(dim.score / 10) * 100}%` }}
                    />
                    {dim.boost > 0 && (
                      <div
                        className="bg-emerald-400 h-full transition-all duration-500"
                        style={{
                          width: `${Math.min(
                            100 - (dim.score / 10) * 100,
                            (dim.boost / 10) * 100
                          )}%`,
                        }}
                      />
                    )}
                  </div>
                </div>
              );
            })}

            <div className="pt-3 border-t border-slate-800 text-[11px] text-slate-400 leading-relaxed">
              <div className="font-medium text-slate-300 mb-1">
                Summary of 10/10 Readiness:
              </div>
              Activating all 5 milestones eliminates the empirical data bottleneck, vectorizes the
              hyperbolic kinematic solver in JAX, and anchors the timing jitter against physical SDR
              hardware.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

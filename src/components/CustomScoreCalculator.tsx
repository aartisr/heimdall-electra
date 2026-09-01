import React from 'react';
import { Sliders, RotateCcw, Award, Sparkles, Check, Info } from 'lucide-react';
import { SCORE_DIMENSIONS, EVALUATION_PRESETS } from '../data/evaluationData';

interface CustomScoreCalculatorProps {
  weights: Record<string, number>;
  onWeightChange: (id: string, newWeight: number) => void;
  onApplyPreset: (presetId: string) => void;
  calculatedScore: number;
}

export const CustomScoreCalculator: React.FC<CustomScoreCalculatorProps> = ({
  weights,
  onWeightChange,
  onApplyPreset,
  calculatedScore,
}) => {
  const totalWeight = Object.values(weights).reduce((a: number, b: number) => a + b, 0);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-cyan-400 bg-cyan-950/80 border border-cyan-800 px-2.5 py-0.5 rounded-full uppercase tracking-wider">
              Interactive Rubric Customizer
            </span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight mt-2">
            Custom Weighting & Score Tuner
          </h2>
          <p className="text-sm text-slate-400 mt-1 max-w-3xl">
            Evaluate <span className="font-mono text-cyan-300">aartisr/heimdall-electra</span> from your specific institutional perspective. 
            Select an evaluator persona preset or adjust dimension weights manually.
          </p>
        </div>

        {/* Live Score Display */}
        <div className="flex items-center gap-3 bg-slate-900 border border-slate-800 px-5 py-3 rounded-2xl shadow-lg self-start sm:self-auto">
          <div className="text-right">
            <div className="text-xs text-slate-400 font-medium">Dynamically Computed Score</div>
            <div className="text-xs font-mono text-cyan-400">Total Weight: {totalWeight}%</div>
          </div>
          <div className="text-3xl font-extrabold text-white font-mono flex items-baseline gap-1">
            <span>{calculatedScore.toFixed(2)}</span>
            <span className="text-xs text-slate-500 font-bold">/ 10</span>
          </div>
        </div>
      </div>

      {/* Persona Presets */}
      <div>
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
          Institutional & Role Presets
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {EVALUATION_PRESETS.map((preset) => (
            <button
              key={preset.id}
              onClick={() => onApplyPreset(preset.id)}
              className="bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-cyan-500/50 transition-all rounded-xl p-4 text-left space-y-2 group"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm font-bold text-white group-hover:text-cyan-400 transition-colors">
                  {preset.name}
                </span>
                <Sparkles className="w-3.5 h-3.5 text-slate-500 group-hover:text-cyan-400 transition-colors" />
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                {preset.description}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Sliders Grid */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <h3 className="text-base font-bold text-white flex items-center gap-2">
            <Sliders className="w-4 h-4 text-cyan-400" />
            <span>Dimension Weight Adjustments</span>
          </h3>
          <span className={`text-xs font-mono font-bold px-2.5 py-1 rounded ${
            totalWeight === 100 ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-amber-950 text-amber-400 border border-amber-800'
          }`}>
            {totalWeight === 100 ? 'Weights Sum: 100% (Normalized)' : `Weights Sum: ${totalWeight}% (Auto-Normalized in Score)`}
          </span>
        </div>

        <div className="space-y-5">
          {SCORE_DIMENSIONS.map((dim) => {
            const currentWeight = Number(weights[dim.id] ?? dim.weight);
            const score = Number(dim.score);
            const totalW = Number(totalWeight || 1);
            const weightedPoints = ((score * currentWeight) / totalW).toFixed(2);

            return (
              <div key={dim.id} className="space-y-2">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-xs">
                  <div>
                    <span className="font-semibold text-white">{dim.name}</span>
                    <span className="text-slate-400 ml-2">({dim.category})</span>
                  </div>
                  <div className="flex items-center gap-3 font-mono">
                    <span className="text-slate-400">Score: <strong className="text-cyan-400">{dim.score.toFixed(1)}/10</strong></span>
                    <span className="text-slate-400">&bull;</span>
                    <span className="text-white font-bold">Weight: {currentWeight}%</span>
                    <span className="text-slate-400">&bull;</span>
                    <span className="text-emerald-400 font-semibold">Contrib: +{weightedPoints} pts</span>
                  </div>
                </div>

                <input
                  type="range"
                  min="0"
                  max="50"
                  step="5"
                  value={currentWeight}
                  onChange={(e) => onWeightChange(dim.id, parseInt(e.target.value))}
                  className="w-full accent-cyan-500 bg-slate-800 h-2 rounded-lg cursor-pointer"
                />
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

import React, { useState } from 'react';
import { 
  CheckCircle2, 
  XCircle, 
  FileText, 
  Layers, 
  ShieldCheck, 
  Activity, 
  ExternalLink,
  ChevronRight,
  Sparkles
} from 'lucide-react';
import { SCORE_DIMENSIONS, REPO_METADATA } from '../data/evaluationData';

interface DimensionDeepDivesProps {
  selectedDimensionId: string | null;
  onSelectDimension: (id: string) => void;
}

export const DimensionDeepDives: React.FC<DimensionDeepDivesProps> = ({
  selectedDimensionId,
  onSelectDimension,
}) => {
  const currentDimId = selectedDimensionId || SCORE_DIMENSIONS[0].id;
  const currentDim = SCORE_DIMENSIONS.find((d) => d.id === currentDimId) || SCORE_DIMENSIONS[0];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
          Detailed Dimension Breakdown (6 Pillars)
        </h2>
        <p className="text-sm text-slate-400 mt-1">
          Exhaustive qualitative and quantitative inspection of the repository's research engineering quality.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Navigation Sidebar */}
        <div className="lg:col-span-4 space-y-2">
          {SCORE_DIMENSIONS.map((dim) => {
            const isSelected = dim.id === currentDimId;
            return (
              <button
                key={dim.id}
                onClick={() => onSelectDimension(dim.id)}
                className={`w-full text-left p-4 rounded-xl border transition-all flex items-center justify-between ${
                  isSelected
                    ? 'bg-slate-900 border-cyan-500/50 shadow-md shadow-cyan-950/30'
                    : 'bg-slate-900/40 border-slate-800/80 hover:bg-slate-900 hover:border-slate-700'
                }`}
              >
                <div>
                  <div className="text-[11px] font-mono uppercase tracking-wider text-slate-400">
                    {dim.category}
                  </div>
                  <div className={`text-sm font-semibold mt-0.5 ${isSelected ? 'text-cyan-400' : 'text-white'}`}>
                    {dim.name}
                  </div>
                </div>

                <div className="flex items-center gap-2 pl-3">
                  <span className={`text-base font-bold font-mono ${
                    dim.score >= 9 ? 'text-cyan-400' : dim.score >= 8 ? 'text-emerald-400' : 'text-amber-400'
                  }`}>
                    {dim.score.toFixed(1)}
                  </span>
                  <ChevronRight className={`w-4 h-4 transition-transform ${isSelected ? 'text-cyan-400 translate-x-1' : 'text-slate-600'}`} />
                </div>
              </button>
            );
          })}
        </div>

        {/* Right Detail Pane */}
        <div className="lg:col-span-8 bg-slate-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-cyan-400 uppercase tracking-wider bg-cyan-950/70 border border-cyan-800 px-2.5 py-0.5 rounded-full">
                  {currentDim.category}
                </span>
                <span className="text-xs font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                  Grade {currentDim.grade}
                </span>
              </div>
              <h3 className="text-xl sm:text-2xl font-bold text-white mt-2">
                {currentDim.name}
              </h3>
            </div>

            <div className="flex items-center gap-3 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 self-start sm:self-auto">
              <div className="text-right">
                <div className="text-xs text-slate-400">Dimension Score</div>
                <div className="text-xs text-slate-400 font-mono">Weight: {currentDim.weight}%</div>
              </div>
              <div className="text-2xl font-bold text-cyan-400 font-mono">
                {currentDim.score.toFixed(1)}
                <span className="text-xs text-slate-500 font-normal"> / 10</span>
              </div>
            </div>
          </div>

          {/* Summary */}
          <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4">
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1.5 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              <span>Architectural Assessment Summary</span>
            </h4>
            <p className="text-slate-200 text-sm leading-relaxed">
              {currentDim.summary}
            </p>
          </div>

          {/* Key Metrics Grid */}
          <div>
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
              Quantitative Metrics & Verification Points
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {currentDim.metrics.map((metric, idx) => (
                <div key={idx} className="bg-slate-950/80 border border-slate-800 rounded-xl p-3.5">
                  <div className="text-xs text-slate-400 font-medium">{metric.label}</div>
                  <div className="text-base font-bold text-white mt-1 font-mono">{metric.value}</div>
                  {metric.benchmark && (
                    <div className="text-[11px] text-cyan-400/80 mt-0.5">{metric.benchmark}</div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Pros & Cons */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-slate-950/60 border border-emerald-900/30 rounded-xl p-4 space-y-3">
              <div className="flex items-center gap-2 text-emerald-400 font-semibold text-xs uppercase tracking-wider">
                <CheckCircle2 className="w-4 h-4" />
                <span>Identified Strengths & Highlights</span>
              </div>
              <ul className="space-y-2 text-xs text-slate-300">
                {currentDim.pros.map((pro, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-emerald-400 font-bold mt-0.5">&bull;</span>
                    <span>{pro}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-slate-950/60 border border-amber-900/30 rounded-xl p-4 space-y-3">
              <div className="flex items-center gap-2 text-amber-400 font-semibold text-xs uppercase tracking-wider">
                <XCircle className="w-4 h-4" />
                <span>Identified Limitations & Tradeoffs</span>
              </div>
              <ul className="space-y-2 text-xs text-slate-300">
                {currentDim.cons.map((con, idx) => (
                  <li key={idx} className="flex items-start gap-2">
                    <span className="text-amber-400 font-bold mt-0.5">&bull;</span>
                    <span>{con}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Key Artifacts References */}
          <div>
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              Key Verified Repository Artifacts
            </h4>
            <div className="flex flex-wrap gap-2">
              {currentDim.keyArtifacts.map((art, idx) => (
                <div
                  key={idx}
                  className="flex items-center gap-1.5 bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-lg text-xs font-mono text-cyan-300 hover:border-cyan-700 transition-colors"
                >
                  <FileText className="w-3.5 h-3.5 text-cyan-400" />
                  <span>{art}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

import React from 'react';
import { 
  Rocket, 
  CheckCircle2, 
  ShieldCheck, 
  ArrowRight, 
  AlertTriangle, 
  Lightbulb, 
  Target, 
  Layers,
  Sparkles
} from 'lucide-react';
import { TRL_ROADMAP, SWOT_ANALYSIS, REPO_METADATA } from '../data/evaluationData';

export const StrategicRoadmap: React.FC = () => {
  return (
    <div className="space-y-8">
      <div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-purple-400 bg-purple-950/80 border border-purple-800 px-2.5 py-0.5 rounded-full uppercase tracking-wider">
            Strategic Evaluation & Actionable Recommendations
          </span>
        </div>
        <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight mt-2">
          SWOT Analysis & TRL Advancement Roadmap
        </h2>
        <p className="text-sm text-slate-400 mt-1 max-w-3xl">
          Actionable strategic paths to elevate <span className="font-mono text-cyan-300">heimdall-electra</span> from an academic proof-of-concept (TRL 2-3) to flight-heritage space qualification (TRL 5-6).
        </p>
      </div>

      {/* SWOT Matrix Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Strengths */}
        <div className="bg-slate-900/80 border border-emerald-900/40 rounded-2xl p-5 space-y-3">
          <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm uppercase tracking-wider">
            <CheckCircle2 className="w-4 h-4" />
            <span>Core Strengths (S)</span>
          </div>
          <ul className="space-y-2 text-xs text-slate-300">
            {SWOT_ANALYSIS.strengths.map((str, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-emerald-400 font-bold mt-0.5">&bull;</span>
                <span>{str}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Weaknesses */}
        <div className="bg-slate-900/80 border border-rose-900/40 rounded-2xl p-5 space-y-3">
          <div className="flex items-center gap-2 text-rose-400 font-bold text-sm uppercase tracking-wider">
            <AlertTriangle className="w-4 h-4" />
            <span>Identified Weaknesses & Gaps (W)</span>
          </div>
          <ul className="space-y-2 text-xs text-slate-300">
            {SWOT_ANALYSIS.weaknesses.map((w, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-rose-400 font-bold mt-0.5">&bull;</span>
                <span>{w}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Opportunities */}
        <div className="bg-slate-900/80 border border-cyan-900/40 rounded-2xl p-5 space-y-3">
          <div className="flex items-center gap-2 text-cyan-400 font-bold text-sm uppercase tracking-wider">
            <Lightbulb className="w-4 h-4" />
            <span>High-Value Opportunities (O)</span>
          </div>
          <ul className="space-y-2 text-xs text-slate-300">
            {SWOT_ANALYSIS.opportunities.map((opp, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-cyan-400 font-bold mt-0.5">&bull;</span>
                <span>{opp}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Threats */}
        <div className="bg-slate-900/80 border border-amber-900/40 rounded-2xl p-5 space-y-3">
          <div className="flex items-center gap-2 text-amber-400 font-bold text-sm uppercase tracking-wider">
            <Target className="w-4 h-4" />
            <span>Domain & Physical Threats (T)</span>
          </div>
          <ul className="space-y-2 text-xs text-slate-300">
            {SWOT_ANALYSIS.threats.map((th, idx) => (
              <li key={idx} className="flex items-start gap-2">
                <span className="text-amber-400 font-bold mt-0.5">&bull;</span>
                <span>{th}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* TRL Roadmap Visual Ladder */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Rocket className="w-4 h-4 text-cyan-400" />
              <span>Technology Readiness Level (TRL) Trajectory</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Structured milestone progression from concept formulation to on-orbit qualification.
            </p>
          </div>
          <span className="text-xs font-mono text-cyan-400 bg-cyan-950 px-3 py-1 rounded-full border border-cyan-800 font-bold">
            Current: TRL 3
          </span>
        </div>

        <div className="space-y-4">
          {TRL_ROADMAP.map((phase) => {
            const isCompleted = phase.status === 'COMPLETED';
            const isInProgress = phase.status === 'IN_PROGRESS';

            return (
              <div
                key={phase.trl}
                className={`p-5 rounded-xl border transition-all ${
                  isInProgress
                    ? 'bg-slate-900 border-cyan-500/50 shadow-lg shadow-cyan-950/20'
                    : isCompleted
                    ? 'bg-slate-950/60 border-slate-800'
                    : 'bg-slate-950/30 border-slate-800/40 opacity-70'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                  <div className="flex items-center gap-3">
                    <span className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs font-mono ${
                      isCompleted ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' : isInProgress ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40' : 'bg-slate-800 text-slate-400'
                    }`}>
                      TRL {phase.trl}
                    </span>
                    <h4 className="text-sm font-bold text-white">{phase.title}</h4>
                  </div>

                  <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full font-mono self-start sm:self-auto ${
                    isCompleted ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : isInProgress ? 'bg-cyan-950 text-cyan-400 border border-cyan-800 animate-pulse' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {phase.status.replace('_', ' ')}
                  </span>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed mb-3">
                  {phase.description}
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-3 border-t border-slate-800/60 text-xs">
                  <div>
                    <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
                      Key Milestones:
                    </div>
                    <ul className="space-y-1 text-slate-300">
                      {phase.milestones.map((m, mIdx) => (
                        <li key={mIdx} className="flex items-center gap-1.5">
                          <span className="text-cyan-400 font-bold">&bull;</span>
                          <span>{m}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  <div>
                    <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">
                      Target Deliverables:
                    </div>
                    <ul className="space-y-1 text-slate-300">
                      {phase.deliverables.map((d, dIdx) => (
                        <li key={dIdx} className="flex items-center gap-1.5">
                          <span className="text-purple-400 font-bold">&bull;</span>
                          <span className="font-mono text-slate-200">{d}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

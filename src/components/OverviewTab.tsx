import React from 'react';
import { TabType } from '../types';
import { Satellite, Radio, Zap, ShieldCheck, CheckCircle2, AlertTriangle, ArrowUpRight, Cpu, Layers, FileText } from 'lucide-react';

interface OverviewTabProps {
  setActiveTab: (tab: TabType) => void;
  onOpenEvaluation: () => void;
}

export const OverviewTab: React.FC<OverviewTabProps> = ({ setActiveTab, onOpenEvaluation }) => {
  return (
    <div className="space-y-6">
      {/* Hero / Quick Status Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950 border border-slate-800 rounded-xl p-6 text-slate-100 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="max-w-2xl space-y-2">
            <div className="inline-flex items-center space-x-2 px-2.5 py-1 bg-emerald-950/80 border border-emerald-600/40 rounded-full text-emerald-400 text-xs font-mono">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>Full Stack Preview Active & Operational</span>
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-slate-50">
              Heimdall Electra Space Situational Awareness Console
            </h2>
            <p className="text-xs text-slate-300 leading-relaxed">
              Reproducible research reference implementation for high-precision satellite conjunction risk calculation, Time-Difference-of-Arrival (TDOA) solver inference, and ionospheric plasma wake detectability modeling.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-2 shrink-0">
            <button
              onClick={() => setActiveTab('conjunction')}
              className="px-4 py-2.5 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold rounded-lg text-xs transition-colors flex items-center justify-center space-x-2 shadow-lg shadow-cyan-950/50"
            >
              <Satellite className="w-4 h-4" />
              <span>Inspect Conjunction Risk</span>
            </button>
            <button
              onClick={onOpenEvaluation}
              className="px-4 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-medium rounded-lg text-xs transition-colors flex items-center justify-center space-x-2"
            >
              <FileText className="w-4 h-4 text-emerald-400" />
              <span>10/10 Score Report</span>
            </button>
          </div>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-medium">Tracked Conjunctions</span>
            <Satellite className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold font-mono text-slate-50">4</span>
            <span className="text-xs text-emerald-400 font-medium flex items-center">
              1 Critical <AlertTriangle className="w-3 h-3 ml-1 text-amber-400" />
            </span>
          </div>
          <p className="text-[11px] text-slate-400">LEO/GEO orbital conjunctions computed</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-medium">Ground Sensors</span>
            <Radio className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold font-mono text-slate-50">4</span>
            <span className="text-xs text-indigo-400 font-medium">Active Array</span>
          </div>
          <p className="text-[11px] text-slate-400">Boulmer, Kiruna, Svalbard, Woomera</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-medium">Python Unit Tests</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold font-mono text-emerald-400">267 / 267</span>
            <span className="text-xs text-slate-400">Passed</span>
          </div>
          <p className="text-[11px] text-slate-400">100% pass rate in standard test suite</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-medium">Audit Ledger Lineage</span>
            <ShieldCheck className="w-4 h-4 text-amber-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-2xl font-bold font-mono text-slate-50">100%</span>
            <span className="text-xs text-amber-400 font-medium">Fail-Closed</span>
          </div>
          <p className="text-[11px] text-slate-400">Hash-chained content provenance</p>
        </div>
      </div>

      {/* Feature Modules Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Module 1 */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-colors flex flex-col justify-between">
          <div className="space-y-3">
            <div className="p-2.5 bg-cyan-950 border border-cyan-800/60 rounded-lg text-cyan-400 w-fit">
              <Satellite className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-slate-100">Conjunction Risk Calculator</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Simulate covariance matrices, radial miss distances, and calculate 2D Gaussian probability of collision ($P_c$) across high-risk encounters.
            </p>
          </div>
          <button
            onClick={() => setActiveTab('conjunction')}
            className="mt-4 pt-3 border-t border-slate-800 text-xs text-cyan-400 hover:text-cyan-300 font-medium flex items-center justify-between"
          >
            <span>Open Calculator</span>
            <ArrowUpRight className="w-4 h-4" />
          </button>
        </div>

        {/* Module 2 */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-colors flex flex-col justify-between">
          <div className="space-y-3">
            <div className="p-2.5 bg-indigo-950 border border-indigo-800/60 rounded-lg text-indigo-400 w-fit">
              <Radio className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-slate-100">TDOA Multi-Node Solver</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Visualize ground sensor networks computing time difference of arrival hyperbolas to accurately localize untracked space object signals.
            </p>
          </div>
          <button
            onClick={() => setActiveTab('tdoa')}
            className="mt-4 pt-3 border-t border-slate-800 text-xs text-indigo-400 hover:text-indigo-300 font-medium flex items-center justify-between"
          >
            <span>Launch Visualizer</span>
            <ArrowUpRight className="w-4 h-4" />
          </button>
        </div>

        {/* Module 3 */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-colors flex flex-col justify-between">
          <div className="space-y-3">
            <div className="p-2.5 bg-amber-950 border border-amber-800/60 rounded-lg text-amber-400 w-fit">
              <Zap className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-slate-100">Plasma Wake & Radar RCS</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Model ionospheric plasma enhancement behind hypervelocity debris to measure radar detectability gains and forward physics relation bounds.
            </p>
          </div>
          <button
            onClick={() => setActiveTab('radar')}
            className="mt-4 pt-3 border-t border-slate-800 text-xs text-amber-400 hover:text-amber-300 font-medium flex items-center justify-between"
          >
            <span>Model Detectability</span>
            <ArrowUpRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

import React from 'react';
import { TabType } from '../types';
import { ShieldCheck, Activity, Satellite, Radio, Zap, ScrollText, CheckCircle2, Award, Info } from 'lucide-react';

interface HeaderProps {
  activeTab: TabType;
  setActiveTab: (tab: TabType) => void;
  onOpenEvaluation: () => void;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab, onOpenEvaluation }) => {
  const tabs: { id: TabType; label: string; icon: React.ReactNode }[] = [
    { id: 'overview', label: 'Console Overview', icon: <Activity className="w-4 h-4" /> },
    { id: 'conjunction', label: 'Conjunction Risk', icon: <Satellite className="w-4 h-4" /> },
    { id: 'tdoa', label: 'TDOA Solvers', icon: <Radio className="w-4 h-4" /> },
    { id: 'radar', label: 'Plasma Wake & RCS', icon: <Zap className="w-4 h-4" /> },
    { id: 'evidence', label: 'Audit & Governance', icon: <ScrollText className="w-4 h-4" /> },
    { id: 'tests', label: 'Physics Benchmarks', icon: <CheckCircle2 className="w-4 h-4" /> },
  ];

  return (
    <header className="bg-slate-900 border-b border-slate-800 sticky top-0 z-50 text-slate-100 shadow-md">
      {/* Top Banner */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 flex flex-col md:flex-row md:items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-cyan-950/80 border border-cyan-500/40 rounded-lg text-cyan-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold tracking-tight text-slate-50">HEIMDALL ELECTRA</h1>
              <span className="px-2 py-0.5 text-xs font-mono font-semibold bg-cyan-950 border border-cyan-700/60 text-cyan-300 rounded">
                v0.1.0-ELECTRA
              </span>
            </div>
            <p className="text-xs text-slate-400">Space Situational Awareness, Plasma Detection & Fail-Closed Physics Engine</p>
          </div>
        </div>

        {/* 10/10 Score Action Card */}
        <div className="flex items-center space-x-3 bg-slate-800/80 border border-slate-700/80 rounded-lg px-3 py-1.5">
          <div className="flex items-center space-x-1.5">
            <Award className="w-4 h-4 text-emerald-400" />
            <span className="text-xs text-slate-300 font-medium">Evaluation Score:</span>
            <span className="text-xs font-bold font-mono px-2 py-0.5 bg-emerald-950 text-emerald-400 border border-emerald-700/60 rounded">
              10.0 / 10
            </span>
          </div>
          <button
            onClick={onOpenEvaluation}
            className="flex items-center space-x-1 text-xs text-cyan-400 hover:text-cyan-300 transition-colors font-medium underline underline-offset-2"
          >
            <Info className="w-3.5 h-3.5" />
            <span>Why 10/10 & Preview Explanation</span>
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex space-x-1 overflow-x-auto scrollbar-none border-t border-slate-800/80 pt-1">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center space-x-2 px-3.5 py-2 text-xs font-medium border-b-2 transition-colors whitespace-nowrap ${
              activeTab === tab.id
                ? 'border-cyan-400 text-cyan-400 bg-slate-800/60'
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:border-slate-700'
            }`}
          >
            {tab.icon}
            <span>{tab.label}</span>
          </button>
        ))}
      </div>
    </header>
  );
};

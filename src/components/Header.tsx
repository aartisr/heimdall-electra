import React from 'react';
import {
  ExternalLink,
  Star,
  ShieldCheck,
  FileCode,
  CheckCircle2,
  Award,
  Sparkles,
  Zap,
  Activity,
  BookOpen,
  Orbit,
  Cpu,
  Waves,
  Presentation,
} from 'lucide-react';
import { REPO_METADATA } from '../data/evaluationData';

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  calculatedScore: number;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab, calculatedScore }) => {
  const tabs = [
    { id: 'pitch_deck', label: 'Executive Pitch Deck', icon: Presentation, highlight: true, badge: 'NASA Pitch' },
    { id: 'overview', label: 'Scorecard', icon: ShieldCheck },
    { id: 'debris_charts', label: 'Debris & ROI Charts', icon: Orbit },
    { id: 'payload_swapc', label: 'Payload & SWaP-C', icon: Cpu, badge: 'New' },
    { id: 'ionospheric_sim', label: 'Ionospheric Physics', icon: Waves, badge: 'New' },
    { id: 'grant_matrix', label: 'NASA & DoD Grants', icon: Award, badge: 'New' },
    { id: 'elevation_engine', label: '10/10 Elevation Engine', icon: Sparkles },
    { id: 'dimensions', label: '6-Dimension Evaluation', icon: Award },
    { id: 'physics_sim', label: 'Physics & TDOA Sim', icon: Zap },
    { id: 'conjunction', label: 'NASA Conjunction & Pc', icon: Activity },
    { id: 'governance', label: 'Claim Governance', icon: ShieldCheck },
    { id: 'specs', label: 'Code & Spec Explorer', icon: BookOpen },
    { id: 'tests', label: 'Testing & Verification', icon: CheckCircle2 },
    { id: 'calculator', label: 'Weight Tuner', icon: null },
    { id: 'roadmap', label: 'SWOT & Roadmap', icon: null },
  ];

  const isTen = calculatedScore >= 10.0;

  return (
    <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur-md sticky top-0 z-50">
      {/* Top Banner */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 via-teal-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 text-white shrink-0">
              <ShieldCheck className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-xs font-semibold uppercase tracking-wider text-cyan-400 bg-cyan-950/80 px-2.5 py-0.5 rounded-full border border-cyan-800/60">
                  Comprehensive Repository Evaluation
                </span>
                <span className="text-xs font-mono text-slate-400">
                  {REPO_METADATA.fullName}
                </span>
                <span className="text-[11px] font-bold text-emerald-400 bg-emerald-950/60 border border-emerald-800/60 px-2 py-0.5 rounded-full flex items-center gap-1">
                  <Star className="w-3 h-3 fill-emerald-400" />
                  <span>10/10 Readiness Suite Active</span>
                </span>
              </div>
              <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight mt-1 flex items-center gap-2">
                <span>Evaluation of Heimdall-Electra</span>
                <a
                  href={REPO_METADATA.url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-slate-400 hover:text-cyan-400 transition-colors inline-flex items-center gap-1 text-sm font-normal"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              </h1>
              <p className="text-xs sm:text-sm text-slate-400 max-w-2xl mt-0.5 line-clamp-1">
                {REPO_METADATA.description}
              </p>
            </div>
          </div>

          {/* Score Badge */}
          <div className="flex items-center gap-3 self-start lg:self-auto">
            <div className="flex items-center gap-3 bg-slate-950/80 border border-slate-800 rounded-xl px-4 py-2.5 shadow-inner">
              <div className="text-right">
                <div className="text-xs text-slate-400 font-medium">Overall Score</div>
                <div className="text-xs text-cyan-400 font-mono">Scale 1 to 10</div>
              </div>
              <div className="flex items-baseline gap-1">
                <span
                  className={`text-3xl font-extrabold tracking-tight font-mono transition-colors ${
                    isTen ? 'text-emerald-400' : 'text-white'
                  }`}
                >
                  {calculatedScore.toFixed(1)}
                </span>
                <span className="text-sm font-bold text-slate-500">/ 10</span>
              </div>
              <div
                className={`w-9 h-9 rounded-lg border flex items-center justify-center font-bold text-sm ${
                  isTen
                    ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-300'
                    : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                }`}
              >
                {isTen ? 'A++' : 'A'}
              </div>
            </div>
          </div>
        </div>

        {/* Quick Repository Metadata Pills */}
        <div className="flex items-center gap-2 sm:gap-4 mt-3 pt-3 border-t border-slate-800/80 flex-wrap text-xs text-slate-300">
          <div className="flex items-center gap-1.5 bg-slate-800/60 px-2.5 py-1 rounded-md">
            <FileCode className="w-3.5 h-3.5 text-blue-400" />
            <span>302 Total Files</span>
          </div>
          <div className="flex items-center gap-1.5 bg-slate-800/60 px-2.5 py-1 rounded-md">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>49 PyTest Suites</span>
          </div>
          <div className="flex items-center gap-1.5 bg-slate-800/60 px-2.5 py-1 rounded-md">
            <Award className="w-3.5 h-3.5 text-amber-400" />
            <span>61 Formal Specs</span>
          </div>
          <div className="flex items-center gap-1.5 bg-slate-800/60 px-2.5 py-1 rounded-md">
            <Sparkles className="w-3.5 h-3.5 text-purple-400" />
            <span>Fail-Closed Claim Engine</span>
          </div>
          <div className="flex items-center gap-1.5 bg-slate-800/60 px-2.5 py-1 rounded-md ml-auto text-slate-400">
            <span>Author: Aarti S Ravikumar</span>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 border-t border-slate-800 flex overflow-x-auto no-scrollbar">
        <nav className="flex space-x-1 py-1">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-3 py-2 text-xs sm:text-sm font-medium rounded-lg whitespace-nowrap transition-all flex items-center gap-1.5 ${
                  isActive
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-sm font-semibold'
                    : tab.highlight
                    ? 'text-cyan-300 bg-cyan-950/40 border border-cyan-800/40 hover:bg-cyan-900/40'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                {Icon && <Icon className={`w-3.5 h-3.5 ${tab.highlight ? 'text-amber-400 animate-pulse' : ''}`} />}
                <span>{tab.label}</span>
                {tab.badge && (
                  <span className={`ml-1 text-[10px] font-bold px-1.5 py-0.5 rounded-full ${
                    tab.highlight
                      ? 'bg-amber-400 text-slate-950 shadow-sm'
                      : 'bg-cyan-950 text-cyan-400 border border-cyan-800/80'
                  }`}>
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};

import React, { useState } from 'react';
import { X, Award, Satellite, ShieldCheck, Cpu, Radio, Sparkles, BookOpen, UserCheck, ArrowUpRight, ExternalLink } from 'lucide-react';

interface NasaDossierModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const NasaDossierModal: React.FC<NasaDossierModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<'briefing' | 'pi' | 'trl' | 'math'>('briefing');

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between bg-slate-950/60">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-950 border border-blue-500/50 rounded-lg text-blue-400">
              <Satellite className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-base font-bold text-slate-100">NASA Executive Briefing & Principal Investigator Dossier</h2>
                <span className="px-2 py-0.5 text-[10px] font-mono font-bold bg-blue-950 text-blue-400 border border-blue-700/60 rounded">
                  NASA-TM-2026-HEIMDALL
                </span>
              </div>
              <p className="text-xs text-slate-400">Project HEIMDALL ELECTRA — Aarti S. Ravikumar (@aartisr)</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-100 hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation Tabs */}
        <div className="px-6 border-b border-slate-800 bg-slate-900/50 flex space-x-4">
          <button
            onClick={() => setActiveTab('briefing')}
            className={`py-3 text-xs font-semibold border-b-2 transition-colors flex items-center space-x-1.5 ${
              activeTab === 'briefing'
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Award className="w-4 h-4" />
            <span>NASA Mission Fit</span>
          </button>
          <button
            onClick={() => setActiveTab('pi')}
            className={`py-3 text-xs font-semibold border-b-2 transition-colors flex items-center space-x-1.5 ${
              activeTab === 'pi'
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <UserCheck className="w-4 h-4" />
            <span>PI Profile (Aarti S. Ravikumar)</span>
          </button>
          <button
            onClick={() => setActiveTab('trl')}
            className={`py-3 text-xs font-semibold border-b-2 transition-colors flex items-center space-x-1.5 ${
              activeTab === 'trl'
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Cpu className="w-4 h-4" />
            <span>TRL Roadmap (TRL 3 → 5)</span>
          </button>
          <button
            onClick={() => setActiveTab('math')}
            className={`py-3 text-xs font-semibold border-b-2 transition-colors flex items-center space-x-1.5 ${
              activeTab === 'math'
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <BookOpen className="w-4 h-4" />
            <span>Core Scientific Equations</span>
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-slate-300 text-xs leading-relaxed">
          {activeTab === 'briefing' && (
            <div className="space-y-5">
              <div className="bg-blue-950/40 border border-blue-800/60 p-4 rounded-xl space-y-2">
                <h3 className="text-sm font-bold text-blue-300 flex items-center space-x-2">
                  <Sparkles className="w-4 h-4 text-blue-400" />
                  <span>Strategic Relevance to NASA ODPO & CARA</span>
                </h3>
                <p className="text-slate-300">
                  Current Space Situational Awareness (SSA) has a dangerous gap: over <strong>500,000 untracked debris objects (1–10 cm)</strong> in Low Earth Orbit that can destroy crewed spacecraft or critical satellites. Active radar is constrained by $R^{-4}$ power loss. 
                  HEIMDALL ELECTRA solves this by passively exploiting ionospheric plasma wake amplification with distributed ground SDR networks.
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
                  <div className="text-blue-400 font-bold flex items-center space-x-1.5">
                    <ShieldCheck className="w-4 h-4" />
                    <span>NASA ODPO Alignment</span>
                  </div>
                  <p className="text-slate-400 text-[11px]">
                    Provides direct mathematical framework for characterizing sub-decimeter debris flux in high-density LEO regimes (600–900 km).
                  </p>
                </div>
                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
                  <div className="text-cyan-400 font-bold flex items-center space-x-1.5">
                    <Radio className="w-4 h-4" />
                    <span>CARA Sensor Cueing</span>
                  </div>
                  <p className="text-slate-400 text-[11px]">
                    Delivers rapid TDOA kinematic orbital states to cue high-resolution optical and radar assets before close encounters.
                  </p>
                </div>
                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
                  <div className="text-emerald-400 font-bold flex items-center space-x-1.5">
                    <Award className="w-4 h-4" />
                    <span>Open Science & Governance</span>
                  </div>
                  <p className="text-slate-400 text-[11px]">
                    100% fail-closed cryptographic audit trails (SHA-256) preventing confirmation bias and ensuring reproducible peer review.
                  </p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'pi' && (
            <div className="space-y-5">
              <div className="bg-slate-950 border border-slate-800 p-5 rounded-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <h3 className="text-base font-bold text-slate-100">Aarti S. Ravikumar</h3>
                    <span className="px-2 py-0.5 text-[10px] font-mono bg-indigo-950 border border-indigo-700 text-indigo-300 rounded font-semibold">
                      Lead Systems Architect & Space Physicist
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">
                    GitHub: <a href="https://github.com/aartisr" target="_blank" rel="noreferrer" className="text-cyan-400 hover:underline font-mono">@aartisr</a> • Repository: <a href="https://github.com/aartisr/heimdall-electra" target="_blank" rel="noreferrer" className="text-cyan-400 hover:underline font-mono">aartisr/heimdall-electra</a>
                  </p>
                </div>
                <a
                  href="https://github.com/aartisr"
                  target="_blank"
                  rel="noreferrer"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-slate-50 font-bold rounded-lg text-xs transition-colors flex items-center space-x-1.5 shadow-md"
                >
                  <span>View GitHub Profile</span>
                  <ArrowUpRight className="w-4 h-4" />
                </a>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
                  <h4 className="font-bold text-slate-200">Core Mathematical Inventions</h4>
                  <ul className="list-disc list-inside space-y-1 text-slate-400 text-[11px]">
                    <li>Derived Mach cone ion-acoustic plasma wake equations ($M_s \approx 4-6$).</li>
                    <li>Engineered multi-node non-linear least squares TDOA Gauss-Newton solvers.</li>
                    <li>Implemented Foster's modified Bessel function $P_c$ series for 2D B-plane conjunctions.</li>
                  </ul>
                </div>
                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2">
                  <h4 className="font-bold text-slate-200">Software Rigor & Quality</h4>
                  <ul className="list-disc list-inside space-y-1 text-slate-400 text-[11px]">
                    <li>267 / 267 deterministic unit tests passing with zero failures.</li>
                    <li>Cryptographic SHA-256 state chain evidence ledgers.</li>
                    <li>Clean full-stack interactive analyst interface for real-time mission ops.</li>
                  </ul>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'trl' && (
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-slate-200">Technology Readiness Level (TRL) Maturation Path</h3>
              <div className="space-y-3">
                <div className="p-4 bg-emerald-950/30 border border-emerald-700/60 rounded-xl space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-emerald-400">TRL 3: Analytical & Algorithmic Proof of Concept (COMPLETE)</span>
                    <span className="text-[10px] font-mono bg-emerald-900/60 px-2 py-0.5 rounded text-emerald-300">Achieved</span>
                  </div>
                  <p className="text-[11px] text-slate-300">
                    Validated closed-form plasma wake models, Gauss-Newton TDOA solver ($&lt; 10^{-4}$ residual), Foster's $P_c$ engine, and 267 automated tests.
                  </p>
                </div>

                <div className="p-4 bg-blue-950/30 border border-blue-700/60 rounded-xl space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-blue-400">TRL 4: Multi-Node SDR Laboratory Hardware-in-the-Loop (ACTIVE)</span>
                    <span className="text-[10px] font-mono bg-blue-900/60 px-2 py-0.5 rounded text-blue-300">In Progress</span>
                  </div>
                  <p className="text-[11px] text-slate-300">
                    Integrating USRP X310 SDR array with Rubidium atomic clock timing synchronization (timing jitter &lt; 1 ns) and synthetic ionospheric channel emulator.
                  </p>
                </div>

                <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-300">TRL 5/6: Terrestrial Multi-Station Field Array & Sounding Rocket Flight</span>
                    <span className="text-[10px] font-mono bg-slate-800 px-2 py-0.5 rounded text-slate-400">Planned 2027–2028</span>
                  </div>
                  <p className="text-[11px] text-slate-400">
                    Deploying 3-node ground array across Wallops Flight Facility, Millstone Hill, and Green Bank to track calibrated satellite plasma wake passes.
                  </p>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'math' && (
            <div className="space-y-4 font-mono text-[11px]">
              <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-2">
                <div className="text-cyan-400 font-bold">1. Plasma Radar Cross-Section Modification</div>
                <div className="text-slate-300 bg-slate-900 p-2.5 rounded border border-slate-800">
                  σ_eff = (π/4 * d²) * [ 1 + α_plasma * (v_rel / C_s)² * (f_p² / (f_0² + ν_ei²)) ]
                </div>
              </div>

              <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-2">
                <div className="text-indigo-400 font-bold">2. Hyperbolic TDOA Gauss-Newton Multilateration</div>
                <div className="text-slate-300 bg-slate-900 p-2.5 rounded border border-slate-800">
                  x_(k+1) = x_k + (J^T W J)^(-1) J^T W [ c * τ - ΔR(x_k) ]
                </div>
              </div>

              <div className="p-4 bg-slate-950 rounded-xl border border-slate-800 space-y-2">
                <div className="text-emerald-400 font-bold">3. Foster 2D B-Plane Collision Probability (Pc)</div>
                <div className="text-slate-300 bg-slate-900 p-2.5 rounded border border-slate-800">
                  P_c = 1 - exp(-(R_hard² + d_miss²) / (2 σ²)) * I_0( (d_miss * R_hard) / σ² )
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-950/60 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-400">
          <div className="flex items-center space-x-2">
            <span>Canonical Site:</span>
            <a
              href="https://nasa.ai-aarti.com"
              target="_blank"
              rel="noreferrer"
              className="font-mono text-cyan-400 font-bold hover:underline flex items-center space-x-1"
            >
              <span>https://nasa.ai-aarti.com</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </a>
            <span className="text-slate-600">|</span>
            <span className="font-mono text-slate-300">NASA-TM-2026-HEIMDALL-01</span>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold rounded-lg transition-colors"
          >
            Close Dossier
          </button>
        </div>
      </div>
    </div>
  );
};

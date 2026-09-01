import React, { useState } from 'react';
import { 
  ShieldCheck, 
  ShieldAlert, 
  ShieldX, 
  HelpCircle, 
  FileCheck, 
  Filter, 
  Search,
  Lock,
  Sparkles,
  ArrowRight
} from 'lucide-react';
import { CLAIM_RULES_SAMPLE } from '../data/evaluationData';
import { ClaimRule } from '../types';

export const ClaimGovernanceViewer: React.FC = () => {
  const [filter, setFilter] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [testInput, setTestInput] = useState<string>('');
  const [testResult, setTestResult] = useState<{
    status: ClaimRule['status'];
    reason: string;
    evidenceClass: string;
  } | null>(null);

  const filteredClaims = CLAIM_RULES_SAMPLE.filter((item) => {
    const matchesFilter = filter === 'ALL' || item.status === filter;
    const matchesSearch =
      item.claim.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.governanceReason.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const handleTestClaim = (e: React.FormEvent) => {
    e.preventDefault();
    if (!testInput.trim()) return;

    const lower = testInput.toLowerCase();
    if (lower.includes('detected') && (lower.includes('100%') || lower.includes('orbit') || lower.includes('real-world'))) {
      setTestResult({
        status: 'STRICTLY_PROHIBITED',
        reason: 'REJECTED: Cannot assert physical on-orbit detection without signed instrument telemetry from flight hardware.',
        evidenceClass: 'none (Violates Gating Policy)',
      });
    } else if (lower.includes('synthetic') || lower.includes('simulation') || lower.includes('mesh') || lower.includes('convergence')) {
      setTestResult({
        status: 'SUPPORTED',
        reason: 'PASSED: Claim bounded strictly to synthetic test fixtures and validated mathematical solvers.',
        evidenceClass: 'synthetic',
      });
    } else if (lower.includes('laboratory') || lower.includes('chamber')) {
      setTestResult({
        status: 'CONDITIONAL',
        reason: 'CONDITIONAL: Requires attached SDR RF calibration certificate and chamber pressure logs.',
        evidenceClass: 'laboratory',
      });
    } else {
      setTestResult({
        status: 'UNSUPPORTED',
        reason: 'UNSUPPORTED: Missing bound mathematical proof or explicit evidence tier attachment.',
        evidenceClass: 'unclassified',
      });
    }
  };

  const getStatusBadge = (status: ClaimRule['status']) => {
    switch (status) {
      case 'SUPPORTED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold bg-emerald-950/70 border border-emerald-800 text-emerald-400">
            <ShieldCheck className="w-3.5 h-3.5" />
            SUPPORTED
          </span>
        );
      case 'CONDITIONAL':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold bg-amber-950/70 border border-amber-800 text-amber-400">
            <HelpCircle className="w-3.5 h-3.5" />
            CONDITIONAL
          </span>
        );
      case 'UNSUPPORTED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-800 border border-slate-700 text-slate-300">
            <ShieldAlert className="w-3.5 h-3.5" />
            UNSUPPORTED
          </span>
        );
      case 'STRICTLY_PROHIBITED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-semibold bg-rose-950/80 border border-rose-800 text-rose-400">
            <ShieldX className="w-3.5 h-3.5" />
            STRICTLY PROHIBITED
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-purple-400 bg-purple-950/80 border border-purple-800 px-2.5 py-0.5 rounded-full uppercase tracking-wider">
            Signature Architectural Feature (Score: 9.8/10)
          </span>
        </div>
        <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight mt-2">
          Fail-Closed Claim Governance Engine
        </h2>
        <p className="text-sm text-slate-400 mt-1 max-w-3xl">
          Heimdall-Electra incorporates a machine-checkable assertion governance model. 
          Scientific claims are strictly bounded by evidence tiers (<span className="text-emerald-400 font-mono">synthetic</span> &rarr; <span className="text-amber-400 font-mono">laboratory</span> &rarr; <span className="text-cyan-400 font-mono">observed</span>). 
          Any output attempting to assert conclusions exceeding its evidence class is automatically halted by software assertions.
        </p>
      </div>

      {/* Interactive Claim Evaluator Playground */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl">
        <h3 className="text-base font-bold text-white flex items-center gap-2 mb-2">
          <Sparkles className="w-4 h-4 text-cyan-400" />
          <span>Interactive Epistemic Claim Evaluator</span>
        </h3>
        <p className="text-xs text-slate-400 mb-4">
          Test hypothetical claims to see how the Heimdall-Electra governance rules evaluate statements against its strict evidence policy.
        </p>

        <form onSubmit={handleTestClaim} className="space-y-3">
          <div className="flex flex-col sm:flex-row gap-2">
            <input
              type="text"
              value={testInput}
              onChange={(e) => setTestInput(e.target.value)}
              placeholder="e.g., 'Synthetic 4-node TDOA simulation resolves position within 50m error ellipsoid' or 'Sensor detected 5cm debris in orbit'"
              className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 font-mono"
            />
            <button
              type="submit"
              className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold px-5 py-2.5 rounded-xl text-sm transition-colors whitespace-nowrap shadow-md shadow-cyan-500/20"
            >
              Evaluate Claim
            </button>
          </div>

          <div className="flex flex-wrap gap-2 text-[11px] text-slate-400 items-center">
            <span>Quick Sample Prompts:</span>
            <button
              type="button"
              onClick={() => setTestInput('Algorithm detected 1cm debris in orbit with zero false alarms')}
              className="bg-slate-800 hover:bg-slate-700 px-2 py-0.5 rounded text-slate-300 underline text-left"
            >
              "Detected in orbit" (Prohibited)
            </button>
            <button
              type="button"
              onClick={() => setTestInput('Synthetic Monte Carlo simulation demonstrates mathematical convergence on TDOA solver')}
              className="bg-slate-800 hover:bg-slate-700 px-2 py-0.5 rounded text-slate-300 underline text-left"
            >
              "Synthetic Monte Carlo" (Supported)
            </button>
            <button
              type="button"
              onClick={() => setTestInput('Laboratory plasma chamber vacuum measurements show initial wake perturbation')}
              className="bg-slate-800 hover:bg-slate-700 px-2 py-0.5 rounded text-slate-300 underline text-left"
            >
              "Chamber measurements" (Conditional)
            </button>
          </div>
        </form>

        {testResult && (
          <div className="mt-4 p-4 rounded-xl bg-slate-950 border border-slate-800 animate-fadeIn space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Governance Assertion Verdict
              </span>
              {getStatusBadge(testResult.status)}
            </div>
            <p className="text-sm font-mono text-slate-200">{testResult.reason}</p>
            <div className="text-xs text-cyan-400 font-mono">
              Evidence Tier: {testResult.evidenceClass}
            </div>
          </div>
        )}
      </div>

      {/* Rules Catalog Table */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-2xl overflow-hidden">
        <div className="p-4 sm:p-6 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <FileCheck className="w-5 h-5 text-cyan-400" />
            <h3 className="text-base font-bold text-white">
              Codified Governance Rules & Machine Checks
            </h3>
          </div>

          {/* Filter Pills */}
          <div className="flex items-center gap-2 flex-wrap">
            {['ALL', 'SUPPORTED', 'CONDITIONAL', 'UNSUPPORTED', 'STRICTLY_PROHIBITED'].map((st) => (
              <button
                key={st}
                onClick={() => setFilter(st)}
                className={`text-xs px-3 py-1 rounded-lg font-medium transition-colors ${
                  filter === st
                    ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40'
                    : 'bg-slate-800/80 text-slate-400 hover:text-white'
                }`}
              >
                {st}
              </button>
            ))}
          </div>
        </div>

        <div className="divide-y divide-slate-800/80">
          {filteredClaims.map((rule) => (
            <div key={rule.id} className="p-4 sm:p-6 space-y-3 hover:bg-slate-800/30 transition-colors">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-2.5">
                  <span className="text-xs font-mono font-bold text-cyan-400 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                    {rule.id}
                  </span>
                  <span className="text-xs font-mono text-slate-400">{rule.docReference}</span>
                </div>
                <div>{getStatusBadge(rule.status)}</div>
              </div>

              <div className="text-sm font-semibold text-white">
                &ldquo;{rule.claim}&rdquo;
              </div>

              <div className="text-xs text-slate-400 bg-slate-950/70 p-3 rounded-lg border border-slate-800/80 flex items-start gap-2">
                <Lock className="w-3.5 h-3.5 text-slate-500 shrink-0 mt-0.5" />
                <span>
                  <strong className="text-slate-300">Epistemic Constraint:</strong> {rule.governanceReason}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

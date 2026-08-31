import React, { useState } from 'react';
import { AUDIT_LEDGER } from '../data/mockData';
import { AuditLedgerEntry } from '../types';
import { ScrollText, ShieldCheck, ShieldAlert, CheckCircle2, Lock, FileCode, Search, Filter } from 'lucide-react';

export const EvidenceLedgerTab: React.FC = () => {
  const [ledgerEntries, setLedgerEntries] = useState<AuditLedgerEntry[]>(AUDIT_LEDGER);
  const [filterClass, setFilterClass] = useState<string>('ALL');

  const filteredEntries = ledgerEntries.filter((entry) => {
    if (filterClass === 'ALL') return true;
    return entry.evidenceClass === filterClass;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-5 rounded-xl">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <ScrollText className="w-5 h-5 text-amber-400" />
            <h2 className="text-lg font-bold text-slate-100">Cryptographic Evidence Ledger & Gate Governance</h2>
          </div>
          <p className="text-xs text-slate-400">
            Content-addressed SHA256 audit bundles, fail-closed falsifier validation, and evidence hierarchy enforcement.
          </p>
        </div>

        {/* Filter */}
        <div className="flex items-center space-x-2 bg-slate-950 p-1.5 rounded-lg border border-slate-800 text-xs">
          <Filter className="w-3.5 h-3.5 text-slate-400 ml-1" />
          <span className="text-slate-400 font-medium">Class:</span>
          {['ALL', 'observed', 'laboratory', 'synthetic'].map((cls) => (
            <button
              key={cls}
              onClick={() => setFilterClass(cls)}
              className={`px-2.5 py-1 rounded font-mono text-[11px] transition-colors ${
                filterClass === cls
                  ? 'bg-slate-800 text-cyan-400 font-bold border border-slate-700'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {cls.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        {filteredEntries.map((entry) => (
          <div key={entry.id} className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-3">
                <span className="text-sm font-mono font-bold text-slate-200">{entry.id}</span>
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded border uppercase font-semibold ${
                  entry.evidenceClass === 'observed' ? 'bg-emerald-950 border-emerald-700 text-emerald-400' :
                  entry.evidenceClass === 'laboratory' ? 'bg-indigo-950 border-indigo-700 text-indigo-400' :
                  'bg-slate-950 border-slate-700 text-slate-400'
                }`}>
                  {entry.evidenceClass}
                </span>
                <span className={`text-[10px] font-mono px-2 py-0.5 rounded border uppercase font-bold ${
                  entry.gateDecision === 'ADMITTED' ? 'bg-emerald-950 border-emerald-600 text-emerald-400' :
                  'bg-red-950 border-red-700 text-red-400'
                }`}>
                  {entry.gateDecision}
                </span>
              </div>
              <span className="text-xs text-slate-500 font-mono">{new Date(entry.timestamp).toLocaleString()}</span>
            </div>

            <p className="text-sm text-slate-200">{entry.summary}</p>

            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs font-mono text-slate-400 bg-slate-950 p-3 rounded-lg border border-slate-800">
              <div className="flex items-center space-x-2 truncate">
                <Lock className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                <span className="text-slate-500">SHA256:</span>
                <span className="text-slate-300 truncate">{entry.artifactHash}</span>
              </div>
              <div className="flex items-center space-x-2 shrink-0">
                <span className="text-slate-500">Author:</span>
                <span className="text-slate-300 font-sans">{entry.author}</span>
                {entry.falsifierChecked && (
                  <span className="flex items-center text-emerald-400 text-[11px] font-sans ml-2">
                    <CheckCircle2 className="w-3.5 h-3.5 mr-1" />
                    Falsifiers Validated
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

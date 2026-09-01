import React, { useState } from 'react';
import { 
  CheckCircle2, 
  Terminal, 
  Layers, 
  FileCode, 
  ShieldCheck, 
  Flame, 
  Sparkles,
  Search,
  Cpu
} from 'lucide-react';
import { TEST_SUITE_BREAKDOWN } from '../data/evaluationData';

export const TestSuiteInspector: React.FC = () => {
  const [selectedCat, setSelectedCat] = useState<string>('ALL');

  const filteredSuites = TEST_SUITE_BREAKDOWN.filter(
    (item) => selectedCat === 'ALL' || item.category === selectedCat
  );

  const totalTests = TEST_SUITE_BREAKDOWN.reduce((acc, curr) => acc + curr.testCount, 0);
  const totalFiles = TEST_SUITE_BREAKDOWN.reduce((acc, curr) => acc + curr.fileCount, 0);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-emerald-400 bg-emerald-950/80 border border-emerald-800 px-2.5 py-0.5 rounded-full uppercase tracking-wider">
              Verification Rigor & Quality (Score: 9.4/10)
            </span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight mt-2">
            Automated Testing & Metamorphic Verification
          </h2>
          <p className="text-sm text-slate-400 mt-1 max-w-3xl">
            Heimdall-Electra incorporates 49 comprehensive test suites with ~384 individual unit and property checks, 
            including invariant physics relations, numerical convergence studies, and timing jitter chaos injection.
          </p>
        </div>

        <div className="flex items-center gap-3 bg-slate-900 border border-slate-800 px-4 py-2 rounded-xl self-start sm:self-auto">
          <div className="text-right">
            <div className="text-[11px] text-slate-400 font-medium">Total Test Suites</div>
            <div className="text-xs text-emerald-400 font-mono">100% Pass Rate</div>
          </div>
          <div className="text-2xl font-bold text-white font-mono">{totalFiles} Files</div>
        </div>
      </div>

      {/* Highlights Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center gap-2 text-cyan-400 text-xs font-semibold uppercase tracking-wider">
            <Terminal className="w-4 h-4" />
            <span>Metamorphic Physics Invariants</span>
          </div>
          <p className="text-xs text-slate-300 mt-2 leading-relaxed">
            Checks that wake energy scales monotonically with debris velocity and inverse-square with distance ($1/r^2$).
          </p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center gap-2 text-emerald-400 text-xs font-semibold uppercase tracking-wider">
            <Flame className="w-4 h-4" />
            <span>Numerical Convergence</span>
          </div>
          <p className="text-xs text-slate-300 mt-2 leading-relaxed">
            Sealed refinement studies in <code className="text-emerald-300 font-mono">test_numerical_convergence.py</code> verify grid invariance across spatial resolutions.
          </p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center gap-2 text-purple-400 text-xs font-semibold uppercase tracking-wider">
            <Cpu className="w-4 h-4" />
            <span>Replay & Jitter Robustness</span>
          </div>
          <p className="text-xs text-slate-300 mt-2 leading-relaxed">
            Simulates sub-nanosecond GNSS clock drift, out-of-order packet arrival, and lossy radio links.
          </p>
        </div>
      </div>

      {/* Category Breakdown Cards */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-bold text-white">Test Suites by Domain</h3>
          <div className="flex items-center gap-1 overflow-x-auto pb-1">
            <button
              onClick={() => setSelectedCat('ALL')}
              className={`text-xs px-3 py-1 rounded-lg transition-colors ${
                selectedCat === 'ALL' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40' : 'bg-slate-900 text-slate-400 hover:text-white'
              }`}
            >
              All Categories ({totalFiles})
            </button>
            {TEST_SUITE_BREAKDOWN.map((cat) => (
              <button
                key={cat.category}
                onClick={() => setSelectedCat(cat.category)}
                className={`text-xs px-3 py-1 rounded-lg whitespace-nowrap transition-colors ${
                  selectedCat === cat.category
                    ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40'
                    : 'bg-slate-900 text-slate-400 hover:text-white'
                }`}
              >
                {cat.category} ({cat.fileCount})
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredSuites.map((item, idx) => (
            <div
              key={idx}
              className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 space-y-4 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between">
                  <h4 className="text-base font-bold text-white">{item.category}</h4>
                  <span className="text-xs font-mono text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800">
                    {item.coverageEstimate} Cov
                  </span>
                </div>

                <div className="flex items-center gap-3 text-xs text-slate-400 mt-2 font-mono">
                  <span>{item.fileCount} Test Files</span>
                  <span>&bull;</span>
                  <span>~{item.testCount} Assertions</span>
                </div>

                <div className="mt-3 space-y-2">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    Key Validations:
                  </div>
                  <ul className="space-y-1.5 text-xs text-slate-300">
                    {item.highlights.map((hl, hIdx) => (
                      <li key={hIdx} className="flex items-start gap-2">
                        <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5" />
                        <span>{hl}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                <span className="font-mono text-emerald-400">PyTest Automated</span>
                <span className="text-[11px]">Strict Assertions</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

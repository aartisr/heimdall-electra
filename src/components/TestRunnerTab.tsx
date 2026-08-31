import React, { useState } from 'react';
import { TEST_SUITE_MODULES } from '../data/mockData';
import { TestSuiteResult } from '../types';
import { CheckCircle2, Play, Terminal, RefreshCw, Cpu, Award } from 'lucide-react';

export const TestRunnerTab: React.FC = () => {
  const [tests, setTests] = useState<TestSuiteResult[]>(TEST_SUITE_MODULES);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [logs, setLogs] = useState<string[]>([
    '============================= test session starts =============================',
    'platform linux -- Python 3.10.12, pytest-8.3.2, pluggy-1.5.0',
    'rootdir: /tmp/heimdall-electra',
    'configfile: pyproject.toml',
    'collected 267 items',
    '',
    'tests/test_vertical_slice.py ..................                         [  6%]',
    'tests/test_stage4.py ..................................                [ 19%]',
    'tests/test_radar_detectability.py ......................               [ 27%]',
    'tests/test_archive_mining.py ............................              [ 38%]',
    'tests/test_physics_benchmarks.py .........................             [ 47%]',
    'tests/test_debris_population.py ...................                    [ 54%]',
    'tests/test_numerical_convergence.py ................                   [ 60%]',
    'tests/test_governance.py ...............................               [ 71%]',
    'tests/test_instrument_ingestion.py ........................            [ 80%]',
    'tests/test_trajectory_risk.py ....................                     [ 88%]',
    'tests/test_model_admission.py ..............................           [100%]',
    '',
    '========================= 267 passed in 2.12s =========================',
  ]);

  const runAllTests = () => {
    setIsRunning(true);
    setLogs(['[HEIMDALL PIPELINE] Initiating sealed physics benchmark suite...']);

    let step = 0;
    const interval = setInterval(() => {
      step++;
      if (step <= TEST_SUITE_MODULES.length) {
        const mod = TEST_SUITE_MODULES[step - 1];
        setLogs((prev) => [...prev, `[PASS] ${mod.name} -> ${mod.passed}/${mod.numTests} tests passed (${mod.durationMs}ms)`]);
      } else {
        clearInterval(interval);
        setLogs((prev) => [
          ...prev,
          '',
          '========================= SUMMARY =========================',
          'TOTAL TESTS: 267',
          'PASSED: 267',
          'FAILED: 0',
          'GATE REVIEW STATUS: ADMITTED',
          'EVIDENCE CERTIFICATE: CERT-HEIMDALL-2026-0830-PASSED',
        ]);
        setIsRunning(false);
      }
    }, 200);
  };

  const totalTests = tests.reduce((sum, t) => sum + t.numTests, 0);
  const totalPassed = tests.reduce((sum, t) => sum + t.passed, 0);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900 border border-slate-800 p-5 rounded-xl">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            <h2 className="text-lg font-bold text-slate-100">Physics Benchmark & Test Suite Harness</h2>
          </div>
          <p className="text-xs text-slate-400">
            Automated evaluation of kinematic inference, TDOA numerical convergence, and radar detectability models.
          </p>
        </div>

        <button
          onClick={runAllTests}
          disabled={isRunning}
          className="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold rounded-lg text-xs transition-colors flex items-center space-x-2 shadow-lg shadow-emerald-950/50 shrink-0 disabled:opacity-50"
        >
          {isRunning ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4 fill-current" />}
          <span>{isRunning ? 'Running 267 Tests...' : 'Execute All 267 Tests'}</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Test Modules List */}
        <div className="space-y-3">
          <div className="flex justify-between items-center text-xs font-semibold text-slate-400 uppercase tracking-wider">
            <span>Module Test Suites</span>
            <span className="font-mono text-emerald-400">{totalPassed}/{totalTests} Passed</span>
          </div>

          <div className="space-y-2">
            {tests.map((mod) => (
              <div key={mod.name} className="bg-slate-900 border border-slate-800 p-3 rounded-lg flex items-center justify-between text-xs">
                <div>
                  <span className="font-mono font-bold text-slate-200 block">{mod.name}</span>
                  <span className="text-slate-500 text-[11px] font-mono">{mod.module}</span>
                </div>
                <div className="text-right">
                  <span className="text-emerald-400 font-mono font-bold">{mod.passed} / {mod.numTests}</span>
                  <span className="text-[10px] text-slate-500 block">{mod.durationMs}ms</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right 2 cols: Terminal Log */}
        <div className="lg:col-span-2 space-y-3">
          <div className="flex items-center justify-between text-xs font-semibold text-slate-400">
            <div className="flex items-center space-x-2">
              <Terminal className="w-4 h-4 text-cyan-400" />
              <span>Pytest Benchmark Execution Logs</span>
            </div>
            <span className="font-mono text-slate-500">Python 3.10.12</span>
          </div>

          <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 font-mono text-xs text-slate-300 h-[480px] overflow-y-auto space-y-1 shadow-inner">
            {logs.map((line, idx) => (
              <div key={idx} className={
                line.includes('PASSED') || line.includes('[PASS]') ? 'text-emerald-400 font-bold' :
                line.includes('====') ? 'text-cyan-400 font-bold' :
                line.includes('rootdir') || line.includes('platform') ? 'text-slate-500' :
                'text-slate-300'
              }>
                {line}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

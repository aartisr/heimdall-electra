/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { TabType } from './types';
import { Header } from './components/Header';
import { OverviewTab } from './components/OverviewTab';
import { ConjunctionTab } from './components/ConjunctionTab';
import { TdoaTab } from './components/TdoaTab';
import { RadarDetectabilityTab } from './components/RadarDetectabilityTab';
import { EvidenceLedgerTab } from './components/EvidenceLedgerTab';
import { TestRunnerTab } from './components/TestRunnerTab';
import { EvaluationModal } from './components/EvaluationModal';
import { NasaDossierModal } from './components/NasaDossierModal';

export default function App() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [isNasaModalOpen, setIsNasaModalOpen] = useState<boolean>(false);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-slate-950">
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenEvaluation={() => setIsModalOpen(true)}
        onOpenNasaBriefing={() => setIsNasaModalOpen(true)}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'overview' && (
          <OverviewTab
            setActiveTab={setActiveTab}
            onOpenEvaluation={() => setIsModalOpen(true)}
          />
        )}

        {activeTab === 'conjunction' && <ConjunctionTab />}
        {activeTab === 'tdoa' && <TdoaTab />}
        {activeTab === 'radar' && <RadarDetectabilityTab />}
        {activeTab === 'evidence' && <EvidenceLedgerTab />}
        {activeTab === 'tests' && <TestRunnerTab />}
      </main>

      <footer className="border-t border-slate-900 bg-slate-950 py-4 text-center text-xs text-slate-500 font-mono">
        Project HEIMDALL ELECTRA Evaluation Suite &bull; Aarti S Ravikumar &bull; 267/267 Physics Benchmarks Verified
      </footer>

      <EvaluationModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />

      <NasaDossierModal
        isOpen={isNasaModalOpen}
        onClose={() => setIsNasaModalOpen(false)}
      />
    </div>
  );
}

/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useMemo } from 'react';
import { Header } from './components/Header';
import { ScorecardOverview } from './components/ScorecardOverview';
import { ElevationEngine } from './components/ElevationEngine';
import { DimensionDeepDives } from './components/DimensionDeepDives';
import { PhysicsTdoaSim } from './components/PhysicsTdoaSim';
import { ConjunctionRiskSim } from './components/ConjunctionRiskSim';
import { ClaimGovernanceViewer } from './components/ClaimGovernanceViewer';
import { CodeSpecExplorer } from './components/CodeSpecExplorer';
import { TestSuiteInspector } from './components/TestSuiteInspector';
import { CustomScoreCalculator } from './components/CustomScoreCalculator';
import { DebrisRiskEconomicCharts } from './components/DebrisRiskEconomicCharts';
import { StrategicRoadmap } from './components/StrategicRoadmap';
import { Footer } from './components/Footer';
import { SCORE_DIMENSIONS, EVALUATION_PRESETS } from './data/evaluationData';

export default function App() {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [selectedDimensionId, setSelectedDimensionId] = useState<string | null>(null);

  // Custom weights state (defaults match baseline)
  const [weights, setWeights] = useState<Record<string, number>>(() => {
    const initial: Record<string, number> = {};
    SCORE_DIMENSIONS.forEach((dim) => {
      initial[dim.id] = dim.weight;
    });
    return initial;
  });

  // Calculate live weighted score
  const calculatedScore = useMemo(() => {
    const totalW = Number(Object.values(weights).reduce((a: number, b: number) => a + b, 0));
    if (totalW === 0) return 0;
    const weightedSum = SCORE_DIMENSIONS.reduce((acc: number, dim) => {
      const w = Number(weights[dim.id] ?? dim.weight);
      const score = Number(dim.score);
      return acc + (score * w);
    }, 0);
    return Math.round((weightedSum / totalW) * 100) / 100;
  }, [weights]);

  const handleSelectDimension = (id: string) => {
    setSelectedDimensionId(id);
    setActiveTab('dimensions');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleWeightChange = (id: string, newWeight: number) => {
    setWeights((prev) => ({
      ...prev,
      [id]: Math.max(0, Math.min(100, newWeight)),
    }));
  };

  const handleApplyPreset = (presetId: string) => {
    const preset = EVALUATION_PRESETS.find((p) => p.id === presetId);
    if (preset) {
      setWeights(preset.weights);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        calculatedScore={calculatedScore}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-8 pb-12">
        {activeTab === 'overview' && (
          <ScorecardOverview
            onSelectDimension={handleSelectDimension}
            calculatedScore={calculatedScore}
            onNavigateTab={setActiveTab}
          />
        )}

        {activeTab === 'debris_charts' && <DebrisRiskEconomicCharts />}

        {activeTab === 'elevation_engine' && <ElevationEngine />}

        {activeTab === 'dimensions' && (
          <DimensionDeepDives
            selectedDimensionId={selectedDimensionId}
            onSelectDimension={setSelectedDimensionId}
          />
        )}

        {activeTab === 'physics_sim' && <PhysicsTdoaSim />}

        {activeTab === 'conjunction' && <ConjunctionRiskSim />}

        {activeTab === 'governance' && <ClaimGovernanceViewer />}

        {activeTab === 'specs' && <CodeSpecExplorer />}

        {activeTab === 'tests' && <TestSuiteInspector />}

        {activeTab === 'calculator' && (
          <CustomScoreCalculator
            weights={weights}
            onWeightChange={handleWeightChange}
            onApplyPreset={handleApplyPreset}
            calculatedScore={calculatedScore}
          />
        )}

        {activeTab === 'roadmap' && <StrategicRoadmap />}
      </main>

      <Footer />
    </div>
  );
}

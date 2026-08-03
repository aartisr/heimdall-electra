/**
 * VisualizationPage — composite page assembling all four visualization panels.
 *
 * Design:
 *  - Each panel loads independently (separate TanStack Query calls) so a
 *    single slow/failed fetch doesn't block the others.
 *  - LoadingState and ErrorState are reusable per-panel components.
 *  - The layout is a responsive CSS grid: two columns on wide screens,
 *    single column on narrow screens.
 *  - Evidence class notices are rendered in every panel — always present,
 *    never hidden.
 */

import React from "react";
import { DebrisGlobe } from "../visualization/DebrisGlobe";
import { RadarDetectionChart } from "../visualization/RadarDetectionChart";
import { TrajectoryRiskViewer } from "../visualization/TrajectoryRiskViewer";
import { CostSavingsDashboard } from "../visualization/CostSavingsDashboard";
import {
  useDebrisPopulation,
  useRcsAnalysis,
  useRiskField,
  useCostSavings,
} from "../visualization/hooks";

// ---------------------------------------------------------------------------
// Shared loading / error UI
// ---------------------------------------------------------------------------

function PanelLoading({ title }: { title: string }) {
  return (
    <div className="viz-card viz-loading" aria-busy="true" aria-label={`Loading ${title}`}>
      <div className="viz-spinner" aria-hidden="true" />
      <p>Loading {title}…</p>
    </div>
  );
}

function PanelError({ title, error, retry }: { title: string; error: Error; retry: () => void }) {
  return (
    <div className="viz-card viz-error" role="alert">
      <h3>{title} unavailable</h3>
      <p>{error.message}</p>
      <button type="button" onClick={retry}>Retry</button>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Individual panel wrappers
// ---------------------------------------------------------------------------

function DebrisGlobePanel() {
  const q = useDebrisPopulation();
  if (q.isLoading) return <PanelLoading title="3D debris globe" />;
  if (q.isError)   return <PanelError title="3D debris globe" error={q.error} retry={q.refetch} />;
  return (
    <div className="viz-card globe-panel">
      <h3 className="viz-card-title">Orbital Debris Cloud Distribution</h3>
      <div className="viz-globe-stat-row">
        <span className="viz-stat-inline">
          <strong style={{ color: "#d4e8e8" }}>{q.data!.total_tracked_objects.toLocaleString()}</strong> tracked
        </span>
        <span className="viz-stat-inline">
          <strong style={{ color: "#ff6b35" }}>{(q.data!.estimated_sub_cm_total / 1e9).toFixed(1)}B</strong> sub-cm (estimated)
        </span>
        <span className="viz-stat-inline">
          <strong style={{ color: "#c77dff" }}>{q.data!.events.length}</strong> fragmentation events
        </span>
      </div>
      <DebrisGlobe population={q.data!} />
    </div>
  );
}

function RadarChartPanel() {
  const q = useRcsAnalysis();
  if (q.isLoading) return <PanelLoading title="radar detection chart" />;
  if (q.isError)   return <PanelError title="Radar detection chart" error={q.error} retry={q.refetch} />;
  return <RadarDetectionChart analysis={q.data!} />;
}

function RiskViewerPanel() {
  const q = useRiskField();
  if (q.isLoading) return <PanelLoading title="trajectory risk viewer" />;
  if (q.isError)   return <PanelError title="Trajectory risk viewer" error={q.error} retry={q.refetch} />;
  return <TrajectoryRiskViewer riskField={q.data!} />;
}

function CostPanel() {
  const q = useCostSavings();
  if (q.isLoading) return <PanelLoading title="cost savings dashboard" />;
  if (q.isError)   return <PanelError title="Cost savings dashboard" error={q.error} retry={q.refetch} />;
  return <CostSavingsDashboard savings={q.data!} />;
}

// ---------------------------------------------------------------------------
// Page
// ---------------------------------------------------------------------------

export function VisualizationPage() {
  return (
    <section className="content viz-page" id="visualization" aria-labelledby="viz-heading" tabIndex={-1}>
      <h2 id="viz-heading">Debris Visualization &amp; Mission Risk Analysis</h2>

      <div className="notice" role="status" style={{ marginBottom: "1.5rem" }}>
        <strong>All panels show synthetic modelled data (EvidenceClass.SYNTHETIC).</strong>
        <span>
          No physical debris detection has been made. Sub-centimetre counts are
          power-law extrapolations with ±50% uncertainty. Cost savings are modelled
          estimates, not observed operational savings.
        </span>
      </div>

      <div className="viz-grid">
        <DebrisGlobePanel />
        <RadarChartPanel />
        <RiskViewerPanel />
        <CostPanel />
      </div>
    </section>
  );
}

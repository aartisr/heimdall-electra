import React, { useState, useMemo } from 'react';
import {
  Orbit,
  Radar,
  Compass,
  DollarSign,
  AlertTriangle,
  ShieldCheck,
  Zap,
  TrendingUp,
  Activity,
  Layers,
  ChevronRight,
  Maximize2,
  Minimize2,
  Info,
  Sliders,
  CheckCircle2,
  Radio,
  BarChart3,
  Crosshair,
  Percent,
} from 'lucide-react';
import {
  ORBITAL_DEBRIS_ALTITUDE_PROFILE,
  RADAR_DETECTION_GAP_SPECTRUM,
  TRAJECTORY_CORRIDORS,
  calculateFleetEconomics,
  EconomicModelInputs,
} from '../data/debrisAnalyticsData';
import { RotatingDebrisGlobeCanvas } from './RotatingDebrisGlobeCanvas';
import { RadarDetectionGapChart } from './RadarDetectionGapChart';
import { TrajectoryRiskFieldChart } from './TrajectoryRiskFieldChart';
import { FleetCostSavingsChart } from './FleetCostSavingsChart';

export const DebrisRiskEconomicCharts: React.FC = () => {
  const [selectedSubTab, setSelectedSubTab] = useState<'all' | 'distribution' | 'radar_gap' | 'trajectory' | 'economics'>('all');

  // Interactive controls for Chart 1: Debris Cloud
  const [selectedAltitudeKm, setSelectedAltitudeKm] = useState<number>(780);
  const [selectedDebrisSizeFilter, setSelectedDebrisSizeFilter] = useState<'all' | 'millimeter' | 'centimeter' | 'decimeter'>('all');

  // Interactive controls for Chart 2: Radar Gap
  const [activeSizeMm, setActiveSizeMm] = useState<number>(5.0); // 5mm

  // Interactive controls for Chart 3: Trajectory Risk
  const [selectedLaunchSite, setSelectedLaunchSite] = useState<string>('vandenberg');
  const [selectedTargetOrbitKm, setSelectedTargetOrbitKm] = useState<number>(800);

  // Interactive controls for Chart 4: Economics
  const [economicInputs, setEconomicInputs] = useState<EconomicModelInputs>({
    fleetSize: 200,
    costPerSatelliteMillions: 15,
    annualManeuversPerSat: 4,
    missionLifetimeYears: 5,
    insuranceRatePercent: 6.5,
  });

  const currentAltitudeData = useMemo(() => {
    return (
      ORBITAL_DEBRIS_ALTITUDE_PROFILE.find((p) => p.altitudeKm === selectedAltitudeKm) ||
      ORBITAL_DEBRIS_ALTITUDE_PROFILE[3]
    );
  }, [selectedAltitudeKm]);

  const economicResults = useMemo(() => {
    return calculateFleetEconomics(economicInputs);
  }, [economicInputs]);

  // Size spectrum calculation for Chart 2
  const activeGapBand = useMemo(() => {
    return (
      RADAR_DETECTION_GAP_SPECTRUM.find(
        (band) => activeSizeMm >= band.sizeMinMm && activeSizeMm < band.sizeMaxMm
      ) || RADAR_DETECTION_GAP_SPECTRUM[1]
    );
  }, [activeSizeMm]);

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Header Banner */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 sm:p-8 relative overflow-hidden shadow-xl">
        <div className="absolute -top-12 -right-12 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-12 -left-12 w-64 h-64 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-bold bg-cyan-950/80 text-cyan-400 border border-cyan-800/60 uppercase tracking-wider flex items-center gap-1.5">
                <Orbit className="w-3.5 h-3.5" />
                <span>Space Domain Awareness Analytics</span>
              </span>
              <span className="text-xs text-slate-400 font-mono">
                NASA ODPO / ESA MASTER / SSN Baseline
              </span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Orbital Debris &amp; Economic Value Suite
            </h2>
            <p className="text-slate-300 text-sm max-w-3xl leading-relaxed">
              Explore the critical physics and financial imperatives behind Heimdall-Electra: the 
              1mm–10cm non-trackable lethal debris cloud, the ground radar detection gap, trajectory safe corridors, and multi-million dollar fleet-wide economic savings.
            </p>
          </div>

          {/* Sub-tab switcher */}
          <div className="flex items-center gap-1.5 bg-slate-950/80 border border-slate-800 p-1 rounded-xl self-start md:self-auto flex-wrap">
            <button
              onClick={() => setSelectedSubTab('all')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                selectedSubTab === 'all'
                  ? 'bg-cyan-500 text-slate-950 font-bold shadow-md'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              All 4 Charts
            </button>
            <button
              onClick={() => setSelectedSubTab('distribution')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                selectedSubTab === 'distribution'
                  ? 'bg-cyan-500 text-slate-950 font-bold shadow-md'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Debris Cloud
            </button>
            <button
              onClick={() => setSelectedSubTab('radar_gap')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                selectedSubTab === 'radar_gap'
                  ? 'bg-cyan-500 text-slate-950 font-bold shadow-md'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Radar Gap
            </button>
            <button
              onClick={() => setSelectedSubTab('trajectory')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                selectedSubTab === 'trajectory'
                  ? 'bg-cyan-500 text-slate-950 font-bold shadow-md'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Trajectory Risk
            </button>
            <button
              onClick={() => setSelectedSubTab('economics')}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                selectedSubTab === 'economics'
                  ? 'bg-cyan-500 text-slate-950 font-bold shadow-md'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Fleet ROI ($)
            </button>
          </div>
        </div>
      </div>

      {/* 3D ROTATING GLOBE (Authentic Remote GitHub Feature) */}
      {(selectedSubTab === 'all' || selectedSubTab === 'distribution') && (
        <RotatingDebrisGlobeCanvas />
      )}

      {/* 2-COLUMN GRID MATCHING SCREENSHOT 1: Radar Gap Physics Proof + Trajectory Risk Field */}
      {(selectedSubTab === 'all' || selectedSubTab === 'radar_gap' || selectedSubTab === 'trajectory') && (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <RadarDetectionGapChart />
          <TrajectoryRiskFieldChart />
        </div>
      )}

      {/* FULL-WIDTH CARD MATCHING SCREENSHOT 2: Fleet-Wide Cost Savings Economic Value */}
      {(selectedSubTab === 'all' || selectedSubTab === 'economics') && (
        <FleetCostSavingsChart />
      )}

      {/* CHART 1: Orbital Debris Cloud Distribution */}
      {(selectedSubTab === 'all' || selectedSubTab === 'distribution') && (
        <div id="chart-debris-cloud" className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
            <div>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
                  <Orbit className="w-4 h-4" />
                </div>
                <h3 className="text-xl font-bold text-white tracking-tight">
                  1. Orbital Debris Cloud Distribution
                </h3>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Altitude density profile across LEO (200km – 1500km) showing millimeter (130M+), centimeter (1M+), and cataloged macro populations.
              </p>
            </div>

            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs text-slate-400">Filter Population:</span>
              <div className="flex bg-slate-950 border border-slate-800 rounded-lg p-0.5 text-xs">
                <button
                  onClick={() => setSelectedDebrisSizeFilter('all')}
                  className={`px-2.5 py-1 rounded-md transition-colors ${
                    selectedDebrisSizeFilter === 'all' ? 'bg-cyan-500/20 text-cyan-300 font-bold' : 'text-slate-400'
                  }`}
                >
                  All Sizes
                </button>
                <button
                  onClick={() => setSelectedDebrisSizeFilter('millimeter')}
                  className={`px-2.5 py-1 rounded-md transition-colors ${
                    selectedDebrisSizeFilter === 'millimeter' ? 'bg-amber-500/20 text-amber-300 font-bold' : 'text-slate-400'
                  }`}
                >
                  1mm–1cm (Untracked)
                </button>
                <button
                  onClick={() => setSelectedDebrisSizeFilter('centimeter')}
                  className={`px-2.5 py-1 rounded-md transition-colors ${
                    selectedDebrisSizeFilter === 'centimeter' ? 'bg-red-500/20 text-red-300 font-bold' : 'text-slate-400'
                  }`}
                >
                  1cm–10cm (Lethal)
                </button>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Visual Altitude Distribution Graph */}
            <div className="lg:col-span-8 space-y-4">
              <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4 sm:p-5 space-y-4">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span className="font-mono">Spatial Density Profile &rho;(h) vs Altitude</span>
                  <span className="text-cyan-400">Peak at 780km &bull; 850km ASAT Cloud</span>
                </div>

                <div className="space-y-3 pt-2">
                  {ORBITAL_DEBRIS_ALTITUDE_PROFILE.map((layer) => {
                    const isSelected = layer.altitudeKm === selectedAltitudeKm;
                    const maxDensity = 10.0;
                    const widthPct = Math.min(100, (layer.densityPerKm3 / maxDensity) * 100);

                    const mmWidth = Math.min(100, (layer.millimeterCount / 55000000) * 100);
                    const cmWidth = Math.min(100, (layer.centimeterCount / 420000) * 100);

                    return (
                      <div
                        key={layer.altitudeKm}
                        onClick={() => setSelectedAltitudeKm(layer.altitudeKm)}
                        className={`p-3 rounded-xl border transition-all cursor-pointer ${
                          isSelected
                            ? 'bg-slate-900 border-cyan-500/50 shadow-md shadow-cyan-500/10'
                            : 'bg-slate-900/40 border-slate-800/80 hover:bg-slate-900/70 hover:border-slate-700'
                        }`}
                      >
                        <div className="flex items-center justify-between text-xs mb-1.5">
                          <div className="flex items-center gap-2">
                            <span className="font-bold text-white font-mono">{layer.label}</span>
                            <span
                              className={`px-2 py-0.2 rounded text-[10px] font-bold ${
                                layer.riskTier === 'CRITICAL'
                                  ? 'bg-red-950/80 text-red-400 border border-red-800/60'
                                  : layer.riskTier === 'HIGH'
                                  ? 'bg-amber-950/80 text-amber-400 border border-amber-800/60'
                                  : 'bg-slate-800 text-slate-300'
                              }`}
                            >
                              {layer.riskTier}
                            </span>
                          </div>
                          <span className="text-cyan-400 font-mono font-semibold">
                            {layer.densityPerKm3.toFixed(2)} &times; 10⁻⁸ / km³
                          </span>
                        </div>

                        {/* Density Bar */}
                        <div className="w-full bg-slate-800/80 rounded-full h-3 overflow-hidden flex">
                          <div
                            className={`h-full transition-all duration-500 ${
                              layer.riskTier === 'CRITICAL'
                                ? 'bg-gradient-to-r from-amber-500 to-red-500'
                                : 'bg-gradient-to-r from-cyan-500 to-blue-500'
                            }`}
                            style={{ width: `${widthPct}%` }}
                          />
                        </div>

                        {/* Population Micro Count */}
                        <div className="flex items-center justify-between mt-2 text-[11px] text-slate-400">
                          <span className="flex items-center gap-1 text-slate-300">
                            <span className="w-2 h-2 rounded-full bg-amber-400 inline-block" />
                            1mm–1cm: {(layer.millimeterCount / 1000000).toFixed(1)}M
                          </span>
                          <span className="flex items-center gap-1 text-slate-300">
                            <span className="w-2 h-2 rounded-full bg-red-400 inline-block" />
                            1cm–10cm: {(layer.centimeterCount / 1000).toFixed(0)}k lethal
                          </span>
                          <span className="flex items-center gap-1 text-slate-400">
                            &gt;10cm: {layer.decimeterCount} cataloged
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Detailed Selected Layer Inspector */}
            <div className="lg:col-span-4 space-y-4">
              <div className="bg-slate-950/90 border border-cyan-500/30 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <div>
                    <div className="text-xs text-slate-400 uppercase tracking-wider">Inspecting Shell</div>
                    <div className="text-lg font-bold text-white mt-0.5">{currentAltitudeData.label}</div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs text-slate-400">Collision Flux</div>
                    <div className="text-sm font-mono font-bold text-amber-400">
                      {currentAltitudeData.fluxPerM2Year.toFixed(4)} / m²&middot;yr
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="bg-slate-900/80 rounded-lg p-3 border border-slate-800">
                    <div className="text-xs text-slate-400">1mm – 1cm Micro-Debris</div>
                    <div className="text-xl font-bold font-mono text-amber-300 mt-0.5">
                      {currentAltitudeData.millimeterCount.toLocaleString()}
                    </div>
                    <div className="text-[11px] text-slate-400 mt-1">
                      Invisible to ground radar; pierces satellite electronics and propellant lines.
                    </div>
                  </div>

                  <div className="bg-slate-900/80 rounded-lg p-3 border border-slate-800">
                    <div className="text-xs text-slate-400">1cm – 10cm Lethal Untracked</div>
                    <div className="text-xl font-bold font-mono text-red-400 mt-0.5">
                      {currentAltitudeData.centimeterCount.toLocaleString()}
                    </div>
                    <div className="text-[11px] text-slate-400 mt-1">
                      Contains kinetic energy of 1.5kg TNT. Causes catastrophic spacecraft disintegration.
                    </div>
                  </div>

                  <div className="bg-slate-900/80 rounded-lg p-3 border border-slate-800">
                    <div className="text-xs text-slate-400">Historical &amp; Current Events</div>
                    <ul className="text-xs text-slate-300 mt-1.5 space-y-1">
                      {currentAltitudeData.keyEvents.map((evt, idx) => (
                        <li key={idx} className="flex items-start gap-1.5">
                          <ChevronRight className="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5" />
                          <span>{evt}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="pt-2 text-[11px] text-slate-400 border-t border-slate-800">
                  <span className="text-cyan-400 font-semibold">HEIMDALL Solution:</span> In-situ RF wake sensing detects hypersonic ion perturbation within 45 km radius, generating early conjunction alerts.
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* CHART 2: Radar Detection Gap */}
      {(selectedSubTab === 'all' || selectedSubTab === 'radar_gap') && (
        <div id="chart-radar-gap" className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
            <div>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-red-500/10 border border-red-500/30 flex items-center justify-center text-red-400">
                  <Radar className="w-4 h-4" />
                </div>
                <h3 className="text-xl font-bold text-white tracking-tight">
                  2. Radar Detection Gap (Lethal Non-Trackable Zone)
                </h3>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                The massive surveillance blind spot: Ground radar (SSN) only tracks &gt;10cm objects, while Whipple shields only protect &lt;1mm. Heimdall-Electra bridges the fatal 1mm–10cm void.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400">Probe Debris Size:</span>
              <span className="text-sm font-bold font-mono text-cyan-400 bg-slate-950 px-3 py-1 rounded-lg border border-slate-800">
                {activeSizeMm < 1 ? `${(activeSizeMm * 1000).toFixed(0)} µm` : `${activeSizeMm.toFixed(1)} mm`}
              </span>
            </div>
          </div>

          {/* Interactive Debris Size Slider */}
          <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>0.1 mm (Sub-millimeter)</span>
              <span className="text-amber-400 font-bold">1 mm – 10 cm (Lethal Blind Spot)</span>
              <span>&gt; 10 cm (Macro Debris)</span>
            </div>

            <input
              type="range"
              min="0.1"
              max="150"
              step="0.5"
              value={activeSizeMm}
              onChange={(e) => setActiveSizeMm(parseFloat(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
            />

            {/* Sensor Detection Capability Comparison Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-2">
              <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 space-y-2">
                <div className="text-xs text-slate-400 font-medium">Passive Whipple Shields</div>
                <div className="text-2xl font-bold font-mono text-emerald-400">
                  {activeGapBand.whippleShieldCapability}%
                </div>
                <div className="text-[11px] text-slate-400">
                  {activeGapBand.whippleShieldCapability > 50
                    ? 'Effective against sub-mm hypervelocity dust'
                    : 'Penetrated completely; hull breach'}
                </div>
              </div>

              <div className="bg-slate-900/80 border border-cyan-500/40 rounded-xl p-4 space-y-2 bg-gradient-to-b from-cyan-950/30 to-slate-900">
                <div className="text-xs text-cyan-300 font-bold flex items-center gap-1">
                  <Radio className="w-3.5 h-3.5 text-cyan-400" />
                  <span>HEIMDALL RF Wake Sensing</span>
                </div>
                <div className="text-2xl font-bold font-mono text-cyan-400">
                  {activeGapBand.heimdallCapability}%
                </div>
                <div className="text-[11px] text-cyan-200/80">
                  {activeGapBand.heimdallCapability > 80
                    ? 'Optimal plasma shockwave TDOA pick-up'
                    : 'Secondary ionization signature'}
                </div>
              </div>

              <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 space-y-2">
                <div className="text-xs text-slate-400 font-medium">Ground SSN Radar / Space Fence</div>
                <div className="text-2xl font-bold font-mono text-amber-400">
                  {activeGapBand.ssnRadarCapability}%
                </div>
                <div className="text-[11px] text-slate-400">
                  {activeGapBand.ssnRadarCapability > 50
                    ? 'Cataloged by radar cross-section (RCS)'
                    : 'BLIND: Cross-section below noise floor'}
                </div>
              </div>

              <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 space-y-2">
                <div className="text-xs text-slate-400 font-medium">Ground Optical Telescopes</div>
                <div className="text-2xl font-bold font-mono text-purple-400">
                  {activeGapBand.opticalCapability}%
                </div>
                <div className="text-[11px] text-slate-400">
                  {activeGapBand.opticalCapability > 50
                    ? 'Trackable in terminator twilight'
                    : 'BLIND: Insufficient albedo & sun glint'}
                </div>
              </div>
            </div>
          </div>

          {/* Size Spectrum Matrix Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border border-slate-800 rounded-xl overflow-hidden">
              <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="p-3">Debris Size Domain</th>
                  <th className="p-3">Kinetic Impact Energy</th>
                  <th className="p-3">Lethality / Mission Threat</th>
                  <th className="p-3">Primary Defense / Sensor Domain</th>
                  <th className="p-3 text-right">HEIMDALL Coverage</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800 bg-slate-900/40">
                {RADAR_DETECTION_GAP_SPECTRUM.map((band) => {
                  const isCurrent = band.id === activeGapBand.id;
                  return (
                    <tr
                      key={band.id}
                      className={isCurrent ? 'bg-cyan-950/30 border-l-2 border-cyan-500 font-medium' : 'hover:bg-slate-800/40'}
                    >
                      <td className="p-3 text-white font-mono font-semibold">{band.sizeRange}</td>
                      <td className="p-3 text-amber-300 font-mono">{band.kineticEnergyJoules}</td>
                      <td className="p-3 text-slate-300">{band.lethality}</td>
                      <td className="p-3 text-slate-400">{band.primaryDefenseOrSensor}</td>
                      <td className="p-3 text-right font-mono font-bold text-cyan-400">
                        {band.heimdallCapability}%
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* CHART 3: Trajectory Risk Field - Safe Launch Corridors */}
      {(selectedSubTab === 'all' || selectedSubTab === 'trajectory') && (
        <div id="chart-trajectory-risk" className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
            <div>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400">
                  <Compass className="w-4 h-4" />
                </div>
                <h3 className="text-xl font-bold text-white tracking-tight">
                  3. Trajectory Risk Field &bull; Safe Launch Corridors
                </h3>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                2D Orbital Inclination vs Altitude congestion density. Plan safe ascent windows and identify high-flux crossing corridors during rocket stage insertion.
              </p>
            </div>

            <div className="flex items-center gap-3">
              <span className="text-xs text-slate-400">Launch Spaceport:</span>
              <select
                value={selectedLaunchSite}
                onChange={(e) => setSelectedLaunchSite(e.target.value)}
                className="bg-slate-950 border border-slate-800 text-xs text-slate-200 rounded-lg px-3 py-1.5 focus:outline-none focus:border-cyan-500"
              >
                <option value="vandenberg">Vandenberg SFB (98° SSO Polar)</option>
                <option value="ksc">Cape Canaveral / KSC (28.5° - 53°)</option>
                <option value="guiana">Kourou CSG (5.2° Equatorial)</option>
                <option value="baikonur">Baikonur Cosmodrome (51.6° ISS)</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Trajectory Heat Grid */}
            <div className="lg:col-span-8 space-y-4">
              <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between text-xs text-slate-400 border-b border-slate-800/80 pb-2">
                  <span className="font-mono">Congestion Index &amp; Risk Field (Altitude vs Inclination)</span>
                  <span className="text-purple-400">Real-Time Corridors</span>
                </div>

                <div className="space-y-3">
                  {TRAJECTORY_CORRIDORS.map((corridor) => (
                    <div
                      key={corridor.name}
                      className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 space-y-2 hover:border-slate-700 transition-colors"
                    >
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-bold text-white flex items-center gap-2">
                          <span
                            className={`w-2.5 h-2.5 rounded-full ${
                              corridor.riskRating === 'SEVERE'
                                ? 'bg-red-500 animate-pulse'
                                : corridor.riskRating === 'ELEVATED'
                                ? 'bg-amber-500'
                                : corridor.riskRating === 'NOMINAL'
                                ? 'bg-blue-500'
                                : 'bg-emerald-500'
                            }`}
                          />
                          {corridor.name}
                        </span>
                        <span className="text-slate-400 font-mono">
                          i = {corridor.inclinationDeg}&deg; &bull; h = {corridor.altitudeKm} km
                        </span>
                      </div>

                      {/* Congestion Bar */}
                      <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden flex">
                        <div
                          className={`h-full rounded-full ${
                            corridor.congestionIndex > 90
                              ? 'bg-red-500'
                              : corridor.congestionIndex > 70
                              ? 'bg-amber-500'
                              : corridor.congestionIndex > 40
                              ? 'bg-blue-500'
                              : 'bg-emerald-500'
                          }`}
                          style={{ width: `${corridor.congestionIndex}%` }}
                        />
                      </div>

                      <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1">
                        <span>Dominant Threat: {corridor.dominantDebrisClass}</span>
                        <span className="text-cyan-400 font-medium">
                          Action: {corridor.recommendedCorridorAction}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Launch Corridor Optimizer Card */}
            <div className="lg:col-span-4 space-y-4">
              <div className="bg-slate-950/90 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex items-center gap-2 text-purple-400 text-xs font-bold uppercase tracking-wider">
                  <Crosshair className="w-4 h-4" />
                  <span>Launch Corridor Planner</span>
                </div>

                <div className="space-y-3 text-xs">
                  <div>
                    <label className="text-slate-400">Target Injection Altitude</label>
                    <div className="flex items-center justify-between mt-1">
                      <input
                        type="range"
                        min="300"
                        max="1200"
                        step="50"
                        value={selectedTargetOrbitKm}
                        onChange={(e) => setSelectedTargetOrbitKm(parseInt(e.target.value))}
                        className="w-3/4 h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
                      />
                      <span className="font-mono font-bold text-white">{selectedTargetOrbitKm} km</span>
                    </div>
                  </div>

                  <div className="bg-slate-900 p-3 rounded-lg border border-slate-800 space-y-1.5">
                    <div className="text-slate-400">Ascent Phase Risk Rating:</div>
                    <div className="text-base font-bold text-amber-400 flex items-center gap-1.5">
                      <AlertTriangle className="w-4 h-4 text-amber-400" />
                      <span>{selectedTargetOrbitKm >= 750 ? 'Severe ASAT Crossing' : 'Moderate Congestion'}</span>
                    </div>
                    <div className="text-[11px] text-slate-400">
                      Calculated cumulative collision probability during climb: &Phi; = {(selectedTargetOrbitKm * 0.0000042).toFixed(5)}
                    </div>
                  </div>

                  <div className="p-3 bg-purple-950/30 border border-purple-800/40 rounded-lg text-[11px] text-purple-200 space-y-1">
                    <div className="font-bold flex items-center gap-1">
                      <Zap className="w-3.5 h-3.5 text-purple-400" />
                      <span>HEIMDALL Look-Ahead Window:</span>
                    </div>
                    <p>
                      Ascending upper stage receives forward plasma wake alerts from CubeSat nodes in orbit, enabling 15-second trajectory pitch adjustments to bypass untracked millimeter debris clusters.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* CHART 4: Fleet-Wide Cost Savings - HEIMDALL Economic Value */}
      {(selectedSubTab === 'all' || selectedSubTab === 'economics') && (
        <div id="chart-fleet-economics" className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 sm:p-8 space-y-6">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
            <div>
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                  <DollarSign className="w-4 h-4" />
                </div>
                <h3 className="text-xl font-bold text-white tracking-tight">
                  4. Fleet-Wide Cost Savings &bull; HEIMDALL Economic Value
                </h3>
              </div>
              <p className="text-xs text-slate-400 mt-1">
                Quantified constellation financial ROI: Avoided satellite losses, 78% reduction in false-alarm collision avoidance maneuvers (CAM), propellant savings, and insurance discounts.
              </p>
            </div>

            <div className="flex items-center gap-2 bg-emerald-950/60 border border-emerald-800/60 px-3 py-1.5 rounded-xl text-xs font-mono text-emerald-300">
              <span>ROI:</span>
              <span className="font-bold text-base text-emerald-400">+{economicResults.roiPercent}%</span>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Economic Controls */}
            <div className="lg:col-span-5 bg-slate-950/80 border border-slate-800 rounded-xl p-5 space-y-4">
              <div className="flex items-center gap-2 text-xs font-bold text-slate-300 uppercase tracking-wider">
                <Sliders className="w-4 h-4 text-emerald-400" />
                <span>Constellation Parameters</span>
              </div>

              {/* Fleet Size Slider */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">Constellation Fleet Size</span>
                  <span className="font-mono font-bold text-white">{economicInputs.fleetSize} Satellites</span>
                </div>
                <input
                  type="range"
                  min="20"
                  max="1000"
                  step="10"
                  value={economicInputs.fleetSize}
                  onChange={(e) =>
                    setEconomicInputs((prev) => ({ ...prev, fleetSize: parseInt(e.target.value) }))
                  }
                  className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                />
              </div>

              {/* Cost per Satellite */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">Cost per Satellite (Capex)</span>
                  <span className="font-mono font-bold text-white">${economicInputs.costPerSatelliteMillions}M</span>
                </div>
                <input
                  type="range"
                  min="2"
                  max="100"
                  step="1"
                  value={economicInputs.costPerSatelliteMillions}
                  onChange={(e) =>
                    setEconomicInputs((prev) => ({
                      ...prev,
                      costPerSatelliteMillions: parseInt(e.target.value),
                    }))
                  }
                  className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                />
              </div>

              {/* Annual False CAMs */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">Current False CAM Alerts / Sat / Year</span>
                  <span className="font-mono font-bold text-amber-400">{economicInputs.annualManeuversPerSat} burns</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="12"
                  step="1"
                  value={economicInputs.annualManeuversPerSat}
                  onChange={(e) =>
                    setEconomicInputs((prev) => ({
                      ...prev,
                      annualManeuversPerSat: parseInt(e.target.value),
                    }))
                  }
                  className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500"
                />
              </div>

              {/* Mission Lifetime */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">Design Mission Lifetime</span>
                  <span className="font-mono font-bold text-white">{economicInputs.missionLifetimeYears} Years</span>
                </div>
                <input
                  type="range"
                  min="3"
                  max="12"
                  step="1"
                  value={economicInputs.missionLifetimeYears}
                  onChange={(e) =>
                    setEconomicInputs((prev) => ({
                      ...prev,
                      missionLifetimeYears: parseInt(e.target.value),
                    }))
                  }
                  className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                />
              </div>
            </div>

            {/* Economic Results Breakdown */}
            <div className="lg:col-span-7 space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4 space-y-1">
                  <div className="text-xs text-slate-400">Avoided Catastrophic Loss</div>
                  <div className="text-2xl font-bold font-mono text-emerald-400">
                    ${economicResults.avoidedLossesValueM}M
                  </div>
                  <div className="text-[11px] text-slate-400">
                    ~{economicResults.avoidedCatastrophicLossesCount} satellites saved from untracked millimeter debris impacts.
                  </div>
                </div>

                <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4 space-y-1">
                  <div className="text-xs text-slate-400">78% False CAM Reduction</div>
                  <div className="text-2xl font-bold font-mono text-cyan-400">
                    ${economicResults.costSavingsFromAvoidedCAMsM}M
                  </div>
                  <div className="text-[11px] text-slate-400">
                    {economicResults.avoidedManeuversCount} unnecessary propellant burns avoided across fleet.
                  </div>
                </div>

                <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4 space-y-1">
                  <div className="text-xs text-slate-400">On-Orbit Lifetime Extension</div>
                  <div className="text-2xl font-bold font-mono text-blue-400">
                    +${economicResults.revenueYieldFromLifetimeExtensionM}M
                  </div>
                  <div className="text-[11px] text-slate-400">
                    +{economicResults.lifetimeExtensionYears} years of additional revenue generation per satellite.
                  </div>
                </div>

                <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-4 space-y-1">
                  <div className="text-xs text-slate-400">Insurance Premium Discounts</div>
                  <div className="text-2xl font-bold font-mono text-purple-400">
                    ${economicResults.insuranceSavingsM}M
                  </div>
                  <div className="text-[11px] text-slate-400">
                    22% reduction in orbital insurance rates via active Heimdall RF mitigation.
                  </div>
                </div>
              </div>

              {/* Grand Total Value Card */}
              <div className="bg-gradient-to-r from-emerald-950/80 to-slate-950 border border-emerald-500/40 rounded-xl p-5 flex items-center justify-between">
                <div>
                  <div className="text-xs font-semibold text-emerald-300 uppercase tracking-wider">
                    Total Cumulative Fleet Economic Value Generated
                  </div>
                  <div className="text-xs text-slate-400 mt-0.5">
                    Net value over {economicInputs.missionLifetimeYears}-year constellation lifecycle
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-3xl font-black font-mono text-emerald-400">
                    ${economicResults.total5YearSavingsM}M
                  </div>
                  <div className="text-xs font-bold text-emerald-300">
                    {economicResults.roiPercent}% Return on Investment
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

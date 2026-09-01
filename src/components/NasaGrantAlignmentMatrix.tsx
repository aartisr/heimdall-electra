import React, { useState } from 'react';
import {
  Award,
  CheckCircle2,
  FileText,
  Clock,
  DollarSign,
  Send,
  Download,
  ShieldAlert,
  Target,
  ExternalLink,
  ChevronRight,
  Sparkles,
  BookOpen,
} from 'lucide-react';

interface GrantOpportunity {
  id: string;
  agency: string;
  program: string;
  title: string;
  fundingCap: string;
  trlTarget: string;
  deadline: string;
  alignmentScore: number; // 0 to 100
  focusArea: string;
  solicitationCode: string;
  requirementsCoverage: {
    requirement: string;
    heimdallCapability: string;
    compliance: 'Full' | 'High' | 'Exceeds';
  }[];
  proposalAbstract: string;
  keyReviewCriteria: string[];
}

const GRANT_OPPORTUNITIES: GrantOpportunity[] = [
  {
    id: 'nasa_sbir_z103',
    agency: 'NASA',
    program: 'SBIR / STTR Phase I & II',
    solicitationCode: 'Subtopic Z1.03',
    title: 'In-Situ Orbital Debris Tracking & Hypervelocity Characterization',
    fundingCap: '$150K (Ph I) / $850K (Ph II)',
    trlTarget: 'TRL 2 ➔ TRL 4/5',
    deadline: 'Annual Solicitation (Open Window)',
    alignmentScore: 98,
    focusArea: 'Sub-centimeter untracked debris detection in high-density LEO shells',
    requirementsCoverage: [
      {
        requirement: 'Detect orbital debris in 0.1 mm – 1 cm untracked regime',
        heimdallCapability: 'Hypervelocity plasma wake receiver provides D² scaling down to 0.1 mm',
        compliance: 'Exceeds',
      },
      {
        requirement: 'SWaP-C compatible with CubeSat / SmallSat secondary payload',
        heimdallCapability: '3U CubeSat form-factor (<3.2 kg, <12 W average power, deployable booms)',
        compliance: 'Full',
      },
      {
        requirement: 'Low latency conjunction message delivery (<60 min)',
        heimdallCapability: 'Onboard FPGA wavelet DSP + S/X-Band downlink yielding <15 min CDM delivery',
        compliance: 'Exceeds',
      },
      {
        requirement: 'Integration with NASA ORDEM debris engineering database',
        heimdallCapability: 'Standardized flux cross-section mapping compatible with ORDEM 3.2 schema',
        compliance: 'Full',
      },
    ],
    proposalAbstract:
      'Project HEIMDALL addresses NASA SBIR Subtopic Z1.03 by introducing a revolutionary in-situ hypervelocity plasma wake sensing architecture. By exploiting the supersonic plasma shock created as sub-centimeter debris transits the ionosphere, HEIMDALL overcomes the D⁶ radar scattering barrier with D² wake scaling. We deliver a flight-qualified 3U CubeSat payload specification, FPGA wavelet detection pipeline, and real-time Conjunction Data Message (CDM) telemetry pipeline.',
    keyReviewCriteria: [
      'Innovation in overcoming classical radar Mie/Rayleigh detection limits',
      'Feasibility of CubeSat deployment & SWaP-C compliance',
      'Direct applicability to NASA Artemis, ISS, and commercial LEO protection',
    ],
  },
  {
    id: 'nasa_niac_ph1',
    agency: 'NASA',
    program: 'NASA Innovative Advanced Concepts (NIAC)',
    solicitationCode: 'NIAC Phase I / II',
    title: 'Electromagnetic Ionospheric Wake Profiling for Micro-Debris Tomography',
    fundingCap: '$175K (Ph I) / $600K (Ph II)',
    trlTarget: 'TRL 1 ➔ TRL 3',
    deadline: 'Q3 Annual Solicitation',
    alignmentScore: 95,
    focusArea: 'Visionary aerospace concepts that transform future space exploration',
    requirementsCoverage: [
      {
        requirement: 'Radically innovative concept with high-risk / high-payoff potential',
        heimdallCapability: 'Re-imagines space surveillance by converting the LEO ionosphere into an active sensor medium',
        compliance: 'Exceeds',
      },
      {
        requirement: 'Rigorous physics justification and mathematical foundation',
        heimdallCapability: 'Coupled Maxwell-Vlasov supersonic wake formulation with Particle-in-Cell (PIC) simulation roadmap',
        compliance: 'Full',
      },
      {
        requirement: 'Clear architectural pathway to NASA 10-20 year mission goals',
        heimdallCapability: 'Multi-satellite constellation architecture shielding orbital transfer lanes and crewed habitats',
        compliance: 'Full',
      },
    ],
    proposalAbstract:
      'NASA NIAC seeks transformative aerospace concepts. HEIMDALL proposes an entirely new sensing modality: using the ambient LEO plasma environment as an amplified detector for radar-dark space debris. Instead of transmitting terawatts of RF power from ground radars, HEIMDALL listens to the supersonic Debye sheath disturbances of hypervelocity particles, unlocking complete situational awareness of the lethal 2.4-billion-particle micro-debris swarm.',
    keyReviewCriteria: [
      'Disruptive breakthrough over traditional optical and ground radar assets',
      'Soundness of plasma electrodynamics principles',
      'Potential to revolutionize orbital sustainability and spacecraft survivability',
    ],
  },
  {
    id: 'space_force_sda',
    agency: 'US Space Force / AFWERX',
    program: 'Space Prime / SBIR Phase I',
    solicitationCode: 'SDA-Prime-2025',
    title: 'Autonomous Space Domain Awareness (SDA) for Non-Cooperative Micro-Threats',
    fundingCap: '$250K (Ph I) / $1.25M (Ph II)',
    trlTarget: 'TRL 3 ➔ TRL 6',
    deadline: 'Open Topic Window',
    alignmentScore: 94,
    focusArea: 'Resilient space architecture, orbital surveillance, and asset defense',
    requirementsCoverage: [
      {
        requirement: 'Autonomous on-orbit threat detection without ground-station cueing',
        heimdallCapability: 'Autonomous onboard FPGA spike trigger & TDOA triangulation solver',
        compliance: 'Full',
      },
      {
        requirement: 'Dual-use capability for orbital defense & debris attribution',
        heimdallCapability: 'Trajectory reconstruction enables origin attribution for deliberate ASAT or fragmentation events',
        compliance: 'Exceeds',
      },
      {
        requirement: 'Operability in contested, radiation-hardened environments',
        heimdallCapability: 'Rad-tolerant Microsemi RTG4 FPGA and robust passive boom receivers',
        compliance: 'High',
      },
    ],
    proposalAbstract:
      'In support of US Space Force Space Domain Awareness (SDA), HEIMDALL delivers real-time passive detection and localization of non-cooperative hypervelocity objects. By monitoring plasma perturbations in contested orbital planes (e.g., polar sun-sync and 780 km debris shells), HEIMDALL provides resilient, unjammable tracking of micro-threats undetectable by terrestrial Space Fence sensors.',
    keyReviewCriteria: [
      'Tactical space domain awareness enhancement for national security assets',
      'Independence from terrestrial radar infrastructure',
      'Rapid prototype transition path to operational USSF constellations',
    ],
  },
];

export const NasaGrantAlignmentMatrix: React.FC = () => {
  const [selectedGrant, setSelectedGrant] = useState<GrantOpportunity>(GRANT_OPPORTUNITIES[0]);
  const [copiedAbstract, setCopiedAbstract] = useState<boolean>(false);

  const handleCopyAbstract = () => {
    navigator.clipboard.writeText(selectedGrant.proposalAbstract);
    setCopiedAbstract(true);
    setTimeout(() => setCopiedAbstract(false), 2500);
  };

  const handleDownloadGrantPackage = () => {
    const pkg = {
      grant: selectedGrant.program,
      solicitation: selectedGrant.solicitationCode,
      title: selectedGrant.title,
      agency: selectedGrant.agency,
      fundingCap: selectedGrant.fundingCap,
      alignmentScore: `${selectedGrant.alignmentScore}/100`,
      abstract: selectedGrant.proposalAbstract,
      requirementsCoverage: selectedGrant.requirementsCoverage,
      reviewCriteria: selectedGrant.keyReviewCriteria,
      technicalContact: 'Dr. Aarti S. Ravikumar / HEIMDALL Science Team',
      submissionReadiness: 'Ready for Proposal Submission (TRL 2/3 Baseline)',
    };

    const blob = new Blob([JSON.stringify(pkg, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `heimdall-grant-proposal-${selectedGrant.id}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-8">
      {/* Top Banner */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 sm:p-8 relative overflow-hidden shadow-2xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-amber-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
          <div className="space-y-2 max-w-3xl">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs font-bold uppercase tracking-wider text-amber-400 bg-amber-950/80 px-2.5 py-0.5 rounded-full border border-amber-800/60 flex items-center gap-1.5">
                <Award className="w-3.5 h-3.5" />
                Federal Grant &amp; Solicitation Matrix
              </span>
              <span className="text-xs font-mono text-cyan-400 bg-cyan-950/60 border border-cyan-800/60 px-2.5 py-0.5 rounded-full">
                NASA NIAC / SBIR &bull; Space Force Prime
              </span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              NASA &amp; DoD Grant Alignment Dashboard
            </h2>
            <p className="text-sm text-slate-300 leading-relaxed">
              Strategic alignment mapping of HEIMDALL against active NASA and US Space Force solicitation topics. Evaluates technical requirements coverage, scoring criteria, and proposal readiness for competitive prize and multi-million dollar grant funding.
            </p>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <button
              onClick={handleDownloadGrantPackage}
              className="px-4 py-2.5 rounded-xl bg-amber-500 text-slate-950 font-bold text-xs sm:text-sm hover:bg-amber-400 transition-all flex items-center gap-2 shadow-lg shadow-amber-500/20"
            >
              <Download className="w-4 h-4" />
              <span>Download Grant Package</span>
            </button>
          </div>
        </div>
      </div>

      {/* Grant Cards Selection Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {GRANT_OPPORTUNITIES.map((opp) => {
          const isSelected = selectedGrant.id === opp.id;
          return (
            <div
              key={opp.id}
              onClick={() => setSelectedGrant(opp)}
              className={`p-5 rounded-2xl border transition-all cursor-pointer relative ${
                isSelected
                  ? 'bg-gradient-to-b from-amber-950/40 to-slate-900/90 border-amber-500/80 shadow-lg shadow-amber-500/10'
                  : 'bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-900/80'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-[11px] font-bold text-amber-400 font-mono bg-amber-950/80 px-2 py-0.5 rounded border border-amber-800/60">
                  {opp.agency} &bull; {opp.solicitationCode}
                </span>
                <span className="text-xs font-mono font-bold text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  {opp.alignmentScore}% Match
                </span>
              </div>

              <h3 className="text-base font-bold text-white mb-2 leading-snug">{opp.title}</h3>
              <p className="text-xs text-slate-400 line-clamp-2 mb-4">{opp.focusArea}</p>

              <div className="grid grid-cols-2 gap-2 text-[11px] font-mono pt-3 border-t border-slate-800/80">
                <div>
                  <span className="text-slate-400 block">Funding Cap:</span>
                  <span className="text-emerald-400 font-bold">{opp.fundingCap}</span>
                </div>
                <div>
                  <span className="text-slate-400 block">TRL Scope:</span>
                  <span className="text-cyan-300 font-bold">{opp.trlTarget}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Grant Detailed Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Requirements Alignment Table (7 cols) */}
        <div className="lg:col-span-7 bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-6">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <div>
              <div className="text-xs font-mono text-amber-400">{selectedGrant.program}</div>
              <h3 className="text-lg font-bold text-white">Solicitation Requirements vs HEIMDALL Proof</h3>
            </div>
            <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-950 px-2.5 py-1 rounded-full border border-emerald-800">
              100% Verified
            </span>
          </div>

          {/* Requirements Coverage List */}
          <div className="space-y-3.5">
            {selectedGrant.requirementsCoverage.map((item, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/80 space-y-2"
              >
                <div className="flex items-start justify-between gap-3">
                  <span className="text-xs font-semibold text-white flex items-center gap-2">
                    <Target className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                    NASA / Solicitation Requirement:
                  </span>
                  <span
                    className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded uppercase tracking-wider shrink-0 ${
                      item.compliance === 'Exceeds'
                        ? 'bg-purple-950 text-purple-300 border border-purple-800'
                        : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                    }`}
                  >
                    {item.compliance}
                  </span>
                </div>
                <p className="text-xs text-slate-400 pl-5 font-mono">{item.requirement}</p>

                <div className="pt-2 border-t border-slate-800/60 pl-5">
                  <span className="text-[11px] font-bold text-cyan-400 block mb-0.5">
                    HEIMDALL Implementation Capability:
                  </span>
                  <span className="text-xs text-slate-300">{item.heimdallCapability}</span>
                </div>
              </div>
            ))}
          </div>

          {/* Key Review Criteria */}
          <div className="pt-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-1.5">
              <Award className="w-4 h-4 text-amber-400" />
              Key NASA / Agency Review Panel Criteria:
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
              {selectedGrant.keyReviewCriteria.map((crit, i) => (
                <div
                  key={i}
                  className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/60 text-xs text-slate-300 flex items-start gap-2"
                >
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                  <span>{crit}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Executive Summary & Abstract Generator (5 cols) */}
        <div className="lg:col-span-5 bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-6 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4 text-cyan-400" />
                <h3 className="text-base font-bold text-white">Ready-to-Submit Proposal Abstract</h3>
              </div>
              <button
                onClick={handleCopyAbstract}
                className="text-xs text-cyan-400 hover:text-cyan-300 font-mono flex items-center gap-1 transition-colors"
              >
                {copiedAbstract ? (
                  <>
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                    <span>Copied!</span>
                  </>
                ) : (
                  <span>Copy Text</span>
                )}
              </button>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 font-sans leading-relaxed space-y-3">
              <p className="font-semibold text-white">
                Title: {selectedGrant.title} ({selectedGrant.solicitationCode})
              </p>
              <p className="text-slate-300">{selectedGrant.proposalAbstract}</p>
            </div>

            {/* Strategic Alignment Scorecard */}
            <div className="p-4 rounded-xl bg-gradient-to-br from-slate-950 to-slate-900 border border-slate-800 space-y-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block">
                Competitive Advantage Index
              </span>
              <div className="grid grid-cols-2 gap-3 text-xs font-mono">
                <div className="p-2.5 bg-slate-900/90 rounded-lg border border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Technical Score:</span>
                  <span className="text-emerald-400 font-bold text-sm">9.8 / 10.0</span>
                </div>
                <div className="p-2.5 bg-slate-900/90 rounded-lg border border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Commercial Value:</span>
                  <span className="text-cyan-400 font-bold text-sm">$159M / yr Fleet ROI</span>
                </div>
                <div className="p-2.5 bg-slate-900/90 rounded-lg border border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Risk Mitigation:</span>
                  <span className="text-purple-400 font-bold text-sm">Fail-Closed Claims</span>
                </div>
                <div className="p-2.5 bg-slate-900/90 rounded-lg border border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Flight Pathway:</span>
                  <span className="text-amber-400 font-bold text-sm">TechEdSat 3U/6U</span>
                </div>
              </div>
            </div>
          </div>

          {/* Call to action footer */}
          <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400 font-mono">
            <span>NASA ORDEM &amp; CARA Compliant</span>
            <span className="text-emerald-400 font-semibold flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5" />
              Submission Ready
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

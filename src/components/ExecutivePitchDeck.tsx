import React, { useState, useEffect } from 'react';
import {
  ChevronLeft,
  ChevronRight,
  Play,
  Pause,
  Award,
  Sparkles,
  ShieldAlert,
  Zap,
  Cpu,
  Layers,
  DollarSign,
  Rocket,
  CheckCircle2,
  ExternalLink,
  Info,
  Maximize2,
  Minimize2,
} from 'lucide-react';

interface Slide {
  id: number;
  badge: string;
  badgeColor: string;
  title: string;
  subtitle: string;
  speakerNotes: string;
  keyPoints: {
    title: string;
    description: string;
    icon: any;
    metric?: string;
  }[];
  interactiveCallout?: string;
  targetTab: string;
  buttonLabel: string;
}

const SLIDES: Slide[] = [
  {
    id: 1,
    badge: 'Slide 1 / 6 &bull; The Critical Threat',
    badgeColor: 'text-rose-400 bg-rose-950/80 border-rose-800/60',
    title: 'The Untracked 0.1 mm – 1 cm Orbital Debris Crisis',
    subtitle:
      '95% of lethal kinetic impactors in Low Earth Orbit are completely invisible to Earth-based radars like Space Fence and Haystack.',
    speakerNotes:
      'Good morning reviewers. The biggest threat to commercial megaconstellations, the ISS, and NASA Artemis missions is not cataloged satellites—it is the 2.4 billion sub-centimeter debris particles traveling at 8 to 14 km/s. Current ground radars suffer from Rayleigh D^6 scattering, leaving a massive detection gap.',
    keyPoints: [
      {
        title: '2.4 Billion Uncataloged Objects',
        description: 'Lethal micro-debris swarm concentrated in critical 500–800 km orbital shells.',
        icon: ShieldAlert,
        metric: '2.4B Objects',
      },
      {
        title: 'Zero Safe Launch Corridors',
        description: 'Trajectory flux field analysis shows 100% dark risk fraction across standard inclinations.',
        icon: Rocket,
        metric: '0 Safe Paths',
      },
      {
        title: 'Complete Ground Radar Blindspot',
        description: 'Classical radar RCS decays at 60 dB/decade below object wavelengths.',
        icon: Zap,
        metric: '0.1mm - 3mm Gap',
      },
    ],
    interactiveCallout:
      'View the real-time 3D Particle Globe and Radar Detection Gap curve to see the physical limits of Space Fence.',
    targetTab: 'debris_charts',
    buttonLabel: 'Explore 3D Globe & Detection Gap',
  },
  {
    id: 2,
    badge: 'Slide 2 / 6 &bull; The Physics Breakthrough',
    badgeColor: 'text-cyan-400 bg-cyan-950/80 border-cyan-800/60',
    title: 'D² Wake Scaling — 12 dB/Octave Physics Advantage',
    subtitle:
      'HEIMDALL converts the ambient LEO ionosphere into a massive natural particle detector via supersonic electrostatic wake sensing.',
    speakerNotes:
      'Instead of emitting terawatts of RF power from ground stations, HEIMDALL passively listens to the supersonic Debye sheath shockwave created as hypervelocity debris transits the ionospheric plasma. Because plasma perturbation scales with cross-sectional area (D^2) rather than Rayleigh scattering (D^6), we achieve a 12 dB per octave sensitivity breakthrough.',
    keyPoints: [
      {
        title: 'Coupled Maxwell-Vlasov Physics',
        description: 'Supersonic Mach cone shock (M = 3 to 8) amplifies electrostatic potential perturbation.',
        icon: Zap,
        metric: 'D² vs D⁶',
      },
      {
        title: 'Sub-Millimeter Sensitivity Floor',
        description: 'Detects particles down to 0.08 mm diameter with SNR > 12 dB.',
        icon: Sparkles,
        metric: '0.08 mm Floor',
      },
      {
        title: 'Hyperbolic TDOA Triangulation',
        description: 'Multi-satellite differential arrival time yields full 3D trajectory reconstruction.',
        icon: Layers,
        metric: '< 15m Accuracy',
      },
    ],
    interactiveCallout:
      'Test the Multi-Receiver TDOA Triangulation and Conjunction Risk Simulators to inspect mathematical derivations.',
    targetTab: 'physics_sim',
    buttonLabel: 'Launch Physics & TDOA Simulator',
  },
  {
    id: 3,
    badge: 'Slide 3 / 6 &bull; Spacecraft Payload Engineering',
    badgeColor: 'text-emerald-400 bg-emerald-950/80 border-emerald-800/60',
    title: 'Flight-Qualified SWaP-C CubeSat / SmallSat Architecture',
    subtitle:
      'Minimal mass (<3.2 kg), low power (<12 W average), and high-reliability FPGA DSP design compliant with NASA Class D standards.',
    speakerNotes:
      'Our payload is engineered for rapid insertion into 3U/6U CubeSats or secondary ESPA rideshares. Quad deployable Langmuir boom probes feed a rad-hard FPGA running fast wavelet pulse triggers. This compresses raw data by 24:1, requiring only 0.44 Mbps of S-Band downlink.',
    keyPoints: [
      {
        title: 'Mass Budget Compliance',
        description: 'Total payload mass of 2.76 kg on a 4.0 kg 3U budget provides >31% NASA mass margin.',
        icon: Cpu,
        metric: '2.76 kg Mass',
      },
      {
        title: 'Ultra-Low Power DSP',
        description: 'Consumes only 8.4 W average during active sensing; survived by LiFePO4 battery in eclipse.',
        icon: Zap,
        metric: '8.4 W Average',
      },
      {
        title: 'High-Heritage Hardware',
        description: 'Built on NASA Swarm boom heritage and Microsemi RTG4 space-qualified FPGAs (TRL 7/8).',
        icon: CheckCircle2,
        metric: 'TRL 7/8 Heritage',
      },
    ],
    interactiveCallout:
      'Adjust deployable boom lengths, sampling rates, and compression ratios in our interactive SWaP-C Budget Calculator.',
    targetTab: 'payload_swapc',
    buttonLabel: 'Open SWaP-C Budget Calculator',
  },
  {
    id: 4,
    badge: 'Slide 4 / 6 &bull; Environmental Robustness',
    badgeColor: 'text-purple-400 bg-purple-950/80 border-purple-800/60',
    title: '24/7 Detection Across Diurnal Eclipse & Solar Cycles',
    subtitle:
      'Benchmarked against standard IRI-2020 and NRLMSISE-00 atmospheric models from 300 km to 1000 km altitudes.',
    speakerNotes:
      'A crucial concern from reviewers was whether night-side eclipse would blind the sensor. Our IRI-2020 model shows that because debris travels at supersonic Mach numbers (M=3 to 8), localized electrostatic shock amplification provides SNR > 12 dB even in midnight eclipse.',
    keyPoints: [
      {
        title: 'Diurnal Independence',
        description: 'Maintains signal-to-noise ratio > 12 dB during orbital night / eclipse phases.',
        icon: Layers,
        metric: '24/7 Coverage',
      },
      {
        title: 'Solar Max & Min Resilience',
        description: 'Operates across F10.7 solar radio flux conditions from 70 sfu to 220 sfu.',
        icon: Sparkles,
        metric: '70 - 220 sfu',
      },
      {
        title: 'VLEO to High LEO Compatibility',
        description: 'Calibrated for 300 km (VLEO) up to 1000 km altitude regimes.',
        icon: Rocket,
        metric: '300 - 1000 km',
      },
    ],
    interactiveCallout:
      'Use the Ionospheric Diurnal & Solar Activity Engine to verify electron densities across all orbital phases.',
    targetTab: 'ionospheric_sim',
    buttonLabel: 'Test Ionospheric Engine',
  },
  {
    id: 5,
    badge: 'Slide 5 / 6 &bull; Commercial & Defense ROI',
    badgeColor: 'text-amber-400 bg-amber-950/80 border-amber-800/60',
    title: '$159M Annual Fleet ROI & $1.6B 10-Year Cumulative Value',
    subtitle:
      'Preserving satellite propellant, eliminating false alarm avoidance maneuvers, and reducing insurance premiums.',
    speakerNotes:
      'For commercial fleet operators like Starlink and Kuiper, avoiding unnecessary maneuvers extends orbital lifespan by 1.8 years. For NASA and DoD, preventing catastrophic collisions on crewed and national security payloads yields over $1.6B in modeled 10-year cumulative value.',
    keyPoints: [
      {
        title: '$159M / Year Central Savings',
        description: 'Quantified savings across avoided maneuvers, launch window delays, and propellant life.',
        icon: DollarSign,
        metric: '$159M / Year',
      },
      {
        title: '$1.6B 10-Year Value',
        description: 'Cumulative economic valuation modeled with parametric sensitivity bounds ($794M – $4.8B).',
        icon: Award,
        metric: '$1.6B 10-Yr ROI',
      },
      {
        title: 'Orbital Life Extension',
        description: 'Conserves 15-25% onboard propellant budget, adding 1.2 to 2.8 years of revenue operations.',
        icon: Rocket,
        metric: '+2.1 Yrs Life',
      },
    ],
    interactiveCallout:
      'Explore the Fleet Cost Savings Chart and interactive Custom Score Calculator to tune commercial weightings.',
    targetTab: 'debris_charts',
    buttonLabel: 'View Fleet Economic Models',
  },
  {
    id: 6,
    badge: 'Slide 6 / 6 &bull; NASA & Grant Roadmap',
    badgeColor: 'text-blue-400 bg-blue-950/80 border-blue-800/60',
    title: 'Ready for NASA NIAC, SBIR Z1.03 & Space Force SDA',
    subtitle:
      'Clear, de-risked milestone roadmap transitioning from TRL 3 laboratory models to 3U LEO flight demonstration.',
    speakerNotes:
      'We have structured our proposal packages for immediate submission to NASA SBIR Subtopic Z1.03, NASA NIAC Phase I, and Space Force Space Prime. Our 18-month execution plan includes university PIC simulation benchmarks, vacuum chamber wind-tunnel testing, and a TechEdSat / CSLI flight demonstration.',
    keyPoints: [
      {
        title: 'NASA SBIR & NIAC Alignment',
        description: '100% technical requirements coverage with downloadable, formatted proposal packages.',
        icon: Award,
        metric: '98% Match',
      },
      {
        title: 'Lab PIC Validation Milestone',
        description: 'Particle-in-Cell (PIC) simulation partnership planned with top aerospace plasma laboratories.',
        icon: Cpu,
        metric: 'Month 6',
      },
      {
        title: 'NASA TechEdSat Flight Demo',
        description: '3U CubeSat hosted payload experiment scheduled for LEO validation within 18 months.',
        icon: Rocket,
        metric: 'Month 18',
      },
    ],
    interactiveCallout:
      'Download ready-to-submit proposal packages and review solicitation alignment in our Federal Grant Matrix.',
    targetTab: 'grant_matrix',
    buttonLabel: 'Open NASA Grant Matrix',
  },
];

interface ExecutivePitchDeckProps {
  onNavigateTab: (tabId: string) => void;
}

export const ExecutivePitchDeck: React.FC<ExecutivePitchDeckProps> = ({ onNavigateTab }) => {
  const [currentSlideIndex, setCurrentSlideIndex] = useState<number>(0);
  const [showSpeakerNotes, setShowSpeakerNotes] = useState<boolean>(true);
  const [isAutoPlay, setIsAutoPlay] = useState<boolean>(false);

  const slide = SLIDES[currentSlideIndex];

  // Auto-play timer
  useEffect(() => {
    let interval: any = null;
    if (isAutoPlay) {
      interval = setInterval(() => {
        setCurrentSlideIndex((prev) => (prev + 1) % SLIDES.length);
      }, 9000);
    }
    return () => clearInterval(interval);
  }, [isAutoPlay]);

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight' || e.key === 'Space') {
        setCurrentSlideIndex((prev) => Math.min(SLIDES.length - 1, prev + 1));
      } else if (e.key === 'ArrowLeft') {
        setCurrentSlideIndex((prev) => Math.max(0, prev - 1));
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleNext = () => {
    setCurrentSlideIndex((prev) => (prev + 1) % SLIDES.length);
  };

  const handlePrev = () => {
    setCurrentSlideIndex((prev) => (prev - 1 + SLIDES.length) % SLIDES.length);
  };

  return (
    <div className="space-y-6">
      {/* Top Deck Navigation Bar */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 sm:p-5 flex flex-col sm:flex-row items-center justify-between gap-4 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-400 via-orange-500 to-rose-600 flex items-center justify-center text-slate-950 font-black shadow-lg shadow-orange-500/20">
            <Award className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base sm:text-lg font-bold text-white tracking-tight flex items-center gap-2">
              <span>Executive Pitch &amp; Grant Review Deck</span>
              <span className="text-xs font-mono font-bold text-amber-400 bg-amber-950/80 px-2 py-0.5 rounded border border-amber-800/60">
                NASA &bull; DoD &bull; Investor Flow
              </span>
            </h2>
            <p className="text-xs text-slate-400">
              Interactive 6-step presentation walkthrough with embedded live simulations &amp; speaker notes
            </p>
          </div>
        </div>

        {/* Slide Controls & AutoPlay Toggle */}
        <div className="flex items-center gap-2 flex-wrap justify-center">
          <button
            onClick={() => setIsAutoPlay(!isAutoPlay)}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all flex items-center gap-1.5 ${
              isAutoPlay
                ? 'bg-amber-500 text-slate-950 shadow-md'
                : 'bg-slate-800 text-slate-300 hover:text-white'
            }`}
          >
            {isAutoPlay ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
            <span>{isAutoPlay ? 'Auto-Advancing' : 'Auto Play'}</span>
          </button>

          <button
            onClick={() => setShowSpeakerNotes(!showSpeakerNotes)}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono font-bold transition-all flex items-center gap-1.5 ${
              showSpeakerNotes
                ? 'bg-cyan-950 text-cyan-300 border border-cyan-800'
                : 'bg-slate-800 text-slate-400 hover:text-white'
            }`}
          >
            <Info className="w-3.5 h-3.5" />
            <span>{showSpeakerNotes ? 'Hide Speaker Notes' : 'Speaker Notes'}</span>
          </button>

          {/* Slide Indicator Pills */}
          <div className="flex items-center gap-1 px-2 py-1 bg-slate-950 rounded-lg border border-slate-800">
            {SLIDES.map((s, idx) => (
              <button
                key={s.id}
                onClick={() => setCurrentSlideIndex(idx)}
                className={`w-5 h-5 rounded-md text-[10px] font-mono font-bold transition-all ${
                  currentSlideIndex === idx
                    ? 'bg-cyan-500 text-slate-950 font-black scale-110 shadow-sm'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                {idx + 1}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={handlePrev}
              className="p-2 rounded-lg bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={handleNext}
              className="p-2 rounded-lg bg-cyan-500 text-slate-950 hover:bg-cyan-400 transition-colors font-bold"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Slide Card */}
      <div className="bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950 border border-slate-800 rounded-3xl p-6 sm:p-10 shadow-2xl space-y-8 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-cyan-500/5 rounded-full blur-3xl pointer-events-none" />

        {/* Slide Header */}
        <div className="space-y-3 relative z-10 max-w-4xl">
          <span
            className={`text-xs font-mono font-bold uppercase tracking-wider px-3 py-1 rounded-full border inline-block ${slide.badgeColor}`}
          >
            {slide.badge}
          </span>
          <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
            {slide.title}
          </h2>
          <p className="text-base sm:text-lg text-slate-300 font-normal leading-relaxed">
            {slide.subtitle}
          </p>
        </div>

        {/* 3 Pillar Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 relative z-10">
          {slide.keyPoints.map((point, idx) => {
            const Icon = point.icon;
            return (
              <div
                key={idx}
                className="bg-slate-950/80 border border-slate-800/80 rounded-2xl p-5 space-y-3 hover:border-slate-700 transition-all shadow-lg flex flex-col justify-between"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="w-9 h-9 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-cyan-400 shadow-inner">
                      <Icon className="w-4 h-4" />
                    </div>
                    {point.metric && (
                      <span className="text-xs font-mono font-extrabold text-emerald-400 bg-emerald-950/80 border border-emerald-800/60 px-2.5 py-0.5 rounded-full">
                        {point.metric}
                      </span>
                    )}
                  </div>
                  <h3 className="text-sm font-bold text-white">{point.title}</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">{point.description}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Interactive Deep-Dive Action Row */}
        <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800/80 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 relative z-10">
          <div className="flex items-center gap-3">
            <Sparkles className="w-5 h-5 text-amber-400 shrink-0" />
            <p className="text-xs text-slate-300 leading-relaxed">
              <strong className="text-white">Interactive Verification: </strong>
              {slide.interactiveCallout}
            </p>
          </div>

          <button
            onClick={() => onNavigateTab(slide.targetTab)}
            className="px-4 py-2 rounded-xl bg-cyan-500 text-slate-950 font-bold text-xs hover:bg-cyan-400 transition-all flex items-center gap-2 shadow-lg shadow-cyan-500/20 shrink-0"
          >
            <span>{slide.buttonLabel}</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Speaker Notes Drawer */}
        {showSpeakerNotes && (
          <div className="p-5 rounded-2xl bg-cyan-950/20 border border-cyan-800/40 text-xs text-cyan-200/90 space-y-1.5 relative z-10">
            <div className="flex items-center gap-2 font-mono font-bold text-cyan-400 uppercase tracking-wider text-[11px]">
              <Info className="w-3.5 h-3.5" />
              <span>Executive Speaker Notes / Pitch Narrative:</span>
            </div>
            <p className="leading-relaxed font-sans text-slate-300">
              "{slide.speakerNotes}"
            </p>
          </div>
        )}

        {/* Slide Footer with Keyboard Hint */}
        <div className="flex items-center justify-between text-xs text-slate-500 font-mono pt-4 border-t border-slate-800/80">
          <span>HEIMDALL Proposal Pitch &bull; Artemis &amp; Commercial LEO Protection</span>
          <span className="hidden sm:inline">Use [◀ / ▶] or Spacebar to navigate</span>
        </div>
      </div>
    </div>
  );
};

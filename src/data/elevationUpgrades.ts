export interface ElevationUpgrade {
  id: string;
  title: string;
  category: 'Empirical Data' | 'High-Performance Computing' | 'Hardware in the Loop' | 'Verification & Catalog' | 'Statistical Physics';
  scoreImpact: number; // Point boost
  targetDimension: 'trl_maturity' | 'architecture' | 'edge_feasibility' | 'testing' | 'epistemology';
  dimensionBoost: number;
  badge: string;
  description: string;
  technicalDetails: string[];
  effortWeeks: number;
  activeByDefault?: boolean;
}

export const ELEVATION_UPGRADES: ElevationUpgrade[] = [
  {
    id: 'upg_swarm_demeter',
    title: 'Spaceborne In-Situ Telemetry Ingestion (ESA Swarm & CNES DEMETER)',
    category: 'Empirical Data',
    scoreImpact: 0.42,
    targetDimension: 'trl_maturity',
    dimensionBoost: 2.5, // Pushes TRL maturity from 7.0 to 9.5
    badge: 'TRL 4.5 Elevation',
    description:
      'Ingests historical high-rate (50 Hz) plasma density, electric field, and magnetometer telemetry from CNES DEMETER and ESA Swarm satellites to calibrate synthetic wake models against real ionospheric noise backgrounds.',
    technicalDetails: [
      'Automated netCDF4 / HDF5 telemetry parser with spatial KD-tree indexing',
      'Empirical background PSD (Power Spectral Density) modeling for auroral hiss and equatorial spread-F',
      'Blind validation against recorded meteor ablation and known small rocket body passes',
    ],
    effortWeeks: 4,
  },
  {
    id: 'upg_jax_vectorization',
    title: 'JAX / C++ Vectorized TDOA Solver & GPU Ambiguity Search',
    category: 'High-Performance Computing',
    scoreImpact: 0.25,
    targetDimension: 'architecture',
    dimensionBoost: 0.8, // Pushes Architecture from 9.2 to 10.0
    badge: '100x Speedup',
    description:
      'Replaces pure Python solver loops with JIT-compiled JAX and vectorized C++ kernels. Enables 100,000 Monte Carlo trajectory evaluations per second for massive multi-satellite constellation meshes.',
    technicalDetails: [
      'JAX `vmap` and `jit` compiled Levenberg-Marquardt optimizer with auto-differentiated Jacobians',
      'Batched 3D spatial ambiguity grid search running natively on GPU/NPU',
      'Zero-allocation memory layout for embedded flight execution (ARM Cortex-M7 & RISC-V)',
    ],
    effortWeeks: 3,
  },
  {
    id: 'upg_hil_sdr_bench',
    title: 'Hardware-in-the-Loop (HIL) Dual-SDR Chamber Bench',
    category: 'Hardware in the Loop',
    scoreImpact: 0.23,
    targetDimension: 'edge_feasibility',
    dimensionBoost: 1.8, // Pushes Edge Feasibility from 8.2 to 10.0
    badge: 'Physical SDR Verified',
    description:
      'Deploys an automated test bench linking Ettus USRP B205mini-i software-defined radios locked to a rubidium atomic standard to simulate real sub-nanosecond GNSS clock jitter and RF front-end phase noise.',
    technicalDetails: [
      'Dual-node synchronized SDR receiver rig with PPS (Pulse Per Second) sync verification',
      'Automated RF noise injection reproducing solar storm EMI and Faraday rotation',
      'CubeSat SWaP hardware validation (measured draw < 3.2W at 12V)',
    ],
    effortWeeks: 6,
  },
  {
    id: 'upg_norad_conjunction',
    title: 'Real-Time Space-Track / NORAD TLE Conjunction Cross-Fix',
    category: 'Verification & Catalog',
    scoreImpact: 0.12,
    targetDimension: 'testing',
    dimensionBoost: 0.6, // Pushes Testing from 9.4 to 10.0
    badge: 'Live Catalog Sync',
    description:
      'Direct REST connector to Space-Track.org / Celestrak 18th Space Defense Squadron catalog. Performs real-time B-plane covariance conjunction prediction whenever a candidate wake signature is detected.',
    technicalDetails: [
      'Automated SGP4 / SDP4 orbital propagator with atmospheric drag covariance inflation',
      'Foster-1992 3D collision probability ($P_c$) matrix integration with mahalanobis distance gating',
      'Automated false-positive filtering against known active payloads and space stations',
    ],
    effortWeeks: 2,
  },
  {
    id: 'upg_bayesian_mcmc',
    title: 'Hierarchical Bayesian MCMC Noise-Floor Inversion Engine',
    category: 'Statistical Physics',
    scoreImpact: 0.08,
    targetDimension: 'epistemology',
    dimensionBoost: 0.2, // Pushes Epistemology from 9.8 to 10.0
    badge: 'Rigorous Uncertainty',
    description:
      'Replaces simple threshold detection with Markov Chain Monte Carlo (MCMC) posterior parameter estimation, yielding rigorous 99.7% Bayesian credible intervals for debris charge $q$, velocity $v$, and miss distance $r$.',
    technicalDetails: [
      'No-U-Turn Sampler (NUTS) implementation for non-Gaussian plasma wake tails',
      'Physics-informed prior distributions based on IRI (International Reference Ionosphere)',
      'Automated convergence diagnostics with Gelman-Rubin $\hat{R} < 1.01$',
    ],
    effortWeeks: 3,
  },
];

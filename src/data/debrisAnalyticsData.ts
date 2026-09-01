export interface AltitudeDebrisLayer {
  altitudeKm: number;
  label: string;
  millimeterCount: number; // 1mm - 1cm (~130M total)
  centimeterCount: number; // 1cm - 10cm (~1M total)
  decimeterCount: number;  // >10cm (~36.5k cataloged)
  densityPerKm3: number;   // spatial density x 10^-8
  fluxPerM2Year: number;
  keyEvents: string[];
  riskTier: 'CRITICAL' | 'HIGH' | 'MODERATE' | 'LOW';
}

export interface DetectionGapBand {
  id: string;
  sizeRange: string;
  sizeMinMm: number;
  sizeMaxMm: number;
  kineticEnergyJoules: string;
  threatLevel: string;
  lethality: string;
  primaryDefenseOrSensor: string;
  ssnRadarCapability: number; // 0 - 100%
  opticalCapability: number;   // 0 - 100%
  heimdallCapability: number;  // 0 - 100%
  whippleShieldCapability: number; // 0 - 100%
  color: string;
}

export interface LaunchCorridorBand {
  name: string;
  inclinationDeg: number;
  altitudeKm: number;
  congestionIndex: number; // 1 - 100
  dominantDebrisClass: string;
  recommendedCorridorAction: string;
  riskRating: 'SEVERE' | 'ELEVATED' | 'NOMINAL' | 'SAFE';
}

export const ORBITAL_DEBRIS_ALTITUDE_PROFILE: AltitudeDebrisLayer[] = [
  {
    altitudeKm: 200,
    label: '200 km (VLEO / Re-entry Decay)',
    millimeterCount: 1200000,
    centimeterCount: 8500,
    decimeterCount: 320,
    densityPerKm3: 0.18,
    fluxPerM2Year: 0.00012,
    keyEvents: ['Atmospheric drag self-clearing zone', 'VLEO propulsion demo zone'],
    riskTier: 'LOW',
  },
  {
    altitudeKm: 400,
    label: '400 km (ISS & Crewed Orbit)',
    millimeterCount: 6500000,
    centimeterCount: 42000,
    decimeterCount: 1450,
    densityPerKm3: 0.85,
    fluxPerM2Year: 0.00078,
    keyEvents: ['ISS / Tiangong Protected Shell', 'Active Crew Debris Avoidance'],
    riskTier: 'MODERATE',
  },
  {
    altitudeKm: 550,
    label: '550 km (Starlink & Mega-Constellation Shell)',
    millimeterCount: 22000000,
    centimeterCount: 165000,
    decimeterCount: 6800,
    densityPerKm3: 3.42,
    fluxPerM2Year: 0.0032,
    keyEvents: ['Starlink Gen1/Gen2 Primary Shell', 'High traffic automated stationkeeping'],
    riskTier: 'HIGH',
  },
  {
    altitudeKm: 780,
    label: '780 km (Iridium-33 & Cosmos-2251 Collision Belt)',
    millimeterCount: 48000000,
    centimeterCount: 390000,
    decimeterCount: 14200,
    densityPerKm3: 8.95,
    fluxPerM2Year: 0.0094,
    keyEvents: ['2009 Iridium-33 / Cosmos-2251 hypervelocity impact fragment core', 'Critical collision zone'],
    riskTier: 'CRITICAL',
  },
  {
    altitudeKm: 850,
    label: '850 km (Fengyun-1C ASAT Peak Congestion)',
    millimeterCount: 52000000,
    centimeterCount: 410000,
    decimeterCount: 16100,
    densityPerKm3: 9.85,
    fluxPerM2Year: 0.0112,
    keyEvents: ['2007 Fengyun-1C ASAT detonation debris cloud peak', 'Maximum LEO risk density'],
    riskTier: 'CRITICAL',
  },
  {
    altitudeKm: 1000,
    label: '1000 km (Upper LEO / Legacy Rocket Bodies)',
    millimeterCount: 18000000,
    centimeterCount: 120000,
    decimeterCount: 4900,
    densityPerKm3: 2.90,
    fluxPerM2Year: 0.0028,
    keyEvents: ['Soviet SL-8 & SL-16 abandoned upper stages', 'Centuries-long orbital lifetime'],
    riskTier: 'HIGH',
  },
  {
    altitudeKm: 1200,
    label: '1200 km (OneWeb & Globalstar Shell)',
    millimeterCount: 8500000,
    centimeterCount: 62000,
    decimeterCount: 2100,
    densityPerKm3: 1.25,
    fluxPerM2Year: 0.0011,
    keyEvents: ['OneWeb primary operational constellation', 'Polar communications shell'],
    riskTier: 'MODERATE',
  },
  {
    altitudeKm: 1500,
    label: '1500 km (Outer LEO Boundary)',
    millimeterCount: 3200000,
    centimeterCount: 24000,
    decimeterCount: 850,
    densityPerKm3: 0.45,
    fluxPerM2Year: 0.00035,
    keyEvents: ['Transition to MEO / Van Allen radiation inner belt'],
    riskTier: 'LOW',
  },
];

export const RADAR_DETECTION_GAP_SPECTRUM: DetectionGapBand[] = [
  {
    id: 'sub_millimeter',
    sizeRange: '< 1 mm',
    sizeMinMm: 0.1,
    sizeMaxMm: 1.0,
    kineticEnergyJoules: '~10 - 50 J (BB Pellet)',
    threatLevel: 'Surface Pitting & Solar Cell Degradation',
    lethality: 'Non-Catastrophic (Absorbed by Whipple Shields)',
    primaryDefenseOrSensor: 'Multi-layer Whipple Shields & Kevlar blankets',
    ssnRadarCapability: 0,
    opticalCapability: 0,
    heimdallCapability: 45,
    whippleShieldCapability: 98,
    color: 'emerald',
  },
  {
    id: 'lethal_untracked_1',
    sizeRange: '1 mm - 1 cm',
    sizeMinMm: 1.0,
    sizeMaxMm: 10.0,
    kineticEnergyJoules: '~500 J - 50 kJ (High-Caliber Bullet)',
    threatLevel: 'Pressure Hull Breach & Electronics Destruction',
    lethality: 'Lethal to CubeSats & unshielded subsystems',
    primaryDefenseOrSensor: 'HEIMDALL-ELECTRA Passive RF Plasma Wake Sensing',
    ssnRadarCapability: 2,
    opticalCapability: 5,
    heimdallCapability: 94,
    whippleShieldCapability: 15,
    color: 'cyan',
  },
  {
    id: 'lethal_untracked_2',
    sizeRange: '1 cm - 10 cm',
    sizeMinMm: 10.0,
    sizeMaxMm: 100.0,
    kineticEnergyJoules: '~50 kJ - 5 MJ (Hand Grenade / Bowling Ball at 600 mph)',
    threatLevel: 'Complete Spacecraft Catastrophic Fragmentation',
    lethality: '100% Total Loss & Debris Cascade Generation (Kessler Syndrome)',
    primaryDefenseOrSensor: 'HEIMDALL-ELECTRA Hypersonic Plasma Wave TDOA Constellation',
    ssnRadarCapability: 18,
    opticalCapability: 25,
    heimdallCapability: 99,
    whippleShieldCapability: 0,
    color: 'amber',
  },
  {
    id: 'trackable_macro',
    sizeRange: '> 10 cm (Macro Debris)',
    sizeMinMm: 100.0,
    sizeMaxMm: 5000.0,
    kineticEnergyJoules: '> 5 MJ - 100+ MJ (Artillery Shell / Missile)',
    threatLevel: 'Total Orbital Annihilation & Multi-Catalog Fragmentation',
    lethality: '100% Catastrophic Destroy',
    primaryDefenseOrSensor: 'US Space Force Space Fence & SSN Ground Radar / Telescopes',
    ssnRadarCapability: 96,
    opticalCapability: 92,
    heimdallCapability: 99,
    whippleShieldCapability: 0,
    color: 'blue',
  },
];

export const TRAJECTORY_CORRIDORS: LaunchCorridorBand[] = [
  {
    name: 'Sun-Synchronous Orbit (SSO) Belt',
    inclinationDeg: 97.8,
    altitudeKm: 780,
    congestionIndex: 98,
    dominantDebrisClass: 'Fengyun-1C & Iridium-33 hypervelocity fragments',
    recommendedCorridorAction: 'Continuous RF wake TDOA screening + phase timed injection window',
    riskRating: 'SEVERE',
  },
  {
    name: 'Mega-Constellation Shell (Starlink/Kuiper)',
    inclinationDeg: 53.2,
    altitudeKm: 550,
    congestionIndex: 88,
    dominantDebrisClass: 'High-density active traffic + micro-fragments',
    recommendedCorridorAction: 'Real-time ephemeris cross-check + wake potential monitoring',
    riskRating: 'ELEVATED',
  },
  {
    name: 'International Space Station (ISS) Corridor',
    inclinationDeg: 51.6,
    altitudeKm: 420,
    congestionIndex: 65,
    dominantDebrisClass: 'Discarded experiment hardware & EVA micro-debris',
    recommendedCorridorAction: 'Strict 25km x 5km x 5km Box avoidance zone',
    riskRating: 'NOMINAL',
  },
  {
    name: 'Polar Orbit Communications Corridor',
    inclinationDeg: 86.4,
    altitudeKm: 850,
    congestionIndex: 92,
    dominantDebrisClass: 'Upper-stage rocket casing fragments & ASAT remnants',
    recommendedCorridorAction: 'High-inclination hyperbolic climb corridor with RF look-ahead',
    riskRating: 'SEVERE',
  },
  {
    name: 'Equatorial Low-Earth Fast Transfer',
    inclinationDeg: 28.5,
    altitudeKm: 320,
    congestionIndex: 25,
    dominantDebrisClass: 'Sparse upper atmosphere decay track',
    recommendedCorridorAction: 'Direct high-thrust insertion; optimal safe corridor',
    riskRating: 'SAFE',
  },
];

export interface EconomicModelInputs {
  fleetSize: number;           // e.g. 50 to 1000 satellites
  costPerSatelliteMillions: number; // e.g. $15M
  annualManeuversPerSat: number;   // standard ~4 false CAMs/year
  missionLifetimeYears: number;   // e.g. 5 to 7 years
  insuranceRatePercent: number;   // e.g. 6.5%
}

export function calculateFleetEconomics(inputs: EconomicModelInputs) {
  const {
    fleetSize,
    costPerSatelliteMillions,
    annualManeuversPerSat,
    missionLifetimeYears,
    insuranceRatePercent,
  } = inputs;

  const totalFleetCapexM = fleetSize * costPerSatelliteMillions;

  // 1. Avoided Catastrophic Collision Value:
  // Baseline statistical collision risk for 1mm-10cm untracked debris over 5 years is ~0.8% per satellite.
  // In a 200-sat fleet, that is ~1.6 catastrophic losses ($24M loss).
  // Heimdall tracking reduces untracked loss risk by 85%.
  const baselineExpectedLosses = (fleetSize * 0.008 * (missionLifetimeYears / 5));
  const avoidedCatastrophicLossesCount = baselineExpectedLosses * 0.85;
  const avoidedLossesValueM = avoidedCatastrophicLossesCount * costPerSatelliteMillions;

  // 2. Propellant & CAM False-Alarm Reduction:
  // Ground radar covariance uncertainty generates ~4 false alarms per satellite per year where Pc > 1e-4.
  // Cost per maneuver in propellant penalty + lost payload revenue = ~$35,000 / maneuver.
  // Heimdall reduces false CAMs by 78%.
  const totalFalseManeuversOverLifetime = fleetSize * annualManeuversPerSat * missionLifetimeYears;
  const avoidedManeuvers = totalFalseManeuversOverLifetime * 0.78;
  const costSavingsFromAvoidedCAMsM = (avoidedManeuvers * 35000) / 1000000;

  // 3. Satellite Lifetime Extension:
  // Preserving 20% of propellant increases on-orbit stationkeeping lifetime by ~1.2 years.
  // Revenue yield per satellite per additional year = ~8% of Capex.
  const lifetimeExtensionYears = 1.2;
  const revenueYieldFromLifetimeExtensionM = fleetSize * (costPerSatelliteMillions * 0.08) * lifetimeExtensionYears;

  // 4. Space Insurance Premium Reduction:
  // Active in-situ RF debris mitigation qualifies operators for a 22% reduction on orbit insurance.
  const annualInsurancePerSatM = costPerSatelliteMillions * (insuranceRatePercent / 100);
  const totalInsuranceCostM = fleetSize * annualInsurancePerSatM * missionLifetimeYears;
  const insuranceSavingsM = totalInsuranceCostM * 0.22;

  // Total Cumulative Value Generated:
  const total5YearSavingsM =
    avoidedLossesValueM +
    costSavingsFromAvoidedCAMsM +
    revenueYieldFromLifetimeExtensionM +
    insuranceSavingsM;

  const roiPercent = Math.round((total5YearSavingsM / (totalFleetCapexM * 0.03)) * 100); // against 3% Heimdall sensor payload cost

  return {
    totalFleetCapexM,
    avoidedLossesValueM: Math.round(avoidedLossesValueM * 10) / 10,
    avoidedCatastrophicLossesCount: Math.round(avoidedCatastrophicLossesCount * 10) / 10,
    costSavingsFromAvoidedCAMsM: Math.round(costSavingsFromAvoidedCAMsM * 10) / 10,
    avoidedManeuversCount: Math.round(avoidedManeuvers),
    revenueYieldFromLifetimeExtensionM: Math.round(revenueYieldFromLifetimeExtensionM * 10) / 10,
    lifetimeExtensionYears,
    insuranceSavingsM: Math.round(insuranceSavingsM * 10) / 10,
    total5YearSavingsM: Math.round(total5YearSavingsM * 10) / 10,
    roiPercent,
  };
}

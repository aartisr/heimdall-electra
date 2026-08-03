/**
 * TypeScript types matching the Python-generated JSON output.
 * Each type includes a runtime validator that throws on malformed data.
 *
 * Design: Fail-fast validation at the data boundary — identical philosophy
 * to the Python domain contracts.  All optional UI state is typed separately
 * so the data layer stays pure.
 */

// ---------------------------------------------------------------------------
// Shared
// ---------------------------------------------------------------------------

export type EvidenceClass = "synthetic" | "laboratory" | "observed" | "external_context";

export type SizeRegime = "tracked" | "near_detectable" | "sub_cm" | "sub_mm";

export type RiskLevel = "very_low" | "low" | "moderate" | "high" | "very_high";

// ---------------------------------------------------------------------------
// Stage 1 — Debris population
// ---------------------------------------------------------------------------

export interface FragmentationEvent {
  event_id: string;
  name: string;
  year: number;
  orbital_altitude_km: number;
  orbital_inclination_deg: number;
  raan_deg: number;
  catalogued_fragment_count: number;
  estimated_sub_cm_count: number;
  source_reference: string;
}

export interface DebrisCloud {
  cloud_id: string;
  event_id: string;
  centroid_altitude_km: number;
  centroid_inclination_deg: number;
  centroid_raan_deg: number;
  spread_altitude_km: number;
  spread_inclination_deg: number;
  peak_number_density_per_km3: number;
  total_mass_estimate_kg: number;
  size_regime: SizeRegime;
  evidence_class: EvidenceClass;
  limitation: string;
}

export interface DebrisShell {
  altitude_km_min: number;
  altitude_km_max: number;
  inclination_deg_min: number;
  inclination_deg_max: number;
  size_regime: SizeRegime;
  object_count: number;
  spatial_density_per_km3: number;
  flux_per_m2_per_year: number;
  population_source: string;
  uncertainty_fraction: number;
  evidence_class: EvidenceClass;
}

export interface DebrisPopulation {
  snapshot_id: string;
  generated_at: string;
  model_version: string;
  model_id: string;
  source_reference: string;
  total_tracked_objects: number;
  estimated_sub_cm_total: number;
  altitude_range_km: [number, number];
  evidence_class: EvidenceClass;
  limitation: string;
  events: FragmentationEvent[];
  clouds: DebrisCloud[];
  shells: DebrisShell[];
}

// ---------------------------------------------------------------------------
// Stage 2 — Radar detectability
// ---------------------------------------------------------------------------

export interface RcsPoint {
  diameter_m: number;
  rcs_m2: number;
  rcs_dbsm: number;
  regime: "rayleigh" | "mie" | "optical";
  detectable: boolean;
}

export interface RadarCurve {
  system_id: string;
  system_name: string;
  frequency_hz: number;
  wavelength_m: number;
  min_detectable_rcs_dbsm: number;
  min_detectable_diameter_m: number;
  source_reference: string;
  evidence_class: EvidenceClass;
  limitation: string;
  points: RcsPoint[];
}

export interface WakeSignalPoint {
  diameter_m: number;
  relative_signal_db: number;
  is_above_noise: boolean;
}

export interface WakeCurve {
  plasma_model_id: string;
  orbital_altitude_km: number;
  electron_density_per_m3: number;
  evidence_class: EvidenceClass;
  limitation: string;
  points: WakeSignalPoint[];
}

export interface RcsAnalysis {
  analysis_id: string;
  generated_at: string;
  gap_min_diameter_m: number;
  gap_max_diameter_m: number;
  undetected_population_fraction: number;
  evidence_class: EvidenceClass;
  limitation: string;
  radar_curves: RadarCurve[];
  wake_curve: WakeCurve;
}

// ---------------------------------------------------------------------------
// Stage 3 — Trajectory risk
// ---------------------------------------------------------------------------

export interface RiskFieldCell {
  altitude_km: number;
  inclination_deg: number;
  flux_tracked: number;
  flux_full: number;
  dark_risk_fraction: number;
  log10_flux_full: number;
}

export interface ProfileScore {
  profile_id: string;
  cumulative_collision_probability: number;
  collision_probability_tracked_only: number;
  collision_probability_full_population: number;
  dark_risk_fraction: number;
  expected_encounters_per_year: number;
  peak_flux_altitude_km: number;
  risk_level: RiskLevel;
  evidence_class: EvidenceClass;
  limitation: string;
}

export interface SafeCorridor {
  corridor_id: string;
  altitude_min_km: number;
  altitude_max_km: number;
  inclination_min_deg: number;
  inclination_max_deg: number;
  max_collision_probability: number;
  risk_margin_factor: number;
  evidence_class: EvidenceClass;
  limitation: string;
}

export interface RiskField {
  report_id: string;
  generated_at: string;
  population_snapshot_id: string;
  risk_threshold: number;
  spacecraft_cross_section_m2: number;
  mission_duration_years: number;
  evidence_class: EvidenceClass;
  limitation: string;
  risk_field: RiskFieldCell[];
  profile_scores: ProfileScore[];
  safe_corridors: SafeCorridor[];
}

// ---------------------------------------------------------------------------
// Stage 4 — Cost savings
// ---------------------------------------------------------------------------

export interface MissionSavings {
  estimate_id: string;
  mission_class: string;
  analysis_period_years: number;
  avoided_maneuvers_usd: number;
  reduced_insurance_usd: number;
  launch_delay_reduction_usd: number;
  propellant_preserved_usd: number;
  total_savings_usd: number;
  uncertainty_low_usd: number;
  uncertainty_high_usd: number;
  assumptions: string[];
  evidence_class: EvidenceClass;
  limitation: string;
}

export interface FleetEntry {
  mission_class: string;
  annual_count: number;
}

export interface CostSavings {
  scenario_id: string;
  generated_at: string;
  fleet: FleetEntry[];
  annual_savings_usd: number;
  ten_year_savings_usd: number;
  uncertainty_low_usd: number;
  uncertainty_high_usd: number;
  evidence_class: EvidenceClass;
  limitation: string;
  per_mission_estimates: MissionSavings[];
}

// ---------------------------------------------------------------------------
// Runtime validators — fail-fast, actionable error messages
// ---------------------------------------------------------------------------

function requireString(v: unknown, field: string): string {
  if (typeof v !== "string" || !v.trim())
    throw new Error(`Visualization data invalid: ${field} must be a non-empty string`);
  return v;
}

function requireNumber(v: unknown, field: string): number {
  if (typeof v !== "number" || !isFinite(v))
    throw new Error(`Visualization data invalid: ${field} must be a finite number`);
  return v;
}

function requireArray(v: unknown, field: string): unknown[] {
  if (!Array.isArray(v))
    throw new Error(`Visualization data invalid: ${field} must be an array`);
  return v;
}

function requireObject(v: unknown, field: string): Record<string, unknown> {
  if (typeof v !== "object" || v === null || Array.isArray(v))
    throw new Error(`Visualization data invalid: ${field} must be an object`);
  return v as Record<string, unknown>;
}

export function validateDebrisPopulation(raw: unknown): DebrisPopulation {
  const r = requireObject(raw, "DebrisPopulation");
  requireString(r.snapshot_id, "snapshot_id");
  requireString(r.limitation, "limitation");
  requireNumber(r.total_tracked_objects, "total_tracked_objects");
  requireArray(r.shells, "shells");
  requireArray(r.clouds, "clouds");
  requireArray(r.events, "events");
  return r as unknown as DebrisPopulation;
}

export function validateRcsAnalysis(raw: unknown): RcsAnalysis {
  const r = requireObject(raw, "RcsAnalysis");
  requireString(r.analysis_id, "analysis_id");
  requireString(r.limitation, "limitation");
  requireArray(r.radar_curves, "radar_curves");
  requireObject(r.wake_curve, "wake_curve");
  return r as unknown as RcsAnalysis;
}

export function validateRiskField(raw: unknown): RiskField {
  const r = requireObject(raw, "RiskField");
  requireString(r.report_id, "report_id");
  requireArray(r.risk_field, "risk_field");
  requireArray(r.profile_scores, "profile_scores");
  return r as unknown as RiskField;
}

export function validateCostSavings(raw: unknown): CostSavings {
  const r = requireObject(raw, "CostSavings");
  requireString(r.scenario_id, "scenario_id");
  requireNumber(r.annual_savings_usd, "annual_savings_usd");
  requireArray(r.per_mission_estimates, "per_mission_estimates");
  return r as unknown as CostSavings;
}

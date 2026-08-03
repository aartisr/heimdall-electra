/**
 * TanStack Query hooks for all four visualization data sources.
 *
 * Design:
 *  - Each hook is completely self-contained and can be used independently.
 *  - Validation at the fetch boundary — malformed JSON throws before reaching
 *    any component.
 *  - staleTime: Infinity because the JSON files are versioned static exports.
 *  - Retry: 2 attempts with exponential back-off (TanStack Query default).
 */

import { useQuery } from "@tanstack/react-query";
import {
  DebrisPopulation,
  RcsAnalysis,
  RiskField,
  CostSavings,
  validateDebrisPopulation,
  validateRcsAnalysis,
  validateRiskField,
  validateCostSavings,
} from "./types";

const BASE = (import.meta as { env?: { BASE_URL?: string } }).env?.BASE_URL ?? "/";
const url = (file: string) => `${BASE}${file}`.replace("//", "/");

async function fetchJson<T>(file: string, validate: (raw: unknown) => T): Promise<T> {
  const res = await fetch(url(file));
  if (!res.ok) throw new Error(`Failed to load ${file}: HTTP ${res.status}`);
  const raw = await res.json();
  return validate(raw);
}

export function useDebrisPopulation() {
  return useQuery<DebrisPopulation, Error>({
    queryKey: ["visualization", "debris-population"],
    queryFn: () => fetchJson("debris_population.json", validateDebrisPopulation),
    staleTime: Infinity,
  });
}

export function useRcsAnalysis() {
  return useQuery<RcsAnalysis, Error>({
    queryKey: ["visualization", "rcs-analysis"],
    queryFn: () => fetchJson("rcs_analysis.json", validateRcsAnalysis),
    staleTime: Infinity,
  });
}

export function useRiskField() {
  return useQuery<RiskField, Error>({
    queryKey: ["visualization", "risk-field"],
    queryFn: () => fetchJson("risk_field.json", validateRiskField),
    staleTime: Infinity,
  });
}

export function useCostSavings() {
  return useQuery<CostSavings, Error>({
    queryKey: ["visualization", "cost-savings"],
    queryFn: () => fetchJson("cost_savings.json", validateCostSavings),
    staleTime: Infinity,
  });
}

export type EvidenceClass = "synthetic" | "laboratory" | "observed" | "external_context";

export interface ResearchSource {
  id: string;
  /** A declared display label; some governed sources legitimately span classes. */
  evidenceClass: string;
  purpose: string;
  status: string;
  limitation: string;
}

export interface ResearchGate {
  stage: string;
  status: "complete" | "in_progress" | "blocked";
  condition: string;
}

export interface ResearchClaim {
  statement: string;
  scope: "software" | "scientific" | "observed_detection" | "operational";
  status: "supported" | "unsupported" | "prohibited";
  limitation: string;
}

export interface ResearchStatus {
  generatedAt: string;
  scientificStatus: string;
  limitation: string;
  sources: ResearchSource[];
  gates: ResearchGate[];
  claims: ResearchClaim[];
}

type UnknownRecord = Record<string, unknown>;

function record(value: unknown, label: string): UnknownRecord {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new Error(`Research status is invalid: ${label} must be an object.`);
  }
  return value as UnknownRecord;
}

function string(value: unknown, label: string): string {
  if (typeof value !== "string" || !value.trim()) {
    throw new Error(`Research status is invalid: ${label} must be a non-empty string.`);
  }
  return value;
}

function list(value: unknown, label: string): unknown[] {
  if (!Array.isArray(value)) throw new Error(`Research status is invalid: ${label} must be a list.`);
  return value;
}

function oneOf<T extends string>(value: unknown, label: string, values: readonly T[]): T {
  const item = string(value, label);
  if (!values.includes(item as T)) throw new Error(`Research status is invalid: ${label} has an unknown value.`);
  return item as T;
}

/** Converts the governed JSON's snake_case fields into a safe UI contract. */
export function parseResearchStatus(value: unknown): ResearchStatus {
  const root = record(value, "root");
  return {
    generatedAt: string(root.generatedAt, "generatedAt"),
    scientificStatus: string(root.scientificStatus, "scientificStatus"),
    limitation: string(root.limitation, "limitation"),
    sources: list(root.sources, "sources").map((value, index) => {
      const source = record(value, `sources[${index}]`);
      return {
        id: string(source.id, `sources[${index}].id`),
        evidenceClass: string(source.evidence_class, `sources[${index}].evidence_class`),
        purpose: string(source.purpose, `sources[${index}].purpose`),
        status: string(source.status, `sources[${index}].status`),
        limitation: string(source.limitation, `sources[${index}].limitation`),
      };
    }),
    gates: list(root.gates, "gates").map((value, index) => {
      const gate = record(value, `gates[${index}]`);
      return {
        stage: string(gate.stage, `gates[${index}].stage`),
        status: oneOf(gate.status, `gates[${index}].status`, ["complete", "in_progress", "blocked"]),
        condition: string(gate.condition, `gates[${index}].condition`),
      };
    }),
    claims: list(root.claims, "claims").map((value, index) => {
      const claim = record(value, `claims[${index}]`);
      return {
        statement: string(claim.statement, `claims[${index}].statement`),
        scope: oneOf(claim.scope, `claims[${index}].scope`, ["software", "scientific", "observed_detection", "operational"]),
        status: oneOf(claim.status, `claims[${index}].status`, ["supported", "unsupported", "prohibited"]),
        limitation: string(claim.limitation, `claims[${index}].limitation`),
      };
    }),
  };
}

export async function fetchResearchStatus(): Promise<ResearchStatus> {
  const response = await fetch("/research-status.json", {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) throw new Error("Research status is unavailable.");
  return parseResearchStatus(await response.json());
}

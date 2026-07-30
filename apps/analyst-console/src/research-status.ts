export type EvidenceClass = "synthetic" | "laboratory" | "observed" | "external_context";

export interface ResearchSource {
  id: string;
  evidenceClass: EvidenceClass;
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

export async function fetchResearchStatus(): Promise<ResearchStatus> {
  const response = await fetch("/research-status.json", {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) throw new Error("Research status is unavailable.");
  return response.json() as Promise<ResearchStatus>;
}

export interface ScoreDimension {
  id: string;
  name: string;
  category: string;
  score: number; // 1 to 10
  maxScore: number;
  weight: number; // percentage in default calculation
  grade: string;
  summary: string;
  pros: string[];
  cons: string[];
  keyArtifacts: string[];
  metrics: {
    label: string;
    value: string | number;
    benchmark?: string;
  }[];
}

export interface ClaimRule {
  id: string;
  claim: string;
  status: 'SUPPORTED' | 'CONDITIONAL' | 'UNSUPPORTED' | 'STRICTLY_PROHIBITED';
  governanceReason: string;
  evidenceClass: 'synthetic' | 'laboratory' | 'observed' | 'none';
  docReference: string;
}

export interface TestSuiteMetric {
  category: string;
  fileCount: number;
  testCount: number;
  coverageEstimate: string;
  highlights: string[];
}

export interface TrlPhase {
  trl: number;
  title: string;
  status: 'COMPLETED' | 'IN_PROGRESS' | 'PLANNED';
  description: string;
  milestones: string[];
  deliverables: string[];
}

export interface EvaluationPreset {
  id: string;
  name: string;
  description: string;
  weights: Record<string, number>;
}

// API client for the Saathi AI 3.0 backend.
const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function get<T>(path: string): Promise<T> {
  const r = await fetch(`${BASE}${path}`);
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`);
  return r.json();
}
async function post<T>(path: string, body: unknown): Promise<T> {
  const r = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`);
  return r.json();
}

export interface FFI {
  ffi: number;
  source: string;
  sub_scores: Record<string, number>;
  top_drivers: { label: string; impact: number }[];
  explanation: string;
}
export interface DNA {
  dna: Record<string, { score: number; drivers: { label: string; direction: string }[] }>;
}
export interface LifeEvents {
  predictions: {
    event: string;
    probability: number;
    signals: { signal: string; why: string }[];
    recommended_journey: string;
    explanation: string;
  }[];
}
export interface FutureGraph {
  current_balance: number;
  monthly_saving_estimate: number;
  history: { month: string; balance: number }[];
  projection: { month: string; balance: number }[];
  explanation: string;
}
export interface GPS {
  goal: string;
  gap: number;
  required_monthly: number;
  months_to_goal: number;
  plan: { instrument: string; allocation_pct: number; monthly_amount: number }[];
  feasibility: { on_track: boolean; shortfall: number } | null;
  explanation: string;
}
export interface RM {
  loop: {
    predict: { event: string; probability: number };
    reason: string;
    recommend: { action: string; product: string; reasoning: string; requires_human_approval: boolean };
  };
  narrative: string;
}
export interface Prospects {
  event: string;
  prospects: { customer_id: string; name: string; city: string; ffi: number; probability: number }[];
}

export const api = {
  ffi: (id: string) => get<FFI>(`/api/v1/customers/${id}/ffi`),
  dna: (id: string) => get<DNA>(`/api/v1/customers/${id}/dna`),
  lifeEvents: (id: string) => get<LifeEvents>(`/api/v1/customers/${id}/life-events`),
  futureGraph: (id: string) => get<FutureGraph>(`/api/v1/customers/${id}/future-graph`),
  peers: (id: string) => get<{ insights: string[] }>(`/api/v1/customers/${id}/peers`),
  gps: (id: string, body: object) => post<GPS>(`/api/v1/customers/${id}/gps`, body),
  rm: (id: string, question?: string) => post<RM>(`/api/v1/customers/${id}/rm`, { question }),
  prospects: (event = 'home_purchase') => get<Prospects>(`/api/v1/sbi/prospects?event=${event}`),
  feedback: (customerId: string, thumbsUp: boolean, comment: string | null) =>
    post<{ status: string; feedback_id: string }>('/api/v1/feedback', {
      customer_id: customerId,
      thumbs_up: thumbsUp,
      comment,
    }),
};

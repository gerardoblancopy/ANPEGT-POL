const BASE = '/api';

export async function fetchCycles(): Promise<unknown> {
  const res = await fetch(`${BASE}/cycles`);
  return res.json();
}

export async function fetchOverview(): Promise<unknown> {
  const res = await fetch(`${BASE}/overview`);
  return res.json();
}

export async function fetchPriorities(cycle: number): Promise<unknown> {
  const res = await fetch(`${BASE}/cycles/${cycle}/priorities`);
  return res.json();
}

export async function fetchGlobalPlan(cycle: number): Promise<unknown> {
  const res = await fetch(`${BASE}/cycles/${cycle}/global-plan`);
  return res.json();
}

export async function fetchSectorPlans(cycle: number): Promise<unknown> {
  const res = await fetch(`${BASE}/cycles/${cycle}/sector-plans`);
  return res.json();
}

export async function fetchCommunicationPlans(cycle: number): Promise<unknown> {
  const res = await fetch(`${BASE}/cycles/${cycle}/communication`);
  return res.json();
}

export async function fetchSocialPosts(cycle: number): Promise<unknown> {
  const res = await fetch(`${BASE}/cycles/${cycle}/social-posts`);
  return res.json();
}

export async function fetchSpeeches(cycle: number): Promise<unknown> {
  const res = await fetch(`${BASE}/cycles/${cycle}/speeches`);
  return res.json();
}

export async function fetchFitness(cycle: number): Promise<unknown> {
  const res = await fetch(`${BASE}/cycles/${cycle}/fitness`);
  return res.json();
}

export async function fetchCycleRun(cycle: number): Promise<unknown> {
  const res = await fetch(`${BASE}/cycles/${cycle}/cycle-run`);
  return res.json();
}

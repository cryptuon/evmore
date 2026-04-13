// Stateless API client for the evmore-dashboard backend.
// Base URL resolves to same-origin ("/api") by default; override with VITE_API_BASE for local dev.

const rawBase = (import.meta.env.VITE_API_BASE as string | undefined)?.replace(/\/$/, '') ?? ''
const API_BASE = `${rawBase}/api`

export interface ApiChain {
  key: string
  name: string
  chain_id: number
  public_rpc_url?: string | null
  token_address?: string | null
  verifier_address?: string | null
  bridge_address?: string | null
  explorer?: string | null
  is_testnet: boolean
}

export interface ApiConfig {
  chains: ApiChain[]
}

export interface ApiOverview {
  chain_key: string
  chain_id: number
  token_address: string
  total_supply: string
  max_supply: string
  circulating_percent: number
  blocks_mined: string
  current_difficulty: string
  current_challenge: string
  last_mining_timestamp: number
  seconds_since_last_block: number
  current_reward: string
  next_halving_block: string
  blocks_until_halving: string
  latest_block: number
}

export interface ApiPrice {
  eth_usd: number | null
  eth_usd_24h_change: number | null
  evmore_usd: number | null
  evmore_usd_24h_change: number | null
  source: string
}

async function request<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { accept: 'application/json' }
  })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`API ${path} failed: ${res.status} ${text}`)
  }
  return res.json() as Promise<T>
}

export const api = {
  health: () => request<{ status: string }>('/health'),
  config: () => request<ApiConfig>('/config'),
  overview: (chain: string) => request<ApiOverview>(`/overview?chain=${encodeURIComponent(chain)}`),
  price: () => request<ApiPrice>('/price')
}

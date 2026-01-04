import type { BrowserProvider, JsonRpcSigner } from 'ethers'

// Wallet types
export interface WalletState {
  address: string | null
  chainId: number | null
  isConnected: boolean
  isConnecting: boolean
  provider: BrowserProvider | null
  signer: JsonRpcSigner | null
  ethBalance: bigint
  error: string | null
}

// Token types
export interface TokenState {
  balance: bigint
  totalSupply: bigint
  allowances: Map<string, bigint>
}

// Mining types
export interface EpochData {
  blockNumber: bigint
  totalReward: bigint
  minerCount: bigint
  claimedCount: bigint
  timestamp: bigint
}

export interface MiningProof {
  solution: Uint8Array
  timestamp: bigint
  claimed: boolean
}

export interface MiningState {
  currentChallenge: string
  currentDifficulty: bigint
  currentEpoch: bigint
  blocksMined: bigint
  lastMiningTimestamp: bigint
  isMining: boolean
  hashRate: number
  foundSolutions: string[]
}

// Bridge types
export interface BridgeConfig {
  minAmount: bigint
  maxAmount: bigint
  dailyLimit: bigint
  withdrawalDelay: bigint
  feeRate: bigint
}

export interface BridgeRequest {
  user: string
  amount: bigint
  timestamp: bigint
  nonce: bigint
  processed: boolean
  direction: 0 | 1
}

export interface BridgeStats {
  totalBridgedToPolygon: bigint
  totalBridgedFromPolygon: bigint
  requestsCount: bigint
  isActive: boolean
}

// Notification types
export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  timestamp: number
  autoClose?: boolean
  duration?: number
}

// Transaction types
export interface TransactionState {
  hash: string | null
  status: 'pending' | 'success' | 'failed' | null
  error: string | null
}

// Contract constants
export const EVMORE_CONSTANTS = {
  MAX_SUPPLY: BigInt('21000000000000000000000000'), // 21M * 10^18
  INITIAL_REWARD: BigInt('50000000000000000000'), // 50 * 10^18
  HALVING_BLOCKS: 210000,
  TARGET_BLOCK_TIME: 600, // 10 minutes
  DIFFICULTY_ADJUSTMENT_INTERVAL: 2016,
  SOLUTION_SIZE: 128, // 4 * 32 bytes
  DECIMALS: 18
} as const

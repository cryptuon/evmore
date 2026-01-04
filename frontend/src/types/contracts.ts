import type { TransactionResponse } from 'ethers'

// Type definitions for EVMORE smart contracts
// These are standalone interfaces that define the contract methods
// Use with type assertions when creating Contract instances

export interface EvmoreContract {
  // ERC-20 methods
  balanceOf(address: string): Promise<bigint>
  totalSupply(): Promise<bigint>
  allowance(owner: string, spender: string): Promise<bigint>
  transfer(to: string, amount: bigint): Promise<TransactionResponse>
  approve(spender: string, amount: bigint): Promise<TransactionResponse>

  // Mining methods
  currentChallenge(): Promise<string>
  currentDifficulty(): Promise<bigint>
  current_epoch(): Promise<bigint>
  blocksMined(): Promise<bigint>
  lastMiningTimestamp(): Promise<bigint>
  submitProof(solution: Uint8Array): Promise<TransactionResponse>
  submitProofBatch(solutions: Uint8Array[]): Promise<TransactionResponse>
  claimReward(epoch: bigint): Promise<TransactionResponse>
  epochs(epoch: bigint): Promise<[bigint, bigint, bigint, bigint, bigint]>
  miner_claimed_epochs(miner: string, epoch: bigint): Promise<boolean>
}

export interface VerifierContract {
  verify_solution(challenge: string, solution: Uint8Array, difficulty: bigint): Promise<boolean>
}

export interface BridgeContract {
  getBridgeStats(): Promise<[bigint, bigint, bigint, boolean]>
  getBridgeConfig(): Promise<[bigint, bigint, bigint, bigint, bigint]>
  isBridgeActive(): Promise<boolean>
  getDailyVolume(): Promise<bigint>
  getUserDailyVolume(user: string): Promise<bigint>
  bridgeToPolygon(amount: bigint): Promise<TransactionResponse>
  getBridgeRequest(requestId: string): Promise<[string, bigint, bigint, bigint, boolean, number]>
}

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { Contract, type InterfaceAbi } from 'ethers'
import { useWalletStore } from './wallet'
import { EVMORE_TOKEN_ADDRESS, VERIFIER_ADDRESS, type ChainId } from '@/contracts/addresses'
import { EVMORE_CONSTANTS, type EpochData } from '@/types'
import type { EvmoreContract, VerifierContract } from '@/types/contracts'
import EvmoreTokenABI from '@/contracts/abis/EvmoreToken.json'
import VerifierABI from '@/contracts/abis/KeccakCollisionVerifier.json'

export const useMiningStore = defineStore('mining', () => {
  const walletStore = useWalletStore()

  // Mining state
  const currentChallenge = ref<string>('')
  const currentDifficulty = ref<bigint>(0n)
  const currentEpoch = ref<bigint>(0n)
  const blocksMined = ref<bigint>(0n)
  const lastMiningTimestamp = ref<bigint>(0n)

  // Mining activity
  const isMining = ref(false)
  const hashRate = ref(0)
  const foundSolutions = ref<string[]>([])

  // User's mining data
  const claimableEpochs = ref<bigint[]>([])
  const userEpochHistory = ref<Map<bigint, EpochData>>(new Map())

  // Loading state
  const isLoading = ref(false)
  const isSubmitting = ref(false)
  const error = ref<string | null>(null)

  // Contracts
  const tokenContract = computed((): EvmoreContract | null => {
    if (!walletStore.signer || !walletStore.chainId) return null

    const address = EVMORE_TOKEN_ADDRESS[walletStore.chainId as ChainId]
    if (!address) return null

    return new Contract(address, EvmoreTokenABI as InterfaceAbi, walletStore.signer) as unknown as EvmoreContract
  })

  const verifierContract = computed((): VerifierContract | null => {
    if (!walletStore.signer || !walletStore.chainId) return null

    const address = VERIFIER_ADDRESS[walletStore.chainId as ChainId]
    if (!address) return null

    return new Contract(address, VerifierABI as InterfaceAbi, walletStore.signer) as unknown as VerifierContract
  })

  // Computed
  const currentReward = computed(() => {
    const halvings = Number(blocksMined.value / BigInt(EVMORE_CONSTANTS.HALVING_BLOCKS))
    return EVMORE_CONSTANTS.INITIAL_REWARD >> BigInt(halvings)
  })

  const nextHalvingBlocks = computed(() => {
    const nextHalving = ((blocksMined.value / BigInt(EVMORE_CONSTANTS.HALVING_BLOCKS)) + 1n) * BigInt(EVMORE_CONSTANTS.HALVING_BLOCKS)
    return nextHalving - blocksMined.value
  })

  const timeSinceLastMining = computed(() => {
    if (lastMiningTimestamp.value === 0n) return 0n
    return BigInt(Math.floor(Date.now() / 1000)) - lastMiningTimestamp.value
  })

  const epochProgress = computed(() => {
    const elapsed = Number(timeSinceLastMining.value)
    const target = EVMORE_CONSTANTS.TARGET_BLOCK_TIME
    return Math.min((elapsed / target) * 100, 100)
  })

  const canMineNewEpoch = computed(() => {
    return timeSinceLastMining.value >= BigInt(EVMORE_CONSTANTS.TARGET_BLOCK_TIME)
  })

  // Actions
  async function fetchMiningState() {
    const tc = tokenContract.value
    if (!tc) return

    isLoading.value = true
    error.value = null

    try {
      const [challenge, difficulty, epoch, mined, timestamp] = await Promise.all([
        tc.currentChallenge(),
        tc.currentDifficulty(),
        tc.current_epoch(),
        tc.blocksMined(),
        tc.lastMiningTimestamp()
      ])

      currentChallenge.value = challenge
      currentDifficulty.value = difficulty
      currentEpoch.value = epoch
      blocksMined.value = mined
      lastMiningTimestamp.value = timestamp
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Unknown error'
      console.error('Failed to fetch mining state:', e)
    } finally {
      isLoading.value = false
    }
  }

  async function submitProof(solution: Uint8Array) {
    const tc = tokenContract.value
    if (!tc) throw new Error('Contract not initialized')

    isSubmitting.value = true
    error.value = null

    try {
      const tx = await tc.submitProof(solution)
      const receipt = await tx.wait()

      // Refresh mining state after submission
      await fetchMiningState()

      return { tx, receipt }
    } catch (e: unknown) {
      error.value = parseContractError(e)
      throw e
    } finally {
      isSubmitting.value = false
    }
  }

  async function submitProofBatch(solutions: Uint8Array[]) {
    const tc = tokenContract.value
    if (!tc) throw new Error('Contract not initialized')
    if (solutions.length > 10) throw new Error('Batch size exceeds limit of 10')

    isSubmitting.value = true
    error.value = null

    try {
      const tx = await tc.submitProofBatch(solutions)
      const receipt = await tx.wait()

      await fetchMiningState()

      return { tx, receipt }
    } catch (e: unknown) {
      error.value = parseContractError(e)
      throw e
    } finally {
      isSubmitting.value = false
    }
  }

  async function claimReward(epoch: bigint) {
    const tc = tokenContract.value
    if (!tc) throw new Error('Contract not initialized')

    isSubmitting.value = true
    error.value = null

    try {
      const tx = await tc.claimReward(epoch)
      const receipt = await tx.wait()

      // Remove from claimable list
      claimableEpochs.value = claimableEpochs.value.filter(e => e !== epoch)

      return { tx, receipt }
    } catch (e: unknown) {
      error.value = parseContractError(e)
      throw e
    } finally {
      isSubmitting.value = false
    }
  }

  async function verifySolution(
    challenge: string,
    solution: Uint8Array,
    difficulty: bigint
  ): Promise<boolean> {
    const vc = verifierContract.value
    if (!vc) return false

    try {
      return await vc.verify_solution(challenge, solution, difficulty)
    } catch {
      return false
    }
  }

  async function getEpochData(epoch: bigint): Promise<EpochData | null> {
    const tc = tokenContract.value
    if (!tc) return null

    try {
      const data = await tc.epochs(epoch)
      return {
        blockNumber: data[0],
        totalReward: data[1],
        minerCount: data[2],
        claimedCount: data[3],
        timestamp: data[4]
      }
    } catch {
      return null
    }
  }

  async function checkClaimableEpochs() {
    const tc = tokenContract.value
    if (!tc || !walletStore.address) return

    const claimable: bigint[] = []

    // Check last 10 epochs for claimable rewards
    for (let i = currentEpoch.value - 1n; i >= 0n && i > currentEpoch.value - 10n; i--) {
      try {
        const hasClaimed = await tc.miner_claimed_epochs(
          walletStore.address,
          i
        )

        if (!hasClaimed) {
          // Check if user participated in this epoch
          const epochData = await getEpochData(i)
          if (epochData && epochData.minerCount > 0n) {
            claimable.push(i)
          }
        }
      } catch {
        continue
      }
    }

    claimableEpochs.value = claimable
  }

  function parseContractError(err: unknown): string {
    const message = err instanceof Error ? err.message : 'Unknown error'

    if (message.includes('Solution already used')) {
      return 'This solution has already been used. Generate a new one.'
    }
    if (message.includes('Invalid solution')) {
      return 'The solution is invalid. Please check your mining parameters.'
    }
    if (message.includes('Contract is paused')) {
      return 'Mining is currently paused by the contract owner.'
    }
    if (message.includes('Epoch not finished')) {
      return 'This epoch has not finished yet. Wait for the next epoch.'
    }
    if (message.includes('Already claimed')) {
      return 'You have already claimed rewards for this epoch.'
    }
    if (message.includes('Not a miner')) {
      return 'You did not participate in this epoch.'
    }

    return message
  }

  return {
    // State
    currentChallenge,
    currentDifficulty,
    currentEpoch,
    blocksMined,
    lastMiningTimestamp,
    isMining,
    hashRate,
    foundSolutions,
    claimableEpochs,
    userEpochHistory,
    isLoading,
    isSubmitting,
    error,

    // Contracts
    tokenContract,
    verifierContract,

    // Computed
    currentReward,
    nextHalvingBlocks,
    timeSinceLastMining,
    epochProgress,
    canMineNewEpoch,

    // Actions
    fetchMiningState,
    submitProof,
    submitProofBatch,
    claimReward,
    verifySolution,
    getEpochData,
    checkClaimableEpochs
  }
})

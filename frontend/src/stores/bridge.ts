import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { Contract, type InterfaceAbi } from 'ethers'
import { useWalletStore } from './wallet'
import { BRIDGE_ADDRESS, type ChainId } from '@/contracts/addresses'
import type { BridgeConfig, BridgeRequest, BridgeStats } from '@/types'
import type { BridgeContract } from '@/types/contracts'
import BridgeABI from '@/contracts/abis/EVMOREBridgeStage2.json'

export const useBridgeStore = defineStore('bridge', () => {
  const walletStore = useWalletStore()

  // State
  const isActive = ref(false)
  const config = ref<BridgeConfig>({
    minAmount: 0n,
    maxAmount: 0n,
    dailyLimit: 0n,
    withdrawalDelay: 0n,
    feeRate: 0n
  })

  // Statistics
  const stats = ref<BridgeStats>({
    totalBridgedToPolygon: 0n,
    totalBridgedFromPolygon: 0n,
    requestsCount: 0n,
    isActive: false
  })

  const dailyVolume = ref<bigint>(0n)
  const userDailyVolume = ref<bigint>(0n)

  // User requests
  const pendingRequests = ref<BridgeRequest[]>([])
  const completedRequests = ref<BridgeRequest[]>([])

  // Loading state
  const isLoading = ref(false)
  const isSubmitting = ref(false)
  const error = ref<string | null>(null)

  // Contract
  const contract = computed((): BridgeContract | null => {
    if (!walletStore.signer || !walletStore.chainId) return null

    const address = BRIDGE_ADDRESS[walletStore.chainId as ChainId]
    if (!address) return null

    return new Contract(address, BridgeABI as InterfaceAbi, walletStore.signer) as unknown as BridgeContract
  })

  // Computed
  const feePercentage = computed(() =>
    Number(config.value.feeRate) / 100
  )

  const remainingDailyLimit = computed(() =>
    config.value.dailyLimit - dailyVolume.value
  )

  const userRemainingDailyLimit = computed(() => {
    const userLimit = config.value.dailyLimit / 10n // 10% per user
    return userLimit - userDailyVolume.value
  })

  const isBridgeAvailable = computed(() =>
    !!contract.value && isActive.value
  )

  // Actions
  async function fetchBridgeState() {
    const c = contract.value
    if (!c) return

    isLoading.value = true
    error.value = null

    try {
      const [bridgeStats, bridgeConfig, active, volume, userVolume] = await Promise.all([
        c.getBridgeStats(),
        c.getBridgeConfig(),
        c.isBridgeActive(),
        c.getDailyVolume(),
        walletStore.address
          ? c.getUserDailyVolume(walletStore.address)
          : Promise.resolve(0n)
      ])

      stats.value = {
        totalBridgedToPolygon: bridgeStats[0],
        totalBridgedFromPolygon: bridgeStats[1],
        requestsCount: bridgeStats[2],
        isActive: bridgeStats[3]
      }

      config.value = {
        minAmount: bridgeConfig[0],
        maxAmount: bridgeConfig[1],
        dailyLimit: bridgeConfig[2],
        withdrawalDelay: bridgeConfig[3],
        feeRate: bridgeConfig[4]
      }

      isActive.value = active
      dailyVolume.value = volume
      userDailyVolume.value = userVolume
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Unknown error'
      console.error('Failed to fetch bridge state:', e)
    } finally {
      isLoading.value = false
    }
  }

  async function bridgeToPolygon(amount: bigint) {
    const c = contract.value
    if (!c) throw new Error('Bridge contract not initialized')

    isSubmitting.value = true
    error.value = null

    try {
      const tx = await c.bridgeToPolygon(amount)
      const receipt = await tx.wait()

      // Refresh state after bridge
      await fetchBridgeState()

      return { tx, receipt }
    } catch (e: unknown) {
      error.value = parseBridgeError(e)
      throw e
    } finally {
      isSubmitting.value = false
    }
  }

  async function fetchBridgeRequest(requestId: string): Promise<BridgeRequest | null> {
    const c = contract.value
    if (!c) return null

    try {
      const data = await c.getBridgeRequest(requestId)
      return {
        user: data[0],
        amount: data[1],
        timestamp: data[2],
        nonce: data[3],
        processed: data[4],
        direction: data[5] as 0 | 1
      }
    } catch {
      return null
    }
  }

  function calculateFee(amount: bigint): bigint {
    return (amount * config.value.feeRate) / 10000n
  }

  function calculateNetAmount(amount: bigint): bigint {
    return amount - calculateFee(amount)
  }

  function parseBridgeError(err: unknown): string {
    const message = err instanceof Error ? err.message : 'Unknown error'

    if (message.includes('Amount below minimum')) {
      return `Minimum bridge amount is ${config.value.minAmount} EVMORE`
    }
    if (message.includes('Amount exceeds maximum')) {
      return `Maximum bridge amount is ${config.value.maxAmount} EVMORE`
    }
    if (message.includes('Daily limit exceeded')) {
      return 'Daily bridge limit has been reached. Try again tomorrow.'
    }
    if (message.includes('Bridge is not active')) {
      return 'Bridge is currently inactive. Stage 2 requires 1K EVMORE treasury.'
    }
    if (message.includes('Insufficient balance')) {
      return 'Insufficient EVMORE balance for this bridge operation.'
    }

    return message
  }

  return {
    // State
    isActive,
    config,
    stats,
    dailyVolume,
    userDailyVolume,
    pendingRequests,
    completedRequests,
    isLoading,
    isSubmitting,
    error,
    contract,

    // Computed
    feePercentage,
    remainingDailyLimit,
    userRemainingDailyLimit,
    isBridgeAvailable,

    // Actions
    fetchBridgeState,
    bridgeToPolygon,
    fetchBridgeRequest,
    calculateFee,
    calculateNetAmount
  }
})

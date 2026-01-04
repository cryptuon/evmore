import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { Contract, formatUnits, type InterfaceAbi } from 'ethers'
import { useWalletStore } from './wallet'
import { EVMORE_TOKEN_ADDRESS, type ChainId } from '@/contracts/addresses'
import { EVMORE_CONSTANTS } from '@/types'
import type { EvmoreContract } from '@/types/contracts'
import EvmoreTokenABI from '@/contracts/abis/EvmoreToken.json'

export const useTokenStore = defineStore('token', () => {
  const walletStore = useWalletStore()

  // State
  const balance = ref<bigint>(0n)
  const totalSupply = ref<bigint>(0n)
  const allowances = ref<Map<string, bigint>>(new Map())
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Contract instance
  const contract = computed((): EvmoreContract | null => {
    if (!walletStore.signer || !walletStore.chainId) return null

    const address = EVMORE_TOKEN_ADDRESS[walletStore.chainId as ChainId]
    if (!address) return null

    return new Contract(address, EvmoreTokenABI as InterfaceAbi, walletStore.signer) as unknown as EvmoreContract
  })

  // Computed
  const formattedBalance = computed(() =>
    formatUnits(balance.value, EVMORE_CONSTANTS.DECIMALS)
  )

  const formattedTotalSupply = computed(() =>
    formatUnits(totalSupply.value, EVMORE_CONSTANTS.DECIMALS)
  )

  const supplyPercentage = computed(() => {
    if (EVMORE_CONSTANTS.MAX_SUPPLY === 0n) return 0
    return Number((totalSupply.value * 10000n) / EVMORE_CONSTANTS.MAX_SUPPLY) / 100
  })

  const remainingSupply = computed(() =>
    EVMORE_CONSTANTS.MAX_SUPPLY - totalSupply.value
  )

  const formattedMaxSupply = computed(() =>
    formatUnits(EVMORE_CONSTANTS.MAX_SUPPLY, EVMORE_CONSTANTS.DECIMALS)
  )

  // Actions
  async function fetchBalance() {
    const c = contract.value
    if (!c || !walletStore.address) return

    isLoading.value = true
    error.value = null

    try {
      balance.value = await c.balanceOf(walletStore.address)
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Unknown error'
      console.error('Failed to fetch balance:', e)
    } finally {
      isLoading.value = false
    }
  }

  async function fetchTotalSupply() {
    const c = contract.value
    if (!c) return

    try {
      totalSupply.value = await c.totalSupply()
    } catch (e: unknown) {
      console.error('Failed to fetch total supply:', e)
    }
  }

  async function getAllowance(spender: string): Promise<bigint> {
    const c = contract.value
    if (!c || !walletStore.address) return 0n

    try {
      const allowance = await c.allowance(walletStore.address, spender)
      allowances.value.set(spender, allowance)
      return allowance
    } catch (e) {
      console.error('Failed to fetch allowance:', e)
      return 0n
    }
  }

  async function transfer(to: string, amount: bigint) {
    const c = contract.value
    if (!c) throw new Error('Contract not initialized')

    isLoading.value = true
    error.value = null

    try {
      const tx = await c.transfer(to, amount)
      await tx.wait()

      // Refresh balance after transfer
      await fetchBalance()

      return tx
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Unknown error'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function approve(spender: string, amount: bigint) {
    const c = contract.value
    if (!c) throw new Error('Contract not initialized')

    isLoading.value = true
    error.value = null

    try {
      const tx = await c.approve(spender, amount)
      await tx.wait()

      // Update cached allowance
      allowances.value.set(spender, amount)

      return tx
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Unknown error'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function refreshAll() {
    await Promise.all([fetchBalance(), fetchTotalSupply()])
  }

  return {
    // State
    balance,
    totalSupply,
    allowances,
    isLoading,
    error,
    contract,

    // Computed
    formattedBalance,
    formattedTotalSupply,
    supplyPercentage,
    remainingSupply,
    formattedMaxSupply,

    // Constants
    MAX_SUPPLY: EVMORE_CONSTANTS.MAX_SUPPLY,
    INITIAL_REWARD: EVMORE_CONSTANTS.INITIAL_REWARD,
    HALVING_BLOCKS: EVMORE_CONSTANTS.HALVING_BLOCKS,

    // Actions
    fetchBalance,
    fetchTotalSupply,
    getAllowance,
    transfer,
    approve,
    refreshAll
  }
})

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { BrowserProvider, JsonRpcSigner, formatEther } from 'ethers'
import { CHAIN_IDS, CHAIN_NAMES, isSupportedChain, type ChainId } from '@/contracts/addresses'

declare global {
  interface Window {
    ethereum?: any
  }
}

export const useWalletStore = defineStore('wallet', () => {
  // State
  const address = ref<string | null>(null)
  const chainId = ref<number | null>(null)
  const isConnected = ref(false)
  const isConnecting = ref(false)
  const provider = ref<BrowserProvider | null>(null)
  const signer = ref<JsonRpcSigner | null>(null)
  const ethBalance = ref<bigint>(0n)
  const error = ref<string | null>(null)

  // Computed
  const shortAddress = computed(() => {
    if (!address.value) return ''
    return `${address.value.slice(0, 6)}...${address.value.slice(-4)}`
  })

  const formattedBalance = computed(() => formatEther(ethBalance.value))

  const chainName = computed(() => {
    if (!chainId.value) return ''
    return CHAIN_NAMES[chainId.value as ChainId] || `Chain ${chainId.value}`
  })

  const isEthereumMainnet = computed(() => chainId.value === CHAIN_IDS.ETHEREUM_MAINNET)
  const isPolygon = computed(() => chainId.value === CHAIN_IDS.POLYGON_MAINNET)
  const isSupportedNetwork = computed(() => chainId.value ? isSupportedChain(chainId.value) : false)

  const hasMetaMask = computed(() => typeof window !== 'undefined' && !!window.ethereum)

  // Actions
  async function connect() {
    if (!window.ethereum) {
      error.value = 'MetaMask not detected. Please install MetaMask.'
      return false
    }

    isConnecting.value = true
    error.value = null

    try {
      provider.value = new BrowserProvider(window.ethereum)

      // Request accounts
      const accounts = await provider.value.send('eth_requestAccounts', [])
      if (accounts.length === 0) {
        throw new Error('No accounts found')
      }

      address.value = accounts[0]
      signer.value = await provider.value.getSigner()

      // Get chain ID
      const network = await provider.value.getNetwork()
      chainId.value = Number(network.chainId)

      // Get balance
      await refreshBalance()

      isConnected.value = true

      // Set up event listeners
      setupEventListeners()

      return true
    } catch (e: any) {
      error.value = e.message || 'Failed to connect wallet'
      return false
    } finally {
      isConnecting.value = false
    }
  }

  async function disconnect() {
    address.value = null
    chainId.value = null
    isConnected.value = false
    provider.value = null
    signer.value = null
    ethBalance.value = 0n
    error.value = null

    removeEventListeners()
  }

  async function switchNetwork(targetChainId: ChainId) {
    if (!window.ethereum) return false

    const chainIdHex = `0x${targetChainId.toString(16)}`

    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: chainIdHex }]
      })
      return true
    } catch (e: any) {
      // Chain not added, try to add it
      if (e.code === 4902) {
        error.value = 'Network not found. Please add it manually.'
      } else {
        error.value = e.message || 'Failed to switch network'
      }
      return false
    }
  }

  async function refreshBalance() {
    if (!provider.value || !address.value) return

    try {
      ethBalance.value = await provider.value.getBalance(address.value)
    } catch (e) {
      console.error('Failed to fetch balance:', e)
    }
  }

  function setupEventListeners() {
    if (!window.ethereum) return

    window.ethereum.on('accountsChanged', handleAccountsChanged)
    window.ethereum.on('chainChanged', handleChainChanged)
  }

  function removeEventListeners() {
    if (!window.ethereum) return

    window.ethereum.removeListener('accountsChanged', handleAccountsChanged)
    window.ethereum.removeListener('chainChanged', handleChainChanged)
  }

  function handleAccountsChanged(accounts: string[]) {
    if (accounts.length === 0) {
      disconnect()
    } else {
      address.value = accounts[0] ?? null
      refreshBalance()
    }
  }

  function handleChainChanged(newChainId: string) {
    chainId.value = parseInt(newChainId, 16)
    refreshBalance()
  }

  return {
    // State
    address,
    chainId,
    isConnected,
    isConnecting,
    provider,
    signer,
    ethBalance,
    error,

    // Computed
    shortAddress,
    formattedBalance,
    chainName,
    isEthereumMainnet,
    isPolygon,
    isSupportedNetwork,
    hasMetaMask,

    // Actions
    connect,
    disconnect,
    switchNetwork,
    refreshBalance
  }
})

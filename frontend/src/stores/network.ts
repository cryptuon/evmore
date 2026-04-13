import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { api, type ApiChain, type ApiOverview, type ApiPrice } from '@/api/client'

const STORAGE_KEY = 'evmore.selectedChain'

export const useNetworkStore = defineStore('network', () => {
  const chains = ref<ApiChain[]>([])
  const selectedKey = ref<string>(localStorage.getItem(STORAGE_KEY) ?? 'mainnet')
  const overview = ref<ApiOverview | null>(null)
  const price = ref<ApiPrice | null>(null)
  const isLoadingConfig = ref(false)
  const isLoadingOverview = ref(false)
  const error = ref<string | null>(null)

  let pollTimer: number | null = null

  const selectedChain = computed<ApiChain | null>(() => {
    return chains.value.find((c) => c.key === selectedKey.value) ?? chains.value[0] ?? null
  })

  const availableKeys = computed(() => chains.value.map((c) => c.key))

  async function loadConfig() {
    if (isLoadingConfig.value) return
    isLoadingConfig.value = true
    error.value = null
    try {
      const cfg = await api.config()
      chains.value = cfg.chains
      if (!chains.value.find((c) => c.key === selectedKey.value) && chains.value.length) {
        selectedKey.value = chains.value[0].key
      }
    } catch (e: any) {
      error.value = e.message ?? 'failed to load config'
    } finally {
      isLoadingConfig.value = false
    }
  }

  async function refreshOverview() {
    if (!selectedChain.value) return
    isLoadingOverview.value = true
    try {
      overview.value = await api.overview(selectedChain.value.key)
    } catch (e: any) {
      error.value = e.message ?? 'failed to load overview'
    } finally {
      isLoadingOverview.value = false
    }
  }

  async function refreshPrice() {
    try {
      price.value = await api.price()
    } catch (e) {
      console.warn('price fetch failed', e)
    }
  }

  async function setChain(key: string) {
    selectedKey.value = key
    localStorage.setItem(STORAGE_KEY, key)
    await refreshOverview()
  }

  function startPolling(intervalMs = 15000) {
    stopPolling()
    refreshOverview()
    refreshPrice()
    pollTimer = window.setInterval(() => {
      refreshOverview()
      refreshPrice()
    }, intervalMs)
  }

  function stopPolling() {
    if (pollTimer !== null) {
      window.clearInterval(pollTimer)
      pollTimer = null
    }
  }

  return {
    chains,
    selectedKey,
    selectedChain,
    availableKeys,
    overview,
    price,
    isLoadingConfig,
    isLoadingOverview,
    error,
    loadConfig,
    refreshOverview,
    refreshPrice,
    setChain,
    startPolling,
    stopPolling
  }
})

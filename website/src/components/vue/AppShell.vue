<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useWalletStore } from '@/stores/wallet'
import { useNetworkStore } from '@/stores/network'
import { storeToRefs } from 'pinia'

const walletStore = useWalletStore()
const networkStore = useNetworkStore()
const { isConnected, shortAddress, chainName, isSupportedNetwork, isConnecting } = storeToRefs(walletStore)
const { chains, selectedKey } = storeToRefs(networkStore)

const isMobileMenuOpen = ref(false)

const navLinks = [
  { name: 'Dashboard', path: '/app/dashboard/' },
  { name: 'Mining', path: '/app/mining/' },
  { name: 'Wallet', path: '/app/wallet/' },
  { name: 'Bridge', path: '/app/bridge/' },
  { name: 'Stats', path: '/app/stats/' },
]

const currentPath = ref(typeof window !== 'undefined' ? window.location.pathname : '')

function isActive(path: string): boolean {
  return currentPath.value === path || currentPath.value === path.replace(/\/$/, '')
}

async function connectWallet() {
  await walletStore.connect()
}

function disconnectWallet() {
  walletStore.disconnect()
}

async function handleChainChange(e: Event) {
  const key = (e.target as HTMLSelectElement).value
  await networkStore.setChain(key)
  const target = networkStore.selectedChain
  if (walletStore.isConnected && target) {
    await walletStore.switchNetwork(target.chain_id as any)
  }
}

onMounted(async () => {
  await networkStore.loadConfig()
  networkStore.startPolling()

  // Auto-reconnect if MetaMask has an active session
  if (window.ethereum?.selectedAddress) {
    await walletStore.connect()
  }
})
</script>

<template>
  <div class="min-h-screen">
    <header class="sticky top-0 z-40 bg-white/80 dark:bg-evmore-dark/80 backdrop-blur-lg border-b border-gray-200 dark:border-gray-800">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center gap-6">
            <a href="/" class="flex items-center gap-2">
              <div class="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
                <span class="text-lg font-bold text-gray-900">E</span>
              </div>
              <span class="text-xl font-bold text-gray-900 dark:text-white">EVMORE</span>
            </a>

            <nav class="hidden md:flex items-center gap-1">
              <a
                v-for="link in navLinks"
                :key="link.path"
                :href="link.path"
                :class="[
                  'px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                  isActive(link.path)
                    ? 'text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/20'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-800'
                ]"
              >
                {{ link.name }}
              </a>
            </nav>
          </div>

          <div class="flex items-center gap-3">
            <div v-if="chains.length" class="hidden sm:flex items-center">
              <select
                :value="selectedKey"
                @change="handleChainChange"
                class="text-xs font-medium rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 px-2 py-1.5 focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <option v-for="c in chains" :key="c.key" :value="c.key">
                  {{ c.name }}{{ c.is_testnet ? ' (test)' : '' }}
                </option>
              </select>
            </div>

            <div v-if="isConnected" class="hidden sm:flex items-center gap-2">
              <span
                :class="[
                  'text-xs font-medium px-2 py-1 rounded-full',
                  isSupportedNetwork
                    ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300'
                    : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300'
                ]"
              >
                {{ chainName }}
              </span>
              <div class="relative group">
                <button class="flex items-center gap-2 px-3 py-1.5 bg-gray-100 dark:bg-gray-800 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors">
                  <span class="w-2 h-2 bg-green-500 rounded-full" />
                  {{ shortAddress }}
                </button>
                <div class="absolute right-0 mt-2 w-48 py-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                  <button class="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-gray-100 dark:hover:bg-gray-700" @click="disconnectWallet">
                    Disconnect
                  </button>
                </div>
              </div>
            </div>
            <button
              v-else
              class="btn-primary text-sm px-4 py-2"
              :disabled="isConnecting"
              @click="connectWallet"
            >
              {{ isConnecting ? 'Connecting...' : 'Connect Wallet' }}
            </button>
          </div>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div v-if="!isConnected" class="text-center py-20">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">Connect Your Wallet</h2>
        <p class="text-gray-600 dark:text-gray-400 mb-6">Connect MetaMask to access the dashboard.</p>
        <button class="btn-primary text-base px-6 py-3" :disabled="isConnecting" @click="connectWallet">
          {{ isConnecting ? 'Connecting...' : 'Connect Wallet' }}
        </button>
      </div>
      <slot v-else />
    </main>
  </div>
</template>

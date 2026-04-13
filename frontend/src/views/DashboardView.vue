<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useWalletStore } from '@/stores/wallet'
import { useTokenStore } from '@/stores/token'
import { useMiningStore } from '@/stores/mining'
import { useNetworkStore } from '@/stores/network'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseBadge from '@/components/common/BaseBadge.vue'
import BaseSpinner from '@/components/common/BaseSpinner.vue'
import { formatTokenAmount, formatBlocks } from '@/utils/formatters'

const walletStore = useWalletStore()
const tokenStore = useTokenStore()
const miningStore = useMiningStore()
const networkStore = useNetworkStore()

const { isConnected, shortAddress, formattedBalance: ethBalance } = storeToRefs(walletStore)
const { overview, price, selectedChain, isLoadingOverview } = storeToRefs(networkStore)

const supplyPct = computed(() => overview.value?.circulating_percent ?? 0)

function fmtWei(wei: string | undefined, digits = 2): string {
  if (!wei) return '0'
  try {
    const v = BigInt(wei)
    const whole = v / 10n ** 18n
    const frac = (v % 10n ** 18n) / 10n ** BigInt(18 - digits)
    return `${whole}.${frac.toString().padStart(digits, '0')}`
  } catch {
    return '0'
  }
}

function fmtDuration(s: number | undefined): string {
  if (!s && s !== 0) return '—'
  if (s < 60) return `${s}s ago`
  if (s < 3600) return `${Math.floor(s / 60)}m ago`
  if (s < 86400) return `${Math.floor(s / 3600)}h ago`
  return `${Math.floor(s / 86400)}d ago`
}

function fmtUsd(n: number | null | undefined): string {
  if (n == null) return '—'
  return `$${n.toLocaleString(undefined, { maximumFractionDigits: 2 })}`
}
const { balance, totalSupply, supplyPercentage, isLoading: tokenLoading } = storeToRefs(tokenStore)
const {
  currentEpoch,
  blocksMined,
  currentDifficulty,
  currentReward,
  nextHalvingBlocks,
  epochProgress,
  isLoading: miningLoading
} = storeToRefs(miningStore)

// Fetch data when wallet connects
watch(isConnected, async (connected) => {
  if (connected) {
    await Promise.all([
      tokenStore.refreshAll(),
      miningStore.fetchMiningState()
    ])
  }
})

onMounted(async () => {
  if (isConnected.value) {
    await Promise.all([
      tokenStore.refreshAll(),
      miningStore.fetchMiningState()
    ])
  }
})
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
      <BaseBadge v-if="selectedChain" :variant="selectedChain.is_testnet ? 'warning' : 'success'">
        {{ selectedChain.name }}
      </BaseBadge>
    </div>

    <!-- Network Overview (public, fed by backend) -->
    <BaseCard>
      <template #header>
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Network Overview</h2>
          <BaseSpinner v-if="isLoadingOverview" size="sm" />
        </div>
      </template>
      <div v-if="overview" class="grid grid-cols-2 md:grid-cols-4 gap-6">
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Total Supply</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">{{ fmtWei(overview.total_supply) }}</p>
          <p class="text-xs text-gray-400 mt-1">{{ supplyPct.toFixed(4) }}% of 21M</p>
        </div>
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Blocks Mined</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">{{ overview.blocks_mined }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Difficulty</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">{{ overview.current_difficulty }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Block Reward</p>
          <p class="text-2xl font-bold text-primary-600 dark:text-primary-400 mt-1">{{ fmtWei(overview.current_reward) }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Last Block</p>
          <p class="text-lg font-semibold text-gray-900 dark:text-white mt-1">{{ fmtDuration(overview.seconds_since_last_block) }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Next Halving</p>
          <p class="text-lg font-semibold text-gray-900 dark:text-white mt-1">{{ overview.blocks_until_halving }} blocks</p>
        </div>
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">ETH Price</p>
          <p class="text-lg font-semibold text-gray-900 dark:text-white mt-1">{{ fmtUsd(price?.eth_usd) }}</p>
          <p v-if="price?.eth_usd_24h_change != null" class="text-xs mt-0.5" :class="price.eth_usd_24h_change >= 0 ? 'text-green-500' : 'text-red-500'">
            {{ price.eth_usd_24h_change.toFixed(2) }}% 24h
          </p>
        </div>
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Latest Block</p>
          <p class="text-lg font-semibold text-gray-900 dark:text-white mt-1">#{{ overview.latest_block }}</p>
        </div>
      </div>
      <div v-else class="py-8 text-center text-gray-500 dark:text-gray-400">
        Loading network data…
      </div>
    </BaseCard>

    <!-- Wallet Overview -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <BaseCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Wallet Address</p>
            <p class="text-lg font-mono text-gray-900 dark:text-white mt-1">
              {{ shortAddress }}
            </p>
          </div>
          <div class="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
            <span class="w-3 h-3 bg-green-500 rounded-full" />
          </div>
        </div>
      </BaseCard>

      <BaseCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">ETH Balance</p>
            <p class="text-lg font-mono text-gray-900 dark:text-white mt-1">
              {{ ethBalance }} ETH
            </p>
          </div>
          <div class="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
            <span class="text-xl">&#9830;</span>
          </div>
        </div>
      </BaseCard>

      <BaseCard>
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">EVMORE Balance</p>
            <p class="text-lg font-mono text-primary-600 dark:text-primary-400 mt-1">
              <BaseSpinner v-if="tokenLoading" size="sm" />
              <span v-else>{{ formatTokenAmount(balance) }} EVMORE</span>
            </p>
          </div>
          <div class="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
            <span class="text-xl font-bold text-primary-600">E</span>
          </div>
        </div>
      </BaseCard>
    </div>

    <!-- Mining Overview -->
    <BaseCard>
      <template #header>
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
            Mining Overview
          </h2>
          <BaseBadge variant="info">
            Epoch {{ currentEpoch?.toString() || '0' }}
          </BaseBadge>
        </div>
      </template>

      <div v-if="miningLoading" class="py-8">
        <BaseSpinner />
      </div>

      <div v-else class="grid grid-cols-2 md:grid-cols-4 gap-6">
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Blocks Mined</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">
            {{ formatBlocks(blocksMined) }}
          </p>
        </div>

        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Current Difficulty</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">
            {{ currentDifficulty?.toString() || '0' }}
          </p>
        </div>

        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Block Reward</p>
          <p class="text-2xl font-bold text-primary-600 dark:text-primary-400 mt-1">
            {{ formatTokenAmount(currentReward) }}
          </p>
        </div>

        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Next Halving</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">
            {{ formatBlocks(nextHalvingBlocks) }} blocks
          </p>
        </div>
      </div>

      <!-- Epoch Progress Bar -->
      <div class="mt-6">
        <div class="flex items-center justify-between text-sm mb-2">
          <span class="text-gray-500 dark:text-gray-400">Epoch Progress</span>
          <span class="text-gray-900 dark:text-white">{{ epochProgress.toFixed(0) }}%</span>
        </div>
        <div class="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div
            class="h-full bg-primary-500 rounded-full transition-all duration-500"
            :style="{ width: `${epochProgress}%` }"
          />
        </div>
      </div>
    </BaseCard>

    <!-- Supply Overview -->
    <BaseCard>
      <template #header>
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
          Supply Overview
        </h2>
      </template>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Total Supply</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">
            {{ formatTokenAmount(totalSupply) }}
          </p>
        </div>

        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Max Supply</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">
            21,000,000
          </p>
        </div>

        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Circulation</p>
          <p class="text-2xl font-bold text-primary-600 dark:text-primary-400 mt-1">
            {{ supplyPercentage.toFixed(4) }}%
          </p>
        </div>
      </div>

      <!-- Supply Progress Bar -->
      <div class="mt-6">
        <div class="flex items-center justify-between text-sm mb-2">
          <span class="text-gray-500 dark:text-gray-400">Supply Mined</span>
          <span class="text-gray-900 dark:text-white">{{ supplyPercentage.toFixed(4) }}%</span>
        </div>
        <div class="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div
            class="h-full bg-gradient-to-r from-primary-400 to-primary-600 rounded-full transition-all duration-500"
            :style="{ width: `${supplyPercentage}%` }"
          />
        </div>
      </div>
    </BaseCard>
  </div>
</template>

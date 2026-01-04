<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useWalletStore } from '@/stores/wallet'
import { useTokenStore } from '@/stores/token'
import { useMiningStore } from '@/stores/mining'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseBadge from '@/components/common/BaseBadge.vue'
import BaseSpinner from '@/components/common/BaseSpinner.vue'
import { formatTokenAmount, formatBlocks } from '@/utils/formatters'

const walletStore = useWalletStore()
const tokenStore = useTokenStore()
const miningStore = useMiningStore()

const { isConnected, shortAddress, formattedBalance: ethBalance } = storeToRefs(walletStore)
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
    <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
      Dashboard
    </h1>

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

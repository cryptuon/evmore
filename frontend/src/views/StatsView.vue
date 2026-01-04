<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useTokenStore } from '@/stores/token'
import { useMiningStore } from '@/stores/mining'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseSpinner from '@/components/common/BaseSpinner.vue'
import { formatTokenAmount, formatDuration, formatBlocks, formatPercentage } from '@/utils/formatters'
import { EVMORE_CONSTANTS } from '@/types'

const tokenStore = useTokenStore()
const miningStore = useMiningStore()

const { totalSupply, supplyPercentage } = storeToRefs(tokenStore)
const {
  currentEpoch,
  blocksMined,
  currentDifficulty,
  currentReward,
  nextHalvingBlocks
} = storeToRefs(miningStore)

const isInitialLoading = ref(true)

onMounted(async () => {
  await Promise.all([
    tokenStore.fetchTotalSupply(),
    miningStore.fetchMiningState()
  ])
  isInitialLoading.value = false
})

// Calculate halving number
function getHalvingNumber(blocks: bigint): number {
  return Number(blocks / BigInt(EVMORE_CONSTANTS.HALVING_BLOCKS))
}

// Calculate estimated time to next halving
function getTimeToHalving(blocksRemaining: bigint): string {
  const seconds = Number(blocksRemaining) * EVMORE_CONSTANTS.TARGET_BLOCK_TIME
  return formatDuration(seconds)
}
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
      Network Statistics
    </h1>

    <div v-if="isInitialLoading" class="py-12">
      <BaseSpinner size="lg" />
    </div>

    <template v-else>
      <!-- Supply Stats -->
      <BaseCard>
        <template #header>
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
            Token Supply
          </h2>
        </template>

        <div class="space-y-6">
          <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
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
              <p class="text-sm text-gray-500 dark:text-gray-400">Circulating %</p>
              <p class="text-2xl font-bold text-primary-600 dark:text-primary-400 mt-1">
                {{ formatPercentage(supplyPercentage, 4) }}
              </p>
            </div>

            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Remaining</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                {{ formatTokenAmount(EVMORE_CONSTANTS.MAX_SUPPLY - totalSupply) }}
              </p>
            </div>
          </div>

          <!-- Supply Progress -->
          <div>
            <div class="flex items-center justify-between text-sm mb-2">
              <span class="text-gray-500 dark:text-gray-400">Supply Progress</span>
              <span class="text-gray-900 dark:text-white">{{ formatPercentage(supplyPercentage, 4) }}</span>
            </div>
            <div class="w-full h-4 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                class="h-full bg-gradient-to-r from-primary-400 to-primary-600 rounded-full transition-all duration-500"
                :style="{ width: `${Math.max(supplyPercentage, 0.1)}%` }"
              />
            </div>
          </div>
        </div>
      </BaseCard>

      <!-- Mining Stats -->
      <BaseCard>
        <template #header>
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
            Mining Statistics
          </h2>
        </template>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Current Epoch</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">
              {{ currentEpoch?.toString() || '0' }}
            </p>
          </div>

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
              {{ formatTokenAmount(currentReward) }} EVMORE
            </p>
          </div>
        </div>
      </BaseCard>

      <!-- Halving Info -->
      <BaseCard>
        <template #header>
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
            Halving Schedule
          </h2>
        </template>

        <div class="space-y-6">
          <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Current Halving</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                #{{ getHalvingNumber(blocksMined) }}
              </p>
            </div>

            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Blocks Until Next</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                {{ formatBlocks(nextHalvingBlocks) }}
              </p>
            </div>

            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Est. Time to Halving</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                {{ getTimeToHalving(nextHalvingBlocks) }}
              </p>
            </div>

            <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">Halving Interval</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                {{ EVMORE_CONSTANTS.HALVING_BLOCKS.toLocaleString() }} blocks
              </p>
            </div>
          </div>

          <!-- Halving Progress -->
          <div>
            <div class="flex items-center justify-between text-sm mb-2">
              <span class="text-gray-500 dark:text-gray-400">Progress to Next Halving</span>
              <span class="text-gray-900 dark:text-white">
                {{ formatBlocks(blocksMined % BigInt(EVMORE_CONSTANTS.HALVING_BLOCKS)) }} / {{ EVMORE_CONSTANTS.HALVING_BLOCKS.toLocaleString() }}
              </span>
            </div>
            <div class="w-full h-3 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div
                class="h-full bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full transition-all duration-500"
                :style="{ width: `${(Number(blocksMined % BigInt(EVMORE_CONSTANTS.HALVING_BLOCKS)) / EVMORE_CONSTANTS.HALVING_BLOCKS) * 100}%` }"
              />
            </div>
          </div>
        </div>
      </BaseCard>

      <!-- Token Economics -->
      <BaseCard>
        <template #header>
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
            Token Economics
          </h2>
        </template>

        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead>
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Halving
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Block Range
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Block Reward
                </th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Supply Added
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr
                v-for="i in 10"
                :key="i"
                :class="getHalvingNumber(blocksMined) === i - 1 ? 'bg-primary-50 dark:bg-primary-900/20' : ''"
              >
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                  {{ i - 1 }}
                  <span v-if="getHalvingNumber(blocksMined) === i - 1" class="ml-2 text-xs text-primary-600 dark:text-primary-400">
                    (Current)
                  </span>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                  {{ ((i - 1) * EVMORE_CONSTANTS.HALVING_BLOCKS).toLocaleString() }} - {{ (i * EVMORE_CONSTANTS.HALVING_BLOCKS - 1).toLocaleString() }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                  {{ (50 / Math.pow(2, i - 1)).toFixed(8) }} EVMORE
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">
                  {{ ((50 * EVMORE_CONSTANTS.HALVING_BLOCKS) / Math.pow(2, i - 1)).toLocaleString() }} EVMORE
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </BaseCard>
    </template>
  </div>
</template>

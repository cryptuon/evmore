<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useMiningStore } from '@/stores/mining'
import { useNotificationsStore } from '@/stores/notifications'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseBadge from '@/components/common/BaseBadge.vue'
import BaseSpinner from '@/components/common/BaseSpinner.vue'
import { formatTokenAmount, formatHash, formatDuration, formatBlocks } from '@/utils/formatters'
import { EVMORE_CONSTANTS } from '@/types'

const miningStore = useMiningStore()
const notificationsStore = useNotificationsStore()

const {
  currentChallenge,
  currentDifficulty,
  currentEpoch,
  blocksMined,
  currentReward,
  nextHalvingBlocks,
  epochProgress,
  timeSinceLastMining,
  canMineNewEpoch,
  claimableEpochs,
  isLoading,
  isSubmitting
} = storeToRefs(miningStore)

// Polling interval
let pollInterval: ReturnType<typeof setInterval> | null = null

onMounted(async () => {
  await miningStore.fetchMiningState()
  await miningStore.checkClaimableEpochs()

  // Poll every 30 seconds
  pollInterval = setInterval(async () => {
    await miningStore.fetchMiningState()
  }, 30000)
})

onUnmounted(() => {
  if (pollInterval) {
    clearInterval(pollInterval)
  }
})

async function handleClaimReward(epoch: bigint) {
  try {
    await miningStore.claimReward(epoch)
    notificationsStore.success('Reward Claimed', `Successfully claimed reward for epoch ${epoch}`)
  } catch (e: any) {
    notificationsStore.error('Claim Failed', e.message)
  }
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
        Mining
      </h1>
      <BaseBadge variant="info">
        Epoch {{ currentEpoch?.toString() || '0' }}
      </BaseBadge>
    </div>

    <!-- Mining Status -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <BaseCard>
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Current Challenge</p>
          <p class="text-lg font-mono text-gray-900 dark:text-white mt-1 break-all">
            <BaseSpinner v-if="isLoading" size="sm" />
            <span v-else>{{ formatHash(currentChallenge, 12) }}</span>
          </p>
        </div>
      </BaseCard>

      <BaseCard>
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Current Difficulty</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">
            {{ currentDifficulty?.toString() || '0' }}
          </p>
        </div>
      </BaseCard>

      <BaseCard>
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Block Reward</p>
          <p class="text-2xl font-bold text-primary-600 dark:text-primary-400 mt-1">
            {{ formatTokenAmount(currentReward) }} EVMORE
          </p>
        </div>
      </BaseCard>

      <BaseCard>
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Blocks Mined</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">
            {{ formatBlocks(blocksMined) }}
          </p>
        </div>
      </BaseCard>
    </div>

    <!-- Epoch Progress -->
    <BaseCard>
      <template #header>
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
          Epoch Progress
        </h2>
      </template>

      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <span class="text-gray-600 dark:text-gray-400">Time Elapsed</span>
          <span class="font-mono text-gray-900 dark:text-white">
            {{ formatDuration(Number(timeSinceLastMining)) }} / {{ formatDuration(EVMORE_CONSTANTS.TARGET_BLOCK_TIME) }}
          </span>
        </div>

        <div class="w-full h-4 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
          <div
            :class="[
              'h-full rounded-full transition-all duration-500',
              canMineNewEpoch ? 'bg-green-500' : 'bg-primary-500'
            ]"
            :style="{ width: `${epochProgress}%` }"
          />
        </div>

        <div class="flex items-center justify-between">
          <BaseBadge :variant="canMineNewEpoch ? 'success' : 'neutral'">
            {{ canMineNewEpoch ? 'Ready for new epoch' : 'Epoch in progress' }}
          </BaseBadge>
          <span class="text-sm text-gray-500 dark:text-gray-400">
            {{ epochProgress.toFixed(1) }}% complete
          </span>
        </div>
      </div>
    </BaseCard>

    <!-- Mining Info -->
    <BaseCard>
      <template #header>
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
          How to Mine EVMORE
        </h2>
      </template>

      <div class="prose dark:prose-invert max-w-none">
        <p class="text-gray-600 dark:text-gray-400">
          EVMORE uses KeccakCollision proof-of-work mining. To mine:
        </p>
        <ol class="list-decimal list-inside space-y-2 text-gray-600 dark:text-gray-400">
          <li>Get the current challenge from the contract</li>
          <li>Find 4 values that create a keccak256 collision with matching N-bit patterns</li>
          <li>Submit your solution to earn rewards</li>
          <li>Claim your rewards after the epoch ends</li>
        </ol>
        <p class="text-gray-600 dark:text-gray-400 mt-4">
          Use a mining client or script to generate valid solutions. Check the
          <a href="https://github.com" target="_blank" class="text-primary-600 dark:text-primary-400 hover:underline">
            documentation
          </a>
          for mining software.
        </p>
      </div>
    </BaseCard>

    <!-- Claimable Rewards -->
    <BaseCard>
      <template #header>
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
            Claimable Rewards
          </h2>
          <BaseBadge v-if="claimableEpochs.length > 0" variant="success">
            {{ claimableEpochs.length }} available
          </BaseBadge>
        </div>
      </template>

      <div v-if="claimableEpochs.length > 0" class="space-y-3">
        <div
          v-for="epoch in claimableEpochs"
          :key="epoch.toString()"
          class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg"
        >
          <div>
            <span class="font-medium text-gray-900 dark:text-white">
              Epoch {{ epoch.toString() }}
            </span>
          </div>
          <BaseButton
            variant="primary"
            size="sm"
            :loading="isSubmitting"
            @click="handleClaimReward(epoch)"
          >
            Claim Reward
          </BaseButton>
        </div>
      </div>

      <div v-else class="text-center py-8">
        <p class="text-gray-500 dark:text-gray-400">
          No rewards to claim. Start mining to earn EVMORE!
        </p>
      </div>
    </BaseCard>

    <!-- Halving Schedule -->
    <BaseCard>
      <template #header>
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
          Halving Schedule
        </h2>
      </template>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Current Reward</p>
          <p class="text-xl font-bold text-primary-600 dark:text-primary-400 mt-1">
            {{ formatTokenAmount(currentReward) }}
          </p>
        </div>

        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Next Halving In</p>
          <p class="text-xl font-bold text-gray-900 dark:text-white mt-1">
            {{ formatBlocks(nextHalvingBlocks) }} blocks
          </p>
        </div>

        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Halving Interval</p>
          <p class="text-xl font-bold text-gray-900 dark:text-white mt-1">
            {{ EVMORE_CONSTANTS.HALVING_BLOCKS.toLocaleString() }}
          </p>
        </div>

        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Target Block Time</p>
          <p class="text-xl font-bold text-gray-900 dark:text-white mt-1">
            {{ formatDuration(EVMORE_CONSTANTS.TARGET_BLOCK_TIME) }}
          </p>
        </div>
      </div>
    </BaseCard>
  </div>
</template>

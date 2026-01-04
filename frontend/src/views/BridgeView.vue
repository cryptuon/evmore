<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useWalletStore } from '@/stores/wallet'
import { useTokenStore } from '@/stores/token'
import { useBridgeStore } from '@/stores/bridge'
import { useNotificationsStore } from '@/stores/notifications'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseBadge from '@/components/common/BaseBadge.vue'
import BaseSpinner from '@/components/common/BaseSpinner.vue'
import { formatTokenAmount, parseTokenAmount } from '@/utils/formatters'

const walletStore = useWalletStore()
const tokenStore = useTokenStore()
const bridgeStore = useBridgeStore()
const notificationsStore = useNotificationsStore()

const { isConnected } = storeToRefs(walletStore)
const { balance } = storeToRefs(tokenStore)
const {
  isActive,
  config,
  stats,
  feePercentage,
  remainingDailyLimit,
  userRemainingDailyLimit,
  isLoading,
  isSubmitting
} = storeToRefs(bridgeStore)

// Bridge form
const bridgeAmount = ref('')
const bridgeError = ref('')

// Computed
const fee = computed(() => {
  const amount = parseTokenAmount(bridgeAmount.value)
  return bridgeStore.calculateFee(amount)
})

const netAmount = computed(() => {
  const amount = parseTokenAmount(bridgeAmount.value)
  return bridgeStore.calculateNetAmount(amount)
})

// Fetch data
watch(isConnected, async (connected) => {
  if (connected) {
    await Promise.all([
      tokenStore.fetchBalance(),
      bridgeStore.fetchBridgeState()
    ])
  }
})

onMounted(async () => {
  if (isConnected.value) {
    await Promise.all([
      tokenStore.fetchBalance(),
      bridgeStore.fetchBridgeState()
    ])
  }
})

async function handleBridge() {
  if (!bridgeAmount.value) {
    bridgeError.value = 'Please enter an amount'
    return
  }

  const amount = parseTokenAmount(bridgeAmount.value)
  if (amount === 0n) {
    bridgeError.value = 'Invalid amount'
    return
  }

  if (amount < config.value.minAmount) {
    bridgeError.value = `Minimum amount is ${formatTokenAmount(config.value.minAmount)} EVMORE`
    return
  }

  if (amount > config.value.maxAmount) {
    bridgeError.value = `Maximum amount is ${formatTokenAmount(config.value.maxAmount)} EVMORE`
    return
  }

  if (amount > balance.value) {
    bridgeError.value = 'Insufficient balance'
    return
  }

  bridgeError.value = ''

  try {
    await bridgeStore.bridgeToPolygon(amount)
    notificationsStore.success(
      'Bridge Initiated',
      `Bridging ${bridgeAmount.value} EVMORE to Polygon`
    )
    bridgeAmount.value = ''
  } catch (e: any) {
    bridgeError.value = e.message
    notificationsStore.error('Bridge Failed', e.message)
  }
}

function setMaxAmount() {
  bridgeAmount.value = formatTokenAmount(balance.value, 18, 18)
}
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
        Bridge
      </h1>
      <BaseBadge :variant="isActive ? 'success' : 'warning'">
        {{ isActive ? 'Active' : 'Inactive' }}
      </BaseBadge>
    </div>

    <!-- Bridge Status Alert -->
    <div
      v-if="!isActive"
      class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4"
    >
      <div class="flex items-start gap-3">
        <svg class="h-5 w-5 text-yellow-500 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
        <div>
          <h3 class="text-sm font-medium text-yellow-800 dark:text-yellow-200">
            Bridge Inactive
          </h3>
          <p class="mt-1 text-sm text-yellow-700 dark:text-yellow-300">
            The EVMORE bridge is currently inactive. Stage 2 activation requires 1,000 EVMORE in the treasury.
          </p>
        </div>
      </div>
    </div>

    <!-- Bridge Statistics -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
      <BaseCard>
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Bridged to Polygon</p>
          <p class="text-xl font-bold text-gray-900 dark:text-white mt-1">
            <BaseSpinner v-if="isLoading" size="sm" />
            <span v-else>{{ formatTokenAmount(stats.totalBridgedToPolygon) }}</span>
          </p>
        </div>
      </BaseCard>

      <BaseCard>
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Bridged from Polygon</p>
          <p class="text-xl font-bold text-gray-900 dark:text-white mt-1">
            {{ formatTokenAmount(stats.totalBridgedFromPolygon) }}
          </p>
        </div>
      </BaseCard>

      <BaseCard>
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Total Requests</p>
          <p class="text-xl font-bold text-gray-900 dark:text-white mt-1">
            {{ stats.requestsCount?.toString() || '0' }}
          </p>
        </div>
      </BaseCard>

      <BaseCard>
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Bridge Fee</p>
          <p class="text-xl font-bold text-primary-600 dark:text-primary-400 mt-1">
            {{ feePercentage }}%
          </p>
        </div>
      </BaseCard>
    </div>

    <!-- Bridge Form -->
    <BaseCard>
      <template #header>
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
          Bridge to Polygon
        </h2>
      </template>

      <form class="space-y-6" @submit.prevent="handleBridge">
        <!-- From Chain -->
        <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">From</p>
            <p class="font-medium text-gray-900 dark:text-white">Ethereum</p>
          </div>
          <div class="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
            <span class="text-xl">&#9830;</span>
          </div>
        </div>

        <!-- Arrow -->
        <div class="flex justify-center">
          <svg class="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
          </svg>
        </div>

        <!-- To Chain -->
        <div class="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">To</p>
            <p class="font-medium text-gray-900 dark:text-white">Polygon</p>
          </div>
          <div class="w-10 h-10 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center">
            <span class="text-xl">&#128268;</span>
          </div>
        </div>

        <!-- Amount Input -->
        <div>
          <BaseInput
            v-model="bridgeAmount"
            type="number"
            label="Amount to Bridge"
            placeholder="0.00"
            :error="bridgeError"
            :disabled="!isActive"
          >
            <template #suffix>
              <button
                type="button"
                class="text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400 font-medium"
                :disabled="!isActive"
                @click="setMaxAmount"
              >
                MAX
              </button>
            </template>
          </BaseInput>
          <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Available: {{ formatTokenAmount(balance) }} EVMORE
          </p>
        </div>

        <!-- Fee Breakdown -->
        <div v-if="bridgeAmount" class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg space-y-2">
          <div class="flex justify-between text-sm">
            <span class="text-gray-600 dark:text-gray-400">Bridge Fee ({{ feePercentage }}%)</span>
            <span class="text-gray-900 dark:text-white">{{ formatTokenAmount(fee) }} EVMORE</span>
          </div>
          <div class="flex justify-between font-medium">
            <span class="text-gray-900 dark:text-white">You will receive</span>
            <span class="text-primary-600 dark:text-primary-400">{{ formatTokenAmount(netAmount) }} EVMORE</span>
          </div>
        </div>

        <BaseButton
          type="submit"
          variant="primary"
          class="w-full"
          :loading="isSubmitting"
          :disabled="!isActive || !bridgeAmount"
        >
          {{ isActive ? 'Bridge to Polygon' : 'Bridge Inactive' }}
        </BaseButton>
      </form>
    </BaseCard>

    <!-- Bridge Limits -->
    <BaseCard>
      <template #header>
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
          Bridge Limits
        </h2>
      </template>

      <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Minimum</p>
          <p class="text-lg font-bold text-gray-900 dark:text-white mt-1">
            {{ formatTokenAmount(config.minAmount) }}
          </p>
        </div>

        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Maximum</p>
          <p class="text-lg font-bold text-gray-900 dark:text-white mt-1">
            {{ formatTokenAmount(config.maxAmount) }}
          </p>
        </div>

        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Daily Limit Remaining</p>
          <p class="text-lg font-bold text-gray-900 dark:text-white mt-1">
            {{ formatTokenAmount(remainingDailyLimit) }}
          </p>
        </div>

        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400">Your Daily Remaining</p>
          <p class="text-lg font-bold text-gray-900 dark:text-white mt-1">
            {{ formatTokenAmount(userRemainingDailyLimit) }}
          </p>
        </div>
      </div>
    </BaseCard>
  </div>
</template>

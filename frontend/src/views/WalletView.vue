<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useWalletStore } from '@/stores/wallet'
import { useTokenStore } from '@/stores/token'
import { useNotificationsStore } from '@/stores/notifications'
import BaseCard from '@/components/common/BaseCard.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseInput from '@/components/common/BaseInput.vue'
import BaseSpinner from '@/components/common/BaseSpinner.vue'
import { formatTokenAmount, parseTokenAmount, formatAddress } from '@/utils/formatters'
import { getExplorerAddressUrl, type ChainId } from '@/contracts/addresses'

const walletStore = useWalletStore()
const tokenStore = useTokenStore()
const notificationsStore = useNotificationsStore()

const { address, chainId, shortAddress, formattedBalance: ethBalance } = storeToRefs(walletStore)
const { balance, isLoading } = storeToRefs(tokenStore)

// Transfer form
const transferTo = ref('')
const transferAmount = ref('')
const isTransferring = ref(false)
const transferError = ref('')

// Fetch data
watch(() => walletStore.isConnected, async (connected) => {
  if (connected) {
    await tokenStore.fetchBalance()
  }
})

onMounted(async () => {
  if (walletStore.isConnected) {
    await tokenStore.fetchBalance()
  }
})

async function handleTransfer() {
  if (!transferTo.value || !transferAmount.value) {
    transferError.value = 'Please fill in all fields'
    return
  }

  // Validate address
  if (!/^0x[a-fA-F0-9]{40}$/.test(transferTo.value)) {
    transferError.value = 'Invalid Ethereum address'
    return
  }

  const amount = parseTokenAmount(transferAmount.value)
  if (amount === 0n) {
    transferError.value = 'Invalid amount'
    return
  }

  if (amount > balance.value) {
    transferError.value = 'Insufficient balance'
    return
  }

  isTransferring.value = true
  transferError.value = ''

  try {
    await tokenStore.transfer(transferTo.value, amount)
    notificationsStore.success(
      'Transfer Successful',
      `Sent ${transferAmount.value} EVMORE to ${formatAddress(transferTo.value)}`
    )
    transferTo.value = ''
    transferAmount.value = ''
  } catch (e: any) {
    transferError.value = e.message
    notificationsStore.error('Transfer Failed', e.message)
  } finally {
    isTransferring.value = false
  }
}

function setMaxAmount() {
  transferAmount.value = formatTokenAmount(balance.value, 18, 18)
}
</script>

<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
      Wallet
    </h1>

    <!-- Balances -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <BaseCard>
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
            <span class="text-2xl font-bold text-primary-600">E</span>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">EVMORE Balance</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">
              <BaseSpinner v-if="isLoading" size="sm" />
              <span v-else>{{ formatTokenAmount(balance) }}</span>
            </p>
          </div>
        </div>
      </BaseCard>

      <BaseCard>
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
            <span class="text-2xl">&#9830;</span>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">ETH Balance</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">
              {{ ethBalance }} ETH
            </p>
          </div>
        </div>
      </BaseCard>
    </div>

    <!-- Account Info -->
    <BaseCard>
      <template #header>
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
          Account Information
        </h2>
      </template>

      <div class="space-y-4">
        <div class="flex items-center justify-between py-3 border-b border-gray-200 dark:border-gray-700">
          <span class="text-gray-600 dark:text-gray-400">Address</span>
          <div class="flex items-center gap-2">
            <span class="font-mono text-gray-900 dark:text-white">
              {{ shortAddress }}
            </span>
            <a
              v-if="chainId"
              :href="getExplorerAddressUrl(chainId as ChainId, address || '')"
              target="_blank"
              class="text-primary-600 hover:text-primary-700 dark:text-primary-400"
            >
              <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
            </a>
          </div>
        </div>

        <div class="flex items-center justify-between py-3">
          <span class="text-gray-600 dark:text-gray-400">Full Address</span>
          <span class="font-mono text-sm text-gray-900 dark:text-white break-all">
            {{ address }}
          </span>
        </div>
      </div>
    </BaseCard>

    <!-- Transfer Form -->
    <BaseCard>
      <template #header>
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
          Send EVMORE
        </h2>
      </template>

      <form class="space-y-4" @submit.prevent="handleTransfer">
        <BaseInput
          v-model="transferTo"
          label="Recipient Address"
          placeholder="0x..."
          :error="transferError && transferError.includes('address') ? transferError : ''"
        />

        <div>
          <BaseInput
            v-model="transferAmount"
            type="number"
            label="Amount"
            placeholder="0.00"
            :error="transferError && !transferError.includes('address') ? transferError : ''"
          >
            <template #suffix>
              <button
                type="button"
                class="text-sm text-primary-600 hover:text-primary-700 dark:text-primary-400 font-medium"
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

        <BaseButton
          type="submit"
          variant="primary"
          class="w-full"
          :loading="isTransferring"
          :disabled="!transferTo || !transferAmount"
        >
          Send EVMORE
        </BaseButton>
      </form>
    </BaseCard>
  </div>
</template>

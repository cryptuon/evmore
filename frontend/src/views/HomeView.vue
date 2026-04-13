<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useWalletStore } from '@/stores/wallet'
import { useNetworkStore } from '@/stores/network'
import { storeToRefs } from 'pinia'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseCard from '@/components/common/BaseCard.vue'

const router = useRouter()
const walletStore = useWalletStore()
const networkStore = useNetworkStore()
const { isConnected, isConnecting } = storeToRefs(walletStore)
const { overview, selectedChain } = storeToRefs(networkStore)

const supplyText = computed(() => {
  if (!overview.value) return '—'
  try {
    const whole = BigInt(overview.value.total_supply) / 10n ** 18n
    return whole.toLocaleString()
  } catch {
    return '—'
  }
})

const features = [
  {
    title: 'Mine Digital Gold',
    description: 'Use KeccakCollision proof-of-work mining to earn EVMORE tokens',
    icon: '&#9874;' // Hammer icon
  },
  {
    title: 'Fair Launch',
    description: 'No premine, no ICO. 100% community-driven from day one',
    icon: '&#9878;' // Scales icon
  },
  {
    title: 'Cross-Chain Bridge',
    description: 'Bridge EVMORE between Ethereum and Polygon seamlessly',
    icon: '&#128279;' // Bridge icon
  },
  {
    title: 'Deflationary Model',
    description: '21M max supply with halving schedule like Bitcoin',
    icon: '&#128200;' // Chart icon
  }
]

async function handleConnect() {
  const success = await walletStore.connect()
  if (success) {
    router.push('/dashboard')
  }
}
</script>

<template>
  <div class="space-y-12">
    <!-- Hero Section -->
    <section class="text-center py-12 md:py-20">
      <div class="max-w-3xl mx-auto">
        <h1 class="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
          <span class="text-gradient">EVMORE</span>
          <br />
          Digital Gold on Ethereum
        </h1>
        <p class="text-xl text-gray-600 dark:text-gray-400 mb-8">
          A revolutionary proof-of-work cryptocurrency with KeccakCollision mining.
          Fair launch, zero premine, and a deflationary economic model.
        </p>
        <div class="flex flex-col sm:flex-row items-center justify-center gap-4">
          <BaseButton
            v-if="!isConnected"
            variant="primary"
            size="lg"
            :loading="isConnecting"
            @click="handleConnect"
          >
            Connect Wallet to Start
          </BaseButton>
          <BaseButton
            v-else
            variant="primary"
            size="lg"
            @click="router.push('/mining')"
          >
            Start Mining
          </BaseButton>
          <BaseButton
            variant="secondary"
            size="lg"
            @click="router.push('/dashboard')"
          >
            Launch Dashboard
          </BaseButton>
        </div>

        <!-- Live public stats strip -->
        <div v-if="overview" class="mt-10 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto">
          <div class="p-3 rounded-lg bg-white/60 dark:bg-gray-800/60 border border-gray-200 dark:border-gray-700">
            <p class="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Network</p>
            <p class="text-sm font-semibold text-gray-900 dark:text-white mt-1">{{ selectedChain?.name ?? '—' }}</p>
          </div>
          <div class="p-3 rounded-lg bg-white/60 dark:bg-gray-800/60 border border-gray-200 dark:border-gray-700">
            <p class="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Supply</p>
            <p class="text-sm font-semibold text-gray-900 dark:text-white mt-1">{{ supplyText }} EVMORE</p>
          </div>
          <div class="p-3 rounded-lg bg-white/60 dark:bg-gray-800/60 border border-gray-200 dark:border-gray-700">
            <p class="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Blocks</p>
            <p class="text-sm font-semibold text-gray-900 dark:text-white mt-1">{{ overview.blocks_mined }}</p>
          </div>
          <div class="p-3 rounded-lg bg-white/60 dark:bg-gray-800/60 border border-gray-200 dark:border-gray-700">
            <p class="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400">Difficulty</p>
            <p class="text-sm font-semibold text-gray-900 dark:text-white mt-1">{{ overview.current_difficulty }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Grid -->
    <section>
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white text-center mb-8">
        Why EVMORE?
      </h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <BaseCard v-for="feature in features" :key="feature.title">
          <div class="flex items-start gap-4">
            <div class="flex-shrink-0 w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
              <span class="text-2xl" v-html="feature.icon" />
            </div>
            <div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {{ feature.title }}
              </h3>
              <p class="text-gray-600 dark:text-gray-400">
                {{ feature.description }}
              </p>
            </div>
          </div>
        </BaseCard>
      </div>
    </section>

    <!-- Stats Preview -->
    <section>
      <BaseCard>
        <template #header>
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">
            Token Economics
          </h2>
        </template>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div class="text-center">
            <p class="text-3xl font-bold text-primary-500">21M</p>
            <p class="text-sm text-gray-600 dark:text-gray-400">Max Supply</p>
          </div>
          <div class="text-center">
            <p class="text-3xl font-bold text-primary-500">50</p>
            <p class="text-sm text-gray-600 dark:text-gray-400">Initial Block Reward</p>
          </div>
          <div class="text-center">
            <p class="text-3xl font-bold text-primary-500">210K</p>
            <p class="text-sm text-gray-600 dark:text-gray-400">Blocks per Halving</p>
          </div>
          <div class="text-center">
            <p class="text-3xl font-bold text-primary-500">10min</p>
            <p class="text-sm text-gray-600 dark:text-gray-400">Target Block Time</p>
          </div>
        </div>
      </BaseCard>
    </section>
  </div>
</template>

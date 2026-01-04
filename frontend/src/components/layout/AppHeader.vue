<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useWalletStore } from '@/stores/wallet'
import { storeToRefs } from 'pinia'
import ThemeToggle from '@/components/common/ThemeToggle.vue'
import BaseButton from '@/components/common/BaseButton.vue'
import BaseBadge from '@/components/common/BaseBadge.vue'

const walletStore = useWalletStore()
const { isConnected, shortAddress, chainName, isSupportedNetwork, isConnecting } = storeToRefs(walletStore)

const isMobileMenuOpen = ref(false)

const navLinks = [
  { name: 'Dashboard', path: '/dashboard', requiresWallet: true },
  { name: 'Mining', path: '/mining', requiresWallet: true },
  { name: 'Wallet', path: '/wallet', requiresWallet: true },
  { name: 'Bridge', path: '/bridge', requiresWallet: true },
  { name: 'Stats', path: '/stats', requiresWallet: false }
]

async function connectWallet() {
  await walletStore.connect()
}

function disconnectWallet() {
  walletStore.disconnect()
}
</script>

<template>
  <header class="sticky top-0 z-40 bg-white/80 dark:bg-evmore-dark/80 backdrop-blur-lg border-b border-gray-200 dark:border-gray-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- Logo -->
        <div class="flex items-center">
          <RouterLink to="/" class="flex items-center gap-2">
            <div class="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
              <span class="text-lg font-bold text-gray-900">E</span>
            </div>
            <span class="text-xl font-bold text-gray-900 dark:text-white">
              EVMORE
            </span>
          </RouterLink>
        </div>

        <!-- Desktop Navigation -->
        <nav class="hidden md:flex items-center gap-1">
          <template v-for="link in navLinks" :key="link.path">
            <RouterLink
              v-if="!link.requiresWallet || isConnected"
              :to="link.path"
              class="px-3 py-2 rounded-lg text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-800 transition-colors"
              active-class="!text-primary-600 dark:!text-primary-400 bg-primary-50 dark:bg-primary-900/20"
            >
              {{ link.name }}
            </RouterLink>
          </template>
        </nav>

        <!-- Right side actions -->
        <div class="flex items-center gap-3">
          <ThemeToggle />

          <!-- Wallet connection -->
          <div v-if="isConnected" class="hidden sm:flex items-center gap-2">
            <BaseBadge
              :variant="isSupportedNetwork ? 'success' : 'warning'"
              size="sm"
            >
              {{ chainName }}
            </BaseBadge>
            <div class="relative group">
              <button
                class="flex items-center gap-2 px-3 py-1.5 bg-gray-100 dark:bg-gray-800 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
              >
                <span class="w-2 h-2 bg-green-500 rounded-full" />
                {{ shortAddress }}
              </button>
              <!-- Dropdown -->
              <div class="absolute right-0 mt-2 w-48 py-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                <button
                  class="w-full px-4 py-2 text-left text-sm text-red-600 hover:bg-gray-100 dark:hover:bg-gray-700"
                  @click="disconnectWallet"
                >
                  Disconnect
                </button>
              </div>
            </div>
          </div>
          <BaseButton
            v-else
            variant="primary"
            size="sm"
            :loading="isConnecting"
            @click="connectWallet"
          >
            Connect Wallet
          </BaseButton>

          <!-- Mobile menu button -->
          <button
            class="md:hidden p-2 rounded-lg text-gray-500 hover:text-gray-700 hover:bg-gray-100 dark:text-gray-400 dark:hover:text-gray-200 dark:hover:bg-gray-800"
            @click="isMobileMenuOpen = !isMobileMenuOpen"
          >
            <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                v-if="!isMobileMenuOpen"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M4 6h16M4 12h16M4 18h16"
              />
              <path
                v-else
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile Navigation -->
    <Transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <div
        v-if="isMobileMenuOpen"
        class="md:hidden border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-evmore-dark"
      >
        <div class="px-4 py-3 space-y-1">
          <template v-for="link in navLinks" :key="link.path">
            <RouterLink
              v-if="!link.requiresWallet || isConnected"
              :to="link.path"
              class="block px-3 py-2 rounded-lg text-base font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-800"
              active-class="!text-primary-600 dark:!text-primary-400 bg-primary-50 dark:bg-primary-900/20"
              @click="isMobileMenuOpen = false"
            >
              {{ link.name }}
            </RouterLink>
          </template>

          <!-- Mobile wallet info -->
          <div v-if="isConnected" class="pt-3 border-t border-gray-200 dark:border-gray-700">
            <div class="flex items-center justify-between px-3 py-2">
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 bg-green-500 rounded-full" />
                <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {{ shortAddress }}
                </span>
              </div>
              <BaseBadge
                :variant="isSupportedNetwork ? 'success' : 'warning'"
                size="sm"
              >
                {{ chainName }}
              </BaseBadge>
            </div>
            <button
              class="w-full mt-2 px-3 py-2 text-left text-sm text-red-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              @click="disconnectWallet"
            >
              Disconnect Wallet
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </header>
</template>

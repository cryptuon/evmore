import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/DashboardView.vue'),
    meta: { requiresWallet: true }
  },
  {
    path: '/mining',
    name: 'Mining',
    component: () => import('@/views/MiningView.vue'),
    meta: { requiresWallet: true }
  },
  {
    path: '/wallet',
    name: 'Wallet',
    component: () => import('@/views/WalletView.vue'),
    meta: { requiresWallet: true }
  },
  {
    path: '/bridge',
    name: 'Bridge',
    component: () => import('@/views/BridgeView.vue'),
    meta: { requiresWallet: true }
  },
  {
    path: '/stats',
    name: 'Stats',
    component: () => import('@/views/StatsView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard for wallet-required routes
router.beforeEach(async (to, _from, next) => {
  if (to.meta.requiresWallet) {
    const { useWalletStore } = await import('@/stores/wallet')
    const walletStore = useWalletStore()

    if (!walletStore.isConnected) {
      next({ name: 'Home', query: { redirect: to.fullPath } })
      return
    }
  }
  next()
})

export default router

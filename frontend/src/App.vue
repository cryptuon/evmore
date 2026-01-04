<script setup lang="ts">
import { RouterView } from 'vue-router'
import AppHeader from '@/components/layout/AppHeader.vue'
import NotificationContainer from '@/components/layout/NotificationContainer.vue'
</script>

<template>
  <div class="min-h-screen bg-gray-50 dark:bg-evmore-darker">
    <AppHeader />
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <RouterView />
    </main>
    <NotificationContainer />
  </div>
</template>

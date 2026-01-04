<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useNotificationsStore } from '@/stores/notifications'
import BaseToast from '@/components/common/BaseToast.vue'

const notificationsStore = useNotificationsStore()
const { notifications } = storeToRefs(notificationsStore)
</script>

<template>
  <Teleport to="body">
    <div class="fixed top-20 right-4 z-50 flex flex-col gap-3 w-full max-w-sm">
      <TransitionGroup
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="opacity-0 translate-x-4"
        enter-to-class="opacity-100 translate-x-0"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="opacity-100 translate-x-0"
        leave-to-class="opacity-0 translate-x-4"
      >
        <BaseToast
          v-for="notification in notifications"
          :key="notification.id"
          :notification="notification"
          @close="notificationsStore.removeNotification(notification.id)"
        />
      </TransitionGroup>
    </div>
  </Teleport>
</template>

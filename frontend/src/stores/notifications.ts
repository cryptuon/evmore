import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Notification } from '@/types'

export const useNotificationsStore = defineStore('notifications', () => {
  const notifications = ref<Notification[]>([])
  const maxNotifications = 5

  function addNotification(notification: Omit<Notification, 'id'>) {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2)}`

    const newNotification: Notification = {
      id,
      autoClose: true,
      duration: 5000,
      ...notification
    }

    notifications.value.unshift(newNotification)

    // Limit notifications
    if (notifications.value.length > maxNotifications) {
      notifications.value = notifications.value.slice(0, maxNotifications)
    }

    // Auto-close after duration
    if (newNotification.autoClose) {
      setTimeout(() => {
        removeNotification(id)
      }, newNotification.duration)
    }

    return id
  }

  function removeNotification(id: string) {
    notifications.value = notifications.value.filter(n => n.id !== id)
  }

  function clearAll() {
    notifications.value = []
  }

  // Convenience methods
  function success(title: string, message: string) {
    return addNotification({ type: 'success', title, message, timestamp: Date.now() })
  }

  function error(title: string, message: string) {
    return addNotification({
      type: 'error',
      title,
      message,
      timestamp: Date.now(),
      autoClose: false // Errors stay until dismissed
    })
  }

  function warning(title: string, message: string) {
    return addNotification({ type: 'warning', title, message, timestamp: Date.now() })
  }

  function info(title: string, message: string) {
    return addNotification({ type: 'info', title, message, timestamp: Date.now() })
  }

  return {
    notifications,
    addNotification,
    removeNotification,
    clearAll,
    success,
    error,
    warning,
    info
  }
})

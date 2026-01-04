<script setup lang="ts">
interface Props {
  padding?: boolean
}

withDefaults(defineProps<Props>(), {
  padding: true
})
</script>

<template>
  <div
    class="bg-white dark:bg-evmore-dark rounded-xl shadow-lg border border-gray-200 dark:border-gray-800 overflow-hidden"
  >
    <div
      v-if="$slots.header"
      class="px-6 py-4 border-b border-gray-200 dark:border-gray-800"
    >
      <slot name="header" />
    </div>
    <div :class="padding ? 'p-6' : ''">
      <slot />
    </div>
    <div
      v-if="$slots.footer"
      class="px-6 py-4 border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/50"
    >
      <slot name="footer" />
    </div>
  </div>
</template>

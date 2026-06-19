<template>
  <AuthEntry
    v-if="!hasEntered"
    @guest-enter="enterSystem"
    @auth-enter="enterSystem"
  />

  <template v-else>
    <router-view />
    <AuthPanel />
  </template>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import AuthEntry from './components/AuthEntry.vue'
import AuthPanel from './components/AuthPanel.vue'
import { getAuthToken, hasGuestEntered } from './utils/auth'

const hasEntered = ref(false)

onMounted(() => {
  if (getAuthToken() || hasGuestEntered()) {
    hasEntered.value = true
  }
})

function enterSystem() {
  hasEntered.value = true
}
</script>
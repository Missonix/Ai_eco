<template>
  <div class="min-h-screen bg-gray-100">
    <Navigation />
    <div class="pt-0 md:pt-16 pb-16 md:pb-0">
      <router-view></router-view>
    </div>
  </div>
</template>

<script setup lang="ts">
import Navigation from './components/Navigation.vue'
</script>

<style>
body {
  margin: 0;
  padding: 0;
  font-family:
    -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}
</style>

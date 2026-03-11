<script setup lang="ts">
import { ref } from 'vue'

const backend_url: string = import.meta.env.VUE_APP_API_URL ?? ""
</script>

<template>
  <div>
    <a :href="`${backend_url}/login/youtube`">Log In with YouTube</a>
  </div>
</template>

<style>

</style>
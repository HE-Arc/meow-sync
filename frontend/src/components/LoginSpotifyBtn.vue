<script setup lang="ts">
import { ref } from 'vue'

const backend_url: string = import.meta.env.VUE_APP_API_URL ?? ""
</script>

<template>
  <div>
    <a :href="backend_url + '/login/spotify'">Log In with Spotify</a>
  </div>
</template>

<style>

</style>
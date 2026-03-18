<script setup lang="ts">
import logo from "@/assets/logo.svg";
</script>

<template>
  <div class="flex items-center">
    <img :src="logo" alt="App logo" class="h-15 w-15 p-2" />
    <h1 class="text-2xl m-1"><span class="text-primary">Meow</span> // Sync</h1>
  </div>
</template>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,100..900;1,100..900&family=Varela+Round&display=swap");

h1 {
  font-family: "Varela Round", sans-serif;
}
</style>

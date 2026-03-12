<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
import HelloWorld from "./components/HelloWorld.vue";
</script>

<template>
  <Suspense>
    <UApp>
      <UHeader>
        <template #left>
          <RouterLink to="/">App logo</RouterLink>
        </template>
      </UHeader>

      <UMain>
        <RouterView />
      </UMain>

      <UFooter>
        <p class="text-center text-sm text-gray-500">
          &copy; 2024 Meow Sync. All rights reserved.
        </p>
      </UFooter>
    </UApp>
  </Suspense>
</template>

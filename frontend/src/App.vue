<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
import AppIconWithText from "./components/icons/AppIconWithText.vue";
</script>

<template>
  <Suspense>
    <UApp>
      <UHeader>
        <template #left>
          <RouterLink to="/">
            <AppIconWithText />
          </RouterLink>
        </template>
      </UHeader>

      <UMain>
        <RouterView />
      </UMain>

      <UFooter>
        <p class="text-center text-sm text-gray-500">
          &copy; {{ new Date().getFullYear() }} Meow Sync. All rights reserved.
        </p>
      </UFooter>
    </UApp>
  </Suspense>
</template>

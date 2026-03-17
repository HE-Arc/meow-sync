<script setup lang="ts">
import {
  ProvidersInformations,
  type SyncProvider,
} from "@/types/SyncProviders";

function redirectTo(syncProvider: SyncProvider) {
  window.location.href = ProvidersInformations[syncProvider].backendRoute;
}
</script>

<template>
  <main class="flex flex-col items-center justify-center h-screen">
    <h1 class="text-4xl font-bold mb-4">Welcome to Meow Sync!</h1>
    <p class="text-lg text-gray-600 mb-8">
      Your ultimate playlist synchronization tool.
    </p>
    <div class="flex space-x-4 flex-col gap-2 items-center justify-center">
      <button
        type="button"
        v-for="syncProvider in ProvidersInformations"
        class="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors"
        :style="{ backgroundColor: syncProvider.color }"
      >
        Login with {{ syncProvider.name }}
      </button>
    </div>
  </main>
</template>

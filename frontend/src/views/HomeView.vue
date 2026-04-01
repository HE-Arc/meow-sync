<script setup lang="ts">
import { useGetLoginUrlAndRedirect } from "@/composables/useAuth";
import { useUserInfo } from "@/composables/useUserInfo";
import {
  ProvidersInformations,
  type SyncProvider,
  type SyncProviderInformation,
} from "@/types/SyncProviders";

const { login } = useGetLoginUrlAndRedirect();
const { user } = useUserInfo();

function handleLogin(
  provider: SyncProvider,
  _syncProvider: SyncProviderInformation,
) {
  login(provider);
}
</script>

<template>
  <div class="flex flex-col items-center justify-center text-center">
    <h1 class="text-4xl font-bold mb-4">Welcome to Meow Sync!</h1>
    <p class="text-lg text-gray-600 mb-8">
      Your ultimate playlist synchronization tool.
    </p>
    <div class="flex space-x-4 flex-col gap-2 items-center justify-center">
      <div v-if="user">
        <p class="text-xl">
          Go to your
          <RouterLink to="/settings" class="text-primary hover:underline"
            >settings</RouterLink
          >
          to manage your connections or create a
          <RouterLink to="/sync" class="text-primary hover:underline"
            >new sync</RouterLink
          >.
        </p>
      </div>
      <UButton
        type="button"
        :icon="syncProvider.icon"
        v-else
        v-for="(syncProvider, provider) in ProvidersInformations"
        :key="provider"
        @click="handleLogin(provider, syncProvider)"
        class="text-white rounded-lg hover:bg-primary-dark transition-colors"
        :style="{ backgroundColor: syncProvider.color }"
      >
        Login with {{ syncProvider.name }}
      </UButton>
    </div>
  </div>
</template>

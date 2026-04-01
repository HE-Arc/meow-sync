<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { useHandleCallback } from "@/composables/useAuth";

const route = useRoute();
const { handleCallback, isHandlingCallback, error } = useHandleCallback();

const errorText = ref("");

onMounted(async () => {
  const code = route.query.code as string | undefined;
  const state = route.query.state as string | undefined;

  if (!code || !state) {
    errorText.value = "Missing code or state in callback URL";
    return;
  }

  await handleCallback({ code, state });
});
</script>

<template>
  <div class="flex flex-col items-center justify-center text-center">
    <div v-if="isHandlingCallback">
      <p class="text-gray-500">Completing login...</p>
    </div>
    <div v-else-if="error">
      <p class="text-red-500">Login failed: {{ error.message }}</p>
    </div>
    <div v-else-if="errorText">
      <p class="text-red-500">{{ errorText }}</p>
    </div>
  </div>
</template>

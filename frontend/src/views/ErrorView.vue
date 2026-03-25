<script setup lang="ts">
import { RouterLink } from "vue-router";

const props = defineProps<{
  errorCode: number;
  errorMessage: string;
}>();
</script>
<template>
  <div class="flex flex-col items-center justify-center">
    <img
      :src="`https://http.cat/${props.errorCode}.jpg`"
      :alt="`Error ${props.errorCode} cat`"
      class="h-150"
    />

    <UButton class="mt-4" to="/">Go to Home</UButton>
  </div>
</template>

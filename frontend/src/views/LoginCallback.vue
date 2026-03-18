<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";

const errorText = ref("");
const route = useRoute();
const router = useRouter();

const token = route.query.token as string;

if (!token) {
  errorText.value = "No token provided";
} else {
  localStorage.setItem("token", token);
  setTimeout(() => {
    router.push("/");
  }, 2000);
}
</script>

<template>
  <div v-if="errorText">
    <p class="text-red-500">{{ errorText }}</p>
  </div>
  <div v-else>
    <p class="text-green-500">
      Login successful! You will be redirected shortly.
    </p>
  </div>
</template>

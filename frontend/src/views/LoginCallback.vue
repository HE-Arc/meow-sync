<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { useAuth } from "@/composables/useAuth";

const route = useRoute();
const { handleOAuthCallback } = useAuth();

const errorText = ref("");
const loading = ref(true);

onMounted(async () => {
	const code = route.query.code as string | undefined;
	const state = route.query.state as string | undefined;

	if (!code || !state) {
		errorText.value = "Missing code or state in callback URL";
		loading.value = false;
		return;
	}

	await handleOAuthCallback(code, state);
	loading.value = false;
});
</script>

<template>
	<div class="flex flex-col items-center justify-center text-center">
		<div v-if="loading">
			<p class="text-gray-500">Completing login...</p>
		</div>
		<div v-else-if="errorText">
			<p class="text-red-500">{{ errorText }}</p>
		</div>
	</div>
</template>

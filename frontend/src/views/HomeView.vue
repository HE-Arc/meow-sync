<script setup lang="ts">
import { useAuth } from "@/composables/useAuth";
import {
	ProvidersInformations,
	type SyncProvider,
	type SyncProviderInformation,
} from "@/types/SyncProviders";

const { login } = useAuth();

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
			<UButton
				type="button"
				:icon="syncProvider.icon"
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

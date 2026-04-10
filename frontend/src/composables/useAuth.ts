import { useToast } from "@nuxt/ui/runtime/composables/useToast.js";
import { defineMutation, useMutation, useQueryCache } from "@pinia/colada";
import { defineStore } from "pinia";
import type { Ref } from "vue";
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { client } from "@/api/client";
import type { components } from "@/api/schema.d.ts";

export type ProviderEnum = components["schemas"]["OAuthConnectionProviderEnum"];
export type OAuthLoginResponse = components["schemas"]["OAuthLoginResponse"];
export type OAuthCallbackSuccess =
	components["schemas"]["OAuthCallbackSuccess"];
export type Me = components["schemas"]["Me"];
export type OAuthConnection = components["schemas"]["OAuthConnection"];

const TOKEN_LOCAL_STORAGE_KEY = "auth_token";

const OAUTH_PROVIDER_SESSION_KEY = "oauth_provider";
const CURRENT_PATH_SESSION_KEY = "current_path";

export const useApiToken = defineStore("apiToken", () => {
	const token: Ref<string | null> = ref(
		localStorage.getItem(TOKEN_LOCAL_STORAGE_KEY),
	);
	const isAuthenticated = computed(() => !!token.value);
	const queryCache = useQueryCache();

	const setToken = (newToken: string | null) => {
		token.value = newToken;
		// We have new token invalidate all queries
		queryCache.invalidateQueries();
		if (newToken) {
			localStorage.setItem(TOKEN_LOCAL_STORAGE_KEY, newToken);
		} else {
			localStorage.removeItem(TOKEN_LOCAL_STORAGE_KEY);
		}
	};

	return {
		isAuthenticated,
		token,
		setToken,
	};
});

export const useGetLoginUrlAndRedirect = defineMutation(() => {
	const router = useRouter();
	const mutation = useMutation({
		key: (provider: ProviderEnum) => ["oauth_login_url", provider],
		mutation: async (provider: ProviderEnum) => {
			const { data } = await client.GET("/api/oauth/{provider}/login/", {
				params: { path: { provider } },
			});
			return data;
		},
		onSuccess(data, provider) {
			if (!data) return;
			sessionStorage.setItem(OAUTH_PROVIDER_SESSION_KEY, provider);
			sessionStorage.setItem(
				CURRENT_PATH_SESSION_KEY,
				router.currentRoute.value.fullPath,
			);
			window.location.href = data.login_url;
		},
	});
	return {
		...mutation,
		login: mutation.mutate,
		isLoggingIn: computed(() => mutation.status.value === "pending"),
	};
});

export const useHandleCallback = defineMutation(() => {
	const router = useRouter();
	const token = useApiToken();

	const mutation = useMutation({
		key: (params: { code: string; state: string }) => [
			"oauth_callback",
			params.code,
		],
		mutation: async ({ code, state }: { code: string; state: string }) => {
			const provider = sessionStorage.getItem(
				OAUTH_PROVIDER_SESSION_KEY,
			) as ProviderEnum;
			if (!provider) throw new Error("No provider found in session storage");
			const { data } = await client.GET("/api/oauth/{provider}/callback/", {
				params: { path: { provider }, query: { code, state } },
			});

			return data;
		},
		onSuccess(data) {
			if (!data) return;
			token.setToken(data.auth_token);
			sessionStorage.removeItem(OAUTH_PROVIDER_SESSION_KEY);
			const currentPath = sessionStorage.getItem(CURRENT_PATH_SESSION_KEY);
			sessionStorage.removeItem(CURRENT_PATH_SESSION_KEY);
			router.push(currentPath || "/playlists");
		},
	});
	return {
		...mutation,
		handleCallback: mutation.mutateAsync,
		isHandlingCallback: computed(() => mutation.status.value === "pending"),
	};
});

export const useDisconnectProvider = defineMutation(() => {
	const toast = useToast();
	const mutation = useMutation({
		key: (provider: ProviderEnum) => ["disconnect", provider],
		mutation: async (provider: ProviderEnum) => {
			const { data } = await client.DELETE(
				"/api/oauth/{provider}/disconnect/",
				{ params: { path: { provider } } },
			);
			return data;
		},
		onSuccess() {
			toast.add({
				title: "Success",
				description: "Provider disconnected successfully.",
				color: "success",
			});
		},
	});
	return {
		...mutation,
		disconnect: mutation.mutateAsync,
		isDisconnecting: computed(() => mutation.asyncStatus.value === "loading"),
	};
});

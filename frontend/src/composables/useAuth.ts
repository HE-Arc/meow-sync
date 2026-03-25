import { computed } from "vue";
import { useRouter } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import type { SyncProvider } from "@/types/SyncProviders";
import { type ProviderEnum, useAuthApi } from "./useAuthApi";

export function useAuth() {
	const store = useAuthStore();
	const authApi = useAuthApi();
	const router = useRouter();

	const isAuthenticated = computed(() => store.isAuthenticated);
	const token = computed(() => store.token);

	async function login(provider: SyncProvider) {
		const data = await authApi.getLoginUrl(provider as ProviderEnum);
		if (!data) return;
		sessionStorage.setItem("oauth_provider", provider);
		window.location.href = data.login_url;
	}

	async function handleOAuthCallback(code: string, state: string) {
		const provider = sessionStorage.getItem("oauth_provider") as ProviderEnum;
		if (!provider) {
			console.error("No provider found in session storage");
			return;
		}
		const data = await authApi.handleCallback(provider, code, state);
		if (!data) return;
		store.setToken(data.auth_token);
		sessionStorage.removeItem("oauth_provider");
		router.push("/playlists");
	}

	function logout() {
		store.clearToken();
		router.push("/");
	}

	return { isAuthenticated, token, login, handleOAuthCallback, logout };
}

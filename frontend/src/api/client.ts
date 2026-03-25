import createClient, { type Middleware } from "openapi-fetch";
import type { components, paths } from "./schema.d.ts";

export type Comment = components["schemas"]["Comment"];

export const client = createClient<paths>({
	baseUrl: import.meta.env.VITE_API_URL,
});

export const authMiddleware: Middleware = {
	async onRequest({ request }) {
		const { useAuthStore } = await import("@/stores/auth");
		const store = useAuthStore();
		if (store.token) {
			request.headers.set("Authorization", `Token ${store.token}`);
		}
		return request;
	},
};

export const unauthorizedMiddleware: Middleware = {
	async onResponse({ response }) {
		if (response.status === 401) {
			const { useAuthStore } = await import("@/stores/auth");
			const { default: router } = await import("@/router");
			const store = useAuthStore();
			store.clearToken();
			router.push("/");
		}
		return response;
	},
};

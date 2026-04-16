import createClient, { type Middleware } from "openapi-fetch";
import { useApiToken } from "@/composables/useAuth.ts";
import type { components, paths } from "./schema.d.ts";

export type Comment = components["schemas"]["Comment"];
export type UserInfo = components["schemas"]["Me"];
export type Playlist = components["schemas"]["PlaylistSynchronization"];

export const client = createClient<paths>({
	baseUrl: import.meta.env.VITE_API_URL,
});

export const authMiddleware: Middleware = {
	async onRequest({ request }) {
		const store = useApiToken();

		if (store.token) {
			request.headers.set("Authorization", `Token ${store.token}`);
		}
		return request;
	},
};

export const unauthorizedMiddleware: Middleware = {
	async onResponse({ response }) {
		if (response.status === 401) {
			const store = useApiToken();
			store.setToken(null);
		}
		return response;
	},
};

export interface ApiErrorDetail {
	code: string;
	detail: string;
	attr: string | null;
}

export class ApiError extends Error {
	status: number;
	errors: ApiErrorDetail[];

	constructor(status: number, errors: ApiErrorDetail[]) {
		super(`HTTP ${status}`);
		this.status = status;
		this.errors = errors;
	}
}

export const throwOnErrorMiddleware: Middleware = {
	async onResponse({ response }) {
		if (!response.ok) {
			const body = await response
				.clone()
				.json()
				.catch(() => ({ errors: [] }));
			throw new ApiError(response.status, body.errors ?? []);
		}
		return response;
	},
};

import { useToast } from "@nuxt/ui/runtime/composables/useToast.js";
import { client } from "@/api/client";
import type { components } from "@/api/schema.d.ts";
import { type BasicApiResponse, handleFetchErrors } from "./utils";

export type ProviderEnum = components["schemas"]["OAuthConnectionProviderEnum"];
export type OAuthLoginResponse = components["schemas"]["OAuthLoginResponse"];
export type OAuthCallbackSuccess =
	components["schemas"]["OAuthCallbackSuccess"];

export function useAuthApi() {
	const toast = useToast();

	const getLoginUrl = async (provider: ProviderEnum) => {
		const response = await handleFetchErrors(
			() =>
				client.GET("/api/oauth/{provider}/login/", {
					params: { path: { provider } },
				}) as Promise<BasicApiResponse<OAuthLoginResponse>>,
			toast,
		);

		if (!response) return;
		return response;
	};

	const handleCallback = async (
		provider: ProviderEnum,
		code: string,
		state: string,
	) => {
		const response = await handleFetchErrors(
			() =>
				client.GET("/api/oauth/{provider}/callback/", {
					params: { path: { provider }, query: { code, state } },
				}) as Promise<BasicApiResponse<OAuthCallbackSuccess>>,
			toast,
		);

		if (!response) return;
		return response;
	};

	const disconnect = async (provider: ProviderEnum) => {
		const response = await handleFetchErrors(
			() =>
				client.DELETE("/api/oauth/{provider}/disconnect/", {
					params: { path: { provider } },
				}) as Promise<BasicApiResponse<{ message: string }>>,
			toast,
		);

		if (!response) return;
		toast.add({
			title: "Success",
			description: "Provider disconnected successfully.",
			color: "success",
		});
		return response;
	};

	return { getLoginUrl, handleCallback, disconnect };
}

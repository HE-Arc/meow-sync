import { defineQuery, useQuery } from "@pinia/colada";
import { client } from "@/api/client";
import { useApiToken } from "./useAuth";

export const useUserInfo = defineQuery(() => {
	const tokenStore = useApiToken();
	const {
		data: user,
		isPending: isUserLoading,
		refetch: refetchUser,
		...rest
	} = useQuery({
		key: () => ["userInfo"],
		query: async () => {
			if (!tokenStore.isAuthenticated) return;
			const response = await client.GET("/api/users/me/");
			return response.data;
		},
	});

	return {
		user,
		isUserLoading,
		refetchUser,
		...rest,
	};
});

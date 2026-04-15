import { defineQuery, useQuery } from "@pinia/colada";
import { client } from "@/api/client";

export const useUserInfo = defineQuery(() => {
	const {
		data: user,
		isPending: isUserLoading,
		refetch: refetchUser,
		...rest
	} = useQuery({
		key: () => ["userInfo"],
		query: async () => {
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

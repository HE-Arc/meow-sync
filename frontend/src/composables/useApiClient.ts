import { client } from "@/api/client";

export function useCommentsApi() {
	const getComments = async () => {
		try {
			const response = await client.GET("/api/comments/");
			return response.data;
		} catch (error) {
			//TODO: Use toast
			console.error("Failed to fetch comments:", error);
			throw error;
		}
	};

	return {
		getComments,
	};
}

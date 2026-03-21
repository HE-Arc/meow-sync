import { useToast } from "@nuxt/ui/runtime/composables/useToast.js";
import { type Comment, client } from "@/api/client";
import { type BasicApiResponse, handleFetchErrors } from "./utils";

export function useCommentsApi() {
	const toast = useToast();

	const getComments = async () => {
		const response = await handleFetchErrors(
			() =>
				client.GET("/api/comments/") as Promise<BasicApiResponse<Comment[]>>,
			toast,
		);

		if (!response) return;

		return response;
	};

	const createComment = async (content: Comment) => {
		const response = await handleFetchErrors(
			() =>
				client.POST("/api/comments/", {
					body: content,
				}) as Promise<BasicApiResponse<Comment>>,
			toast,
		);

		if (!response) return;
		toast.add({
			title: "Success",
			description: "Comment created successfully!",
			color: "success",
		});
	};

	const deleteComment = async (id: number) => {
		const response = await handleFetchErrors(
			() =>
				client.DELETE(`/api/comments/{id}/`, {
					params: { path: { id } },
				}) as Promise<BasicApiResponse<void>>,
			toast,
		);

		if (!response) return;
		toast.add({
			title: "Success",
			description: "Comment deleted successfully!",
			color: "success",
		});
	};

	const getCommentById = async (id: number) => {
		const response = await handleFetchErrors(
			() =>
				client.GET(`/api/comments/{id}/`, {
					params: { path: { id } },
				}) as Promise<BasicApiResponse<Comment>>,
			toast,
		);

		if (!response) return;
		return response;
	};

	const editComment = async (id: number, content: Comment) => {
		const response = await handleFetchErrors(
			() =>
				client.PUT(`/api/comments/{id}/`, {
					params: { path: { id } },
					body: content,
				}) as Promise<BasicApiResponse<Comment>>,
			toast,
		);

		if (!response) return;
		toast.add({
			title: "Success",
			description: "Comment updated successfully!",
			color: "success",
		});
	};

	return {
		getComments,
		createComment,
		deleteComment,
		getCommentById,
		editComment,
	};
}

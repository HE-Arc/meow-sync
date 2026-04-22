import { useToast } from "@nuxt/ui/runtime/composables/useToast.js";
import { defineMutation, useMutation } from "@pinia/colada";
import { client } from "@/api/client";

export const runSync = defineMutation(() => {
	const toast = useToast();
	const mutation = useMutation({
		mutation: async (playlist_sync_id: number) => {
			const res1 = await client.POST("/api/playlists-sync/{playlist_sync_id}", {
				params: { path: { playlist_sync_id }, query: { inverse: false } },
			});
			const res2 = await client.POST("/api/playlists-sync/{playlist_sync_id}", {
				params: { path: { playlist_sync_id }, query: { inverse: true } },
			});
			return [res1.data, res2.data];
		},
		onSuccess: () => {
			toast.add({
				title: "Successfully synced playlist",
				color: "success",
			});
		},
	});
	return {
		...mutation,
	};
});

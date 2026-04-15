import { defineMutation, useMutation } from "@pinia/colada";
import { client } from "@/api/client";
import { useToast } from "@nuxt/ui/runtime/composables/useToast.js";

export const runSync = defineMutation(() => {
  const toast = useToast();
  const mutation = useMutation({
    mutation: async (playlist_sync_id: number) => {
      const res = await client.POST("/api/playlists-sync/{playlist_sync_id}", {
        params: { path: { playlist_sync_id } },
      });
      return res.data;
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

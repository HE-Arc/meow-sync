import { useToast } from "@nuxt/ui/runtime/composables/useToast.js";
import {
  defineMutation,
  defineQuery,
  useMutation,
  useQuery,
  useQueryCache,
} from "@pinia/colada";
import { ref } from "vue";
import type { Playlist as ApiPlaylist } from "@/api/client";
import { client } from "@/api/client";
import type { Playlist } from "@/api/Playlist";

export const usePlaylists = defineQuery(() => {
  const {
    data: playlists,
    isPending: isPlaylistsLoading,
    ...rest
  } = useQuery({
    key: () => ["playlists"],
    query: async () => {
      const response = await client.GET("/api/playlists/");
      return response.data;
    },
  });

  return {
    playlists,
    isPlaylistsLoading,
    ...rest,
  };
});

export const usePlaylist = defineQuery(() => {
  const id = ref(0);

  const {
    data: playlist,
    isPending: isPlaylistLoading,
    ...rest
  } = useQuery({
    key: () => ["playlist", id.value],
    enabled: () => id.value > 0,
    query: async () => {
      const response = await client.GET("/api/playlists/{id}/", {
        params: { path: { id: id.value } },
      });
      return response.data;
    },
  });

  return { playlistId: id, playlist, isPlaylistLoading, ...rest };
});

export const createPlaylist = defineMutation(() => {
  const toast = useToast();
  const queryCache = useQueryCache();

  const mutation = useMutation({
    mutation: async (playlist: Playlist) => {
      // Cast needed because the generated schema includes server-generated readonly fields
      // (id, user, created_at, updated_at) in the POST body type, but the backend sets them automatically.
      const response = await client.POST("/api/playlists/", {
        body: playlist as unknown as ApiPlaylist,
      });
      return response.data;
    },
    onSuccess() {
      toast.add({
        title: "Playlist created",
        description: "Your playlist has been created successfully.",
        color: "success",
      });
      queryCache.invalidateQueries({ key: ["playlists"], exact: true });
    },
  });

  return { ...mutation };
});

export const useUpdatePlaylist = defineMutation(() => {
  const toast = useToast();
  const queryCache = useQueryCache();

  const mutation = useMutation({
    mutation: async ({ id, data }: { id: number; data: Playlist }) => {
      const response = await client.PATCH("/api/playlists/{id}/", {
        params: { path: { id } },
        body: data,
      });
      return response.data;
    },
    onSuccess(_, { id }) {
      toast.add({
        title: "Playlist updated",
        description: "Your playlist has been updated successfully.",
        color: "success",
      });
      queryCache.invalidateQueries({ key: ["playlists"], exact: true });
      queryCache.invalidateQueries({ key: ["playlist", id], exact: true });
    },
  });

  return { ...mutation };
});

export const useDeletePlaylist = defineMutation(() => {
  const toast = useToast();
  const queryCache = useQueryCache();

  const mutation = useMutation({
    mutation: async (id: number) => {
      await client.DELETE("/api/playlists/{id}/", {
        params: { path: { id } },
      });
    },
    onSuccess(_, id) {
      toast.add({
        title: "Playlist deleted",
        description: "Your playlist has been deleted successfully.",
        color: "success",
      });
      queryCache.invalidateQueries({ key: ["playlists"], exact: true });
      queryCache.invalidateQueries({ key: ["playlist", id], exact: true });
    },
  });

  return { ...mutation };
});

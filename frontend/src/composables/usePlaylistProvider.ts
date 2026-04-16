import type { SelectItem } from "@nuxt/ui";
import { defineQuery, useQuery } from "@pinia/colada";
import { ref } from "vue";
import { client } from "@/api/client";
import type { SyncProvider } from "@/types/SyncProviders";

async function queryForProviderPlaylists(
	provider: SyncProvider,
): Promise<SelectItem[] | undefined> {
	const res = await client.GET("/api/{provider}/playlists/", {
		params: { path: { provider: provider } },
	});

	if (!res.data) {
		return;
	}

	return res.data.data.map((playlist) => ({
		label: playlist.title,
		value: playlist.id,
	}));
}

// We create two separate composables for the first and second provider playlists to avoid intereference between the two.
// If we used a single composable, changing the provider for one would change it for both, which is not the desired behavior in this case.
// This is a bit hacky but it works...

export const useFirstProviderPlaylists = defineQuery(() => {
	const provider = ref<SyncProvider | null>(null);

	const { data: providerPlaylists, isPending: isProviderPlaylistsLoading } =
		useQuery({
			key: () => ["provider_playlists", provider.value],
			query: async () => {
				if (!provider.value) return [];

				return await queryForProviderPlaylists(provider.value);
			},
		});

	return {
		firstProvider: provider,
		firstProviderPlaylists: providerPlaylists,
		isFirstProviderPlaylistsLoading: isProviderPlaylistsLoading,
	};
});

export const useSecondProviderPlaylists = defineQuery(() => {
	const provider = ref<SyncProvider | null>(null);

	const { data: providerPlaylists, isPending: isProviderPlaylistsLoading } =
		useQuery({
			key: () => ["provider_playlists", provider.value],
			query: async () => {
				if (!provider.value) return [];

				return await queryForProviderPlaylists(provider.value);
			},
		});

	return {
		secondProvider: provider,
		secondProviderPlaylists: providerPlaylists,
		isSecondProviderPlaylistsLoading: isProviderPlaylistsLoading,
	};
});

export const useFirstPlaylistProvider = defineQuery(() => {
	const provider = ref<SyncProvider | null>(null);
	const playlistId = ref<string | null>("");

	const {
		data: providerPlaylist,
		isPending: isProviderPlaylistLoading,
		...rest
	} = useQuery({
		key: () => ["provider_playlist", provider.value, playlistId.value],
		enabled: () => provider.value !== null && playlistId.value !== null,
		query: async () => {
			if (!provider.value || !playlistId.value) return null;

			const res = await client.GET("/api/{provider}/playlists/{playlist_id}", {
				params: {
					path: { provider: provider.value, playlist_id: playlistId.value },
				},
			});

			return res.data;
		},
	});

	return {
		firstPlaylistProvider: provider,
		firstPlaylistId: playlistId,
		firstProviderPlaylist: providerPlaylist,
		isFirstProviderPlaylistLoading: isProviderPlaylistLoading,
		...rest,
	};
});

export const useSecondPlaylistProvider = defineQuery(() => {
	const provider = ref<SyncProvider | null>(null);
	const playlistId = ref<string | null>("");

	const {
		data: providerPlaylist,
		isPending: isProviderPlaylistLoading,
		...rest
	} = useQuery({
		key: () => ["provider_playlist", provider.value, playlistId.value],
		enabled: () => provider.value !== null && playlistId.value !== null,
		query: async () => {
			if (!provider.value || !playlistId.value) return null;

			const res = await client.GET("/api/{provider}/playlists/{playlist_id}", {
				params: {
					path: { provider: provider.value, playlist_id: playlistId.value },
				},
			});

			return res.data;
		},
	});

	return {
		secondPlaylistProvider: provider,
		secondPlaylistId: playlistId,
		secondProviderPlaylist: providerPlaylist,
		isSecondProviderPlaylistLoading: isProviderPlaylistLoading,
		...rest,
	};
});

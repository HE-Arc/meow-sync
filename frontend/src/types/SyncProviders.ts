export const SyncProviders = ["spotify", "youtube_music"] as const;
export type SyncProvider = (typeof SyncProviders)[number];

type SyncProviderInformation = {
	backendRoute: string;
	color: string;
	logoName: string;
	name: string;
};

export const ProvidersInformations: Record<
	SyncProvider,
	SyncProviderInformation
> = {
	spotify: {
		backendRoute: "/auth/spotify",
		color: "#1DB954",
		logoName: "spotify",
		name: "Spotify",
	},
	youtube_music: {
		backendRoute: "/auth/youtube_music",
		color: "#FF0000",
		logoName: "youtube_music",
		name: "YouTube Music",
	},
};

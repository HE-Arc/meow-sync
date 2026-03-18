const API_URL = import.meta.env.VITE_API_URL;

export const SyncProviders = ["spotify", "youtube"] as const;
export type SyncProvider = (typeof SyncProviders)[number];

export type SyncProviderInformation = {
	backendRoute: string;
	color: string;
	icon: string;
	name: string;
};

export const ProvidersInformations: Record<
	SyncProvider,
	SyncProviderInformation
> = {
	spotify: {
		backendRoute: `${API_URL}/auth/spotify`,
		color: "#1DB954",
		icon: "mdi:spotify",
		name: "Spotify",
	},
	youtube: {
		backendRoute: `${API_URL}/auth/youtube_music`,
		color: "#FF0000",
		icon: "mdi:youtube",
		name: "YouTube Music",
	},
};

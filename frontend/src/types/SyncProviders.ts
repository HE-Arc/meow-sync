export const SyncProviders = ["spotify", "youtube"] as const;
export type SyncProvider = (typeof SyncProviders)[number];

export type SyncProviderInformation = {
	color: string;
	icon: string;
	name: string;
};

export const ProvidersInformations: Record<
	SyncProvider,
	SyncProviderInformation
> = {
	spotify: {
		color: "#1DB954",
		icon: "mdi:spotify",
		name: "Spotify",
	},
	youtube: {
		color: "#FF0000",
		icon: "mdi:youtube",
		name: "YouTube Music",
	},
};

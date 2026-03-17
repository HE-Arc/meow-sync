import * as z from "zod";

export const PlaylistSchema = z.object({
	playlist_id: z
		.string("Playlist ID must be a string")
		.min(8, "Playlist ID cannot be less than 8 characters"),
	provider: z.enum(
		["spotify", "youtube"],
		"Provider must be either 'spotify' or 'youtube'",
	),
	title: z
		.string("Title must be a string")
		.min(8, "Title cannot be less than 8 characters"),
	description: z.string("Description must be a string").nullable(),
	author: z.string("Author must be a string"),
	img_url: z.string("Image URL must be a string").nullable(),
});

export type Playlist = z.infer<typeof PlaylistSchema>;

const PLAYLIST_BASE_URL = `${import.meta.env.VITE_API_URL}/playlists`;

async function fetchWithAuth(url: string, options: RequestInit = {}) {
	const token = localStorage.getItem("token");
	if (!token) {
		throw new Error("No access token found");
	}

	const headers = {
		...options.headers,
		Authorization: `Bearer ${token}`,
	};
	const response = await fetch(url, {
		...options,
		headers,
	});

	if (!response.ok) {
		throw new Error(`API request failed: ${response.statusText}`);
	}

	return response;
}

export async function createPlaylist(data: Playlist): Promise<Playlist> {
	const response = await fetchWithAuth(PLAYLIST_BASE_URL, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(data),
	});

	const responseData = await response.json();
	return PlaylistSchema.parse(responseData);
}

export async function getPlaylists(): Promise<Playlist[]> {
	const response = await fetchWithAuth(PLAYLIST_BASE_URL);
	if (!response.ok) {
		throw new Error("Failed to fetch playlists");
	}
	const responseData = await response.json();
	return z.array(PlaylistSchema).parse(responseData);
}

export async function getPlaylistById(playlistId: string): Promise<Playlist> {
	const response = await fetchWithAuth(`${PLAYLIST_BASE_URL}/${playlistId}`);
	if (!response.ok) {
		throw new Error("Failed to fetch playlist");
	}
	const responseData = await response.json();
	return PlaylistSchema.parse(responseData);
}

export async function deletePlaylist(playlistId: string): Promise<void> {
	const response = await fetchWithAuth(`${PLAYLIST_BASE_URL}/${playlistId}`, {
		method: "DELETE",
	});
	if (!response.ok) {
		throw new Error("Failed to delete playlist");
	}
}

export async function updatePlaylist(
	playlistId: string,
	data: Partial<Playlist>,
): Promise<Playlist> {
	const response = await fetchWithAuth(`${PLAYLIST_BASE_URL}/${playlistId}`, {
		method: "PUT",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(data),
	});

	if (!response.ok) {
		throw new Error("Failed to update playlist");
	}

	const responseData = await response.json();
	return PlaylistSchema.parse(responseData);
}

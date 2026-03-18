import * as z from "zod";
import { SyncProviders } from "@/types/SyncProviders";

export const PlaylistSchema = z.object({
	id: z.number("ID must be a number"),
	playlist_id: z
		.string("Playlist ID must be a string")
		.min(3, "Playlist ID cannot be less than 3 characters"),
	provider: z.enum(
		SyncProviders,
		"Provider must be either 'spotify' or 'youtube'",
	),
	title: z
		.string("Title must be a string")
		.min(3, "Title cannot be less than 3 characters"),
	description: z.string("Description must be a string").nullable(),
	author: z.string("Author must be a string"),
	user: z.number("User ID must be a number"),
	img_url: z.string().nullable(),
});

export type Playlist = Omit<PlaylistWithId, "id">;
export type PlaylistWithId = z.infer<typeof PlaylistSchema>;

const PLAYLIST_BASE_URL = `${import.meta.env.VITE_API_URL}/api/playlists`;

async function fetchWithAuth(url: string, options: RequestInit = {}) {
	/*const token = localStorage.getItem("token");
	if (!token) {
		throw new Error("No access token found");
	}*/ //TODO: Re-enable this when the backend is ready to accept the token

	const headers = {
		...options.headers,
		//Authorization: `Bearer ${token}`, //TODO: Re-enable this when the backend is ready to accept the token
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

export async function createPlaylist(data: Playlist): Promise<PlaylistWithId> {
	const response = await fetchWithAuth(`${PLAYLIST_BASE_URL}/`, {
		method: "POST",
		headers: {
			"Content-Type": "application/json",
		},
		body: JSON.stringify(data),
	});

	const responseData = await response.json();
	return PlaylistSchema.parse(responseData);
}

export async function getPlaylists(): Promise<PlaylistWithId[]> {
	const response = await fetchWithAuth(PLAYLIST_BASE_URL);
	if (!response.ok) {
		throw new Error("Failed to fetch playlists");
	}
	const responseData = await response.json();
	return z.array(PlaylistSchema).parse(responseData);
}

export async function getPlaylistById(
	playlistId: number,
): Promise<PlaylistWithId> {
	const response = await fetchWithAuth(`${PLAYLIST_BASE_URL}/${playlistId}/`);
	if (!response.ok) {
		throw new Error("Failed to fetch playlist");
	}
	const responseData = await response.json();
	return PlaylistSchema.parse(responseData);
}

export async function deletePlaylist(playlistId: number): Promise<void> {
	const response = await fetchWithAuth(`${PLAYLIST_BASE_URL}/${playlistId}/`, {
		method: "DELETE",
	});
	if (!response.ok) {
		throw new Error("Failed to delete playlist");
	}
}

export async function updatePlaylist(
	playlistId: number,
	data: Partial<Playlist>,
): Promise<PlaylistWithId> {
	const response = await fetchWithAuth(`${PLAYLIST_BASE_URL}/${playlistId}/`, {
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

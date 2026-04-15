import * as z from "zod";
import { SyncProviders } from "@/types/SyncProviders";
import type { Playlist as ApiPlaylist } from "./client";
import { id } from "zod/v4/locales";

export const PlaylistSchema = z
  .object({
    id: z.number().optional(),
    first_provider: z.enum(SyncProviders, {
      message: "First provider must be 'spotify' or 'youtube'",
    }),
    first_playlist_id: z.string().min(1, "Please select a first playlist"),
    second_provider: z.enum(SyncProviders, {
      message: "Second provider must be 'spotify' or 'youtube'",
    }),
    second_playlist_id: z.string().min(1, "Please select a second playlist"),
  })
  .refine((data) => data.first_provider !== data.second_provider, {
    message: "The two providers must be different",
    path: ["second_provider"],
  });

export type Playlist = Omit<PlaylistWithId, "id">;
export type PlaylistWithId = z.infer<typeof PlaylistSchema>;

// We use this to check that the zod schema matches the API response.
// If there is a type error here, it means that the API response has changed and the zod schema needs to be updated accordingly.
PlaylistSchema.parse({
  id: 1,
  first_playlist_id: "abc123",
  first_provider: "spotify",
  second_playlist_id: "def456",
  second_provider: "youtube",
} as ApiPlaylist);

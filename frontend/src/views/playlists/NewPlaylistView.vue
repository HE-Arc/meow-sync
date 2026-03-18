<script lang="ts" setup>
import type { FormSubmitEvent } from "@nuxt/ui";
import { useToast } from "@nuxt/ui/runtime/composables/useToast.js";
import { type Ref, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import * as z from "zod";
import {
  createPlaylist,
  getPlaylistById,
  getPlaylists,
  type Playlist,
  PlaylistSchema,
  updatePlaylist,
} from "@/api/Playlist";
import { SyncProviders } from "@/types/SyncProviders";

const props = defineProps<{
  isEditMode?: boolean;
}>();

const route = useRoute();
const playlistId = route.params.id as number | undefined;

const schema = z.object({
  playlist_id: z
    .string("Playlist ID must be a string")
    .min(3, "Playlist ID cannot be less than 3 characters"),
  provider: z.enum(
    SyncProviders,
    "Provider must be either 'spotify' or 'youtube'",
  ),
  author: z
    .string("Author must be a string")
    .min(3, "Author name cannot be less than 3 characters"),
  user: z.number("User ID must be a number"), //TODO: Remove this when login works
  title: z
    .string("Title must be a string")
    .min(3, "Title cannot be less than 3 characters"),
  description: z.string("Description must be a string").nullable(),

  img_url: z.url("Image URL must be a valid URL").nullable(),
});

type PlaylistForm = z.infer<typeof schema>;

const isLoading = ref(true);
const toast = useToast();
const router = useRouter();

const state: Ref<PlaylistForm> = ref({
  playlist_id: "",
  provider: "spotify",
  title: "",
  description: null,
  author: "",
  user: 1,
  img_url: null,
} as PlaylistForm);

const providers = ref(
  SyncProviders.map((provider) => ({
    label: provider.charAt(0).toUpperCase() + provider.slice(1),
    value: provider,
  })),
);

async function loadPlaylist() {
  if (props.isEditMode && playlistId) {
    try {
      const data = await getPlaylistById(playlistId);
      state.value = data;
    } catch (error) {
      console.error("Failed to load playlist:", error);
    }
  }
  isLoading.value = false;
}

async function submit(_event: FormSubmitEvent<PlaylistForm>) {
  try {
    if (props.isEditMode && playlistId) {
      await updatePlaylist(playlistId, state.value as Playlist);
    } else {
      await createPlaylist(state.value as Playlist);
    }

    toast?.add({
      title: props.isEditMode
        ? "Playlist updated successfully"
        : "Playlist created successfully",
      color: "green",
    });

    router.push("/playlists");
  } catch (error) {
    console.error("Failed to submit playlist:", error);
    toast?.add({
      title: "Error",
      description: "Failed to save playlist",
      color: "red",
    });
  }
}

loadPlaylist();
</script>

<template>
  <template v-if="isLoading">
    <div
      class="flex items-center justify-center min-h-screen bg-white dark:bg-slate-950"
    >
      <p class="text-lg text-gray-500 dark:text-gray-400">Loading...</p>
    </div>
  </template>
  <div
    v-else
    class="min-h-screen bg-linear-to-br from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900 py-12 px-4"
  >
    <div class="max-w-md mx-auto">
      <div
        class="bg-white dark:bg-slate-900 rounded-lg shadow-lg dark:shadow-xl p-8"
      >
        <h1
          class="text-3xl font-bold mb-2 text-slate-900 dark:text-slate-50 text-center"
        >
          {{ props.isEditMode ? "Edit Playlist" : "Create New Playlist" }}
        </h1>
        <p class="text-slate-500 dark:text-slate-400 mb-8 text-center">
          {{
            props.isEditMode
              ? "Update your playlist details"
              : "Add a new playlist to your collection"
          }}
        </p>

        <UForm
          :schema="schema"
          :state="state"
          @submit="submit"
          class="grid grid-cols-1 md:grid-cols-2 gap-6"
        >
          <UFormField
            label="Playlist ID"
            name="playlist_id"
            class="space-y-2 md:col-span-2"
          >
            <UInput
              v-model="state.playlist_id"
              :disabled="props.isEditMode"
              placeholder="Enter playlist ID"
              size="lg"
              class="w-full"
            />
          </UFormField>

          <UFormField
            label="Title"
            name="title"
            class="space-y-2 md:col-span-2"
          >
            <UInput
              v-model="state.title"
              placeholder="Enter playlist title"
              size="lg"
              class="w-full"
            />
          </UFormField>

          <UFormField label="Author" name="author" class="space-y-2">
            <UInput
              v-model="state.author"
              placeholder="Enter author name"
              size="lg"
              class="w-full"
            />
          </UFormField>

          <UFormField label="User ID" name="user" class="space-y-2">
            <UInput
              v-model="state.user"
              type="number"
              placeholder="Enter user ID"
              size="lg"
              class="w-full"
            />
          </UFormField>

          <UFormField
            label="Description"
            name="description"
            class="space-y-2 md:col-span-2"
          >
            <UTextarea
              :model-value="state.description ?? ''"
              @update:model-value="state.description = $event || null"
              placeholder="Enter playlist description"
              class="w-full"
              :rows="4"
            />
          </UFormField>

          <UFormField
            label="Provider"
            name="provider"
            class="space-y-2 md:col-span-2"
          >
            <USelect
              v-model="state.provider"
              :items="providers"
              placeholder="Select a provider"
              size="lg"
              class="w-full"
            />
          </UFormField>

          <UFormField
            label="Image URL"
            name="img_url"
            class="space-y-2 md:col-span-2"
          >
            <UInput
              :model-value="state.img_url ?? ''"
              @update:model-value="state.img_url = $event || null"
              placeholder="https://example.com/image.jpg"
              size="lg"
              class="w-full"
            />
          </UFormField>

          <div class="md:col-span-2 flex gap-3 pt-2">
            <UButton
              type="submit"
              color="primary"
              size="lg"
              class="flex-1 justify-center"
            >
              {{ props.isEditMode ? "Update Playlist" : "Create Playlist" }}
            </UButton>
          </div>
        </UForm>
      </div>
    </div>
  </div>
</template>

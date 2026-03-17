<script lang="ts" setup>
import type { FormSubmitEvent } from "@nuxt/ui";
import { type Ref, ref } from "vue";
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
  id?: string;
}>();

const isLoading = ref(true);
const toast = useToast();

const state: Ref<Playlist> = ref({
  playlist_id: "",
  provider: "spotify",
  title: "",
  description: "",
  author: "",
  img_url: "",
});

const providers = ref(
  SyncProviders.map((provider) => ({
    label: provider.charAt(0).toUpperCase() + provider.slice(1),
    value: provider,
  })),
);

async function loadPlaylist() {
  if (props.isEditMode) {
    try {
      const data = await getPlaylistById(props.id);
      state.value = data;
    } catch (error) {
      console.error("Failed to load playlist:", error);
    }
  }
  isLoading.value = false;
}

async function submit(event: FormSubmitEvent<Playlist>) {
  toast.add({
    title: props.isEditMode
      ? "Playlist updated successfully"
      : "Playlist created successfully",
  });
}

loadPlaylist();
</script>

<template>
  <template v-if="isLoading">
    <p>Loading...</p>
  </template>
  <div v-else class="flex items-center justify-center flex-col">
    <h1 class="text-2xl font-bold m-4">
      {{ props.isEditMode ? "Edit Playlist" : "Create New Playlist" }}
    </h1>
    <UForm :schema="PlaylistSchema" :state="state" @submit="submit">
      <UFormField label="Playlist ID" name="playlist_id">
        <UInput
          v-model="state.playlist_id"
          :disabled="props.isEditMode"
          placeholder="Enter playlist ID"
        />
      </UFormField>
      <UFormField label="Title" name="title">
        <UInput v-model="state.title" placeholder="Enter playlist title" />
      </UFormField>

      <UFormField label="Author" name="author">
        <UInput v-model="state.author" placeholder="Enter author name" />
      </UFormField>

      <UFormField label="Description" name="description">
        <UTextarea
          v-model="state.description"
          placeholder="Enter playlist description"
        />
      </UFormField>

      <UFormField label="Provider" name="provider">
        <USelect
          v-model="state.provider"
          :items="providers"
          placeholder="Select a provider"
        />
      </UFormField>

      <UFormField label="Image URL" name="img_url" class="mt-2">
        <UInput
          v-model="state.img_url"
          placeholder="https://example.com/image.jpg"
        />
      </UFormField>

      <UButton type="submit" color="primary" class="mt-4">
        {{ props.isEditMode ? "Update Playlist" : "Create Playlist" }}
      </UButton>
    </UForm>
  </div>
</template>

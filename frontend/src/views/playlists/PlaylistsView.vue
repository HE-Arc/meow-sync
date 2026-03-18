<script lang="ts" setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { getPlaylists, type PlaylistWithId } from "@/api/Playlist";

const playlists = ref<PlaylistWithId[]>([]);
const isLoading = ref(true);
const router = useRouter();
const showDeleteModal = ref(false);
const playlistToDelete = ref<PlaylistWithId | null>(null);

async function loadPlaylists() {
  try {
    const data = await getPlaylists();
    playlists.value = data;
  } catch (error) {
    console.error("Failed to load playlists:", error);
  } finally {
    isLoading.value = false;
  }
}

function handleDelete(id: number) {
  playlistToDelete.value = playlists.value.find((p) => p.id === id) || null;
  showDeleteModal.value = true;
}

function handleDeleted() {
  if (playlistToDelete.value) {
    playlists.value = playlists.value.filter(
      (p) => p.id !== playlistToDelete.value?.id,
    );
  }
  playlistToDelete.value = null;
}

loadPlaylists();
</script>

<template>
  <div class="space-y-4 mt-2">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold">Your Playlists</h1>
      <UButton to="/playlists/new" color="primary">Create New Playlist</UButton>
    </div>
    <div v-if="isLoading" class="space-y-4">
      <PlaylistCard v-for="n in 3" :key="n" :isLoading="true" />
    </div>
    <UEmpty
      v-else-if="playlists.length === 0"
      icon="lucide:play"
      title="No paylists found"
      description="It looks like you haven't created any playlists. Create one to get started!"
      :actions="[
        {
          icon: 'lucide:plus',
          label: 'Create Playlist',
          to: '/playlists/new',
        },
      ]"
    />

    <div v-else class="space-y-4">
      <PlaylistCard
        v-for="playlist in playlists"
        class="m-2"
        :key="playlist.playlist_id"
        :playlist="playlist"
        :isLoading="false"
        @click="(id) => router.push(`/playlists/${id}`)"
        @edit="(id) => router.push(`/playlists/${id}/edit`)"
        @delete="(id) => handleDelete(id)"
      />
    </div>

    <DeletePlaylistModal
      :playlist="playlistToDelete"
      :open="showDeleteModal"
      @update:open="showDeleteModal = $event"
      @deleted="handleDeleted"
    />
  </div>
</template>

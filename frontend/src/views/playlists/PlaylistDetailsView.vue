<script lang="ts" setup>
import { type Ref, ref } from "vue";
import { useRouter } from "vue-router";
import { getPlaylistById, type PlaylistWithId } from "@/api/Playlist";

const router = useRouter();

const props = defineProps<{
  id: string;
}>();

const isLoading = ref(true);
const showDeleteModal = ref(false);
const playlistData: Ref<PlaylistWithId | null> = ref(null);

async function loadPlaylist() {
  try {
    const data = await getPlaylistById(Number(props.id));
    playlistData.value = data;
  } catch (error) {
    console.error("Failed to load playlist:", error);
  } finally {
    isLoading.value = false;
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
    <div class="max-w-4xl mx-auto">
      <template v-if="playlistData">
        <div class="flex gap-4 mb-8">
          <div class="flex-1">
            <h1
              class="text-4xl font-bold text-slate-900 dark:text-slate-50 mb-2"
            >
              {{ playlistData.title }}
            </h1>
            <p class="text-lg text-slate-600 dark:text-slate-300">
              by {{ playlistData.author }}
            </p>
          </div>
        </div>

        <div
          class="bg-white dark:bg-slate-900 rounded-lg shadow-lg dark:shadow-xl p-8 mb-8"
        >
          <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <p
                class="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-2"
              >
                Playlist ID
              </p>
              <p
                class="text-lg text-slate-900 dark:text-slate-50 font-mono break-all"
              >
                {{ playlistData.playlist_id }}
              </p>
            </div>

            <div>
              <p
                class="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-2"
              >
                Provider
              </p>
              <div class="flex items-center gap-2">
                <UBadge color="blue" variant="soft">
                  {{ playlistData.provider.toUpperCase() }}
                </UBadge>
              </div>
            </div>

            <div v-if="playlistData.user">
              <p
                class="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-2"
              >
                User ID
              </p>
              <p class="text-lg text-slate-900 dark:text-slate-50">
                {{ playlistData.user }}
              </p>
            </div>
          </div>

          <div
            class="mt-8 pt-8 border-t border-slate-200 dark:border-slate-700"
          >
            <p
              class="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-3"
            >
              Description
            </p>
            <p
              class="text-slate-700 dark:text-slate-300 whitespace-pre-wrap leading-relaxed wrap-break-word"
            >
              {{ playlistData.description || "No description provided" }}
            </p>
          </div>
        </div>

        <div class="flex gap-3">
          <UButton
            @click="router.push(`/playlists/${playlistData.id}/edit`)"
            color="primary"
            size="lg"
            class="flex-1"
            icon="i-heroicons-pencil"
          >
            Edit Playlist
          </UButton>
          <UButton
            @click="showDeleteModal = true"
            color="red"
            variant="soft"
            size="lg"
            class="flex-1"
            icon="i-heroicons-trash"
          >
            Delete Playlist
          </UButton>
        </div>

        <DeletePlaylistModal
          :playlist="playlistData"
          :open="showDeleteModal"
          @update:open="showDeleteModal = $event"
          @deleted="router.replace('/playlists')"
        />
      </template>
      <template v-else>
        <div
          class="bg-white dark:bg-slate-900 rounded-lg shadow-lg p-8 text-center"
        >
          <p class="text-lg text-slate-600 dark:text-slate-300">
            Playlist not found
          </p>
          <UButton
            @click="router.push('/playlists')"
            color="primary"
            class="mt-4"
          >
            Back to Playlists
          </UButton>
        </div>
      </template>
    </div>
  </div>
</template>

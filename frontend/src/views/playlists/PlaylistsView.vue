<script lang="ts" setup>
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import type { PlaylistWithId } from "@/api/Playlist";
import { usePlaylists } from "@/composables/usePlaylist";
import { runSync } from "@/composables/useSync";

const router = useRouter();
const showDeleteModal = ref(false);
const playlistToDelete = ref<PlaylistWithId | null>(null);

const { playlists, isPlaylistsLoading } = usePlaylists();
const { mutateAsync: sync, asyncStatus } = runSync();

const isSyncing = computed(() => asyncStatus.value === "loading");

function handleDelete(id: number) {
    playlistToDelete.value = playlists.value?.find((p) => p.id === id) ?? null;
    showDeleteModal.value = true;
}

async function handleSync(id: number) {
    await sync(id);
}
</script>

<template>
    <div class="space-y-4 mt-2">
        <div class="flex justify-between items-center">
            <h1 class="text-2xl font-bold">Your Playlists</h1>
            <UButton to="/playlists/new" color="primary"
                >Create Sync Pair</UButton
            >
        </div>

        <div v-if="isPlaylistsLoading" class="space-y-4">
            <PlaylistCard
                v-for="n in 3"
                :key="n"
                :isLoading="true"
                :isSyncing="false"
            />
        </div>

        <UEmpty
            v-else-if="!playlists?.length"
            icon="lucide:play"
            title="No sync pairs found"
            description="It looks like you haven't created any playlist sync pairs. Create one to get started!"
            :actions="[
                {
                    icon: 'lucide:plus',
                    label: 'Create Sync Pair',
                    to: '/playlists/new',
                },
            ]"
        />

        <div v-else class="space-y-4">
            <PlaylistCard
                v-for="playlist in playlists"
                :key="playlist.id"
                class="m-2"
                :playlist="playlist"
                :isLoading="false"
                :isSyncing="isSyncing"
                @click="(id: number) => router.push(`/playlists/${id}`)"
                @edit="(id: number) => router.push(`/playlists/${id}/edit`)"
                @delete="(id: number) => handleDelete(id)"
                @sync="(id: number) => handleSync(id)"
            />
        </div>

        <DeletePlaylistModal
            :playlist="playlistToDelete"
            :open="showDeleteModal"
            @update:open="showDeleteModal = $event"
            @deleted="playlistToDelete = null"
        />
    </div>
</template>

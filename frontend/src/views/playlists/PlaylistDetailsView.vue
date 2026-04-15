<script lang="ts" setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { usePlaylist } from "@/composables/usePlaylist";
import { ProvidersInformations } from "@/types/SyncProviders";

const router = useRouter();

const props = defineProps<{
    id: string;
}>();

const { playlistId, playlist, isPlaylistLoading } = usePlaylist();

const firstProvider = computed(() =>
    playlist.value
        ? ProvidersInformations[playlist.value.first_provider]
        : null,
);
const secondProvider = computed(() =>
    playlist.value
        ? ProvidersInformations[playlist.value.second_provider]
        : null,
);

const showDeleteModal = ref(false);

onMounted(() => {
    playlistId.value = Number(props.id);
});

function formatDate(iso: string) {
    return new Date(iso).toLocaleDateString(undefined, {
        year: "numeric",
        month: "long",
        day: "numeric",
    });
}
</script>

<template>
    <template v-if="isPlaylistLoading">
        <div class="flex items-center justify-center min-h-screen">
            <span class="animate-spin">
                <UIcon name="lucide:loader-2" class="text-xl" />
            </span>
            <p>Loading...</p>
        </div>
    </template>
    <div v-else class="py-12 px-4">
        <div class="max-w-2xl mx-auto">
            <template v-if="playlist">
                <!-- Header -->
                <div class="flex items-center gap-3 mb-8">
                    <UButton
                        icon="lucide:arrow-left"
                        color="neutral"
                        variant="ghost"
                        @click="router.push('/playlists')"
                    />
                    <h1
                        class="text-3xl font-bold text-slate-900 dark:text-slate-50"
                    >
                        Sync Pair
                    </h1>
                </div>

                <!-- Sync pair card -->
                <div
                    class="bg-white dark:bg-slate-900 rounded-lg shadow-lg dark:shadow-xl p-8 mb-6"
                >
                    <div class="flex items-center justify-around gap-6">
                        <!-- First provider -->
                        <div
                            class="flex flex-col items-center gap-3 flex-1 min-w-0"
                        >
                            <UIcon
                                v-if="firstProvider"
                                :name="firstProvider.icon"
                                class="text-5xl"
                                :style="{ color: firstProvider.color }"
                            />
                            <p
                                class="text-base font-semibold text-slate-900 dark:text-slate-50"
                            >
                                {{ firstProvider?.name }}
                            </p>
                            <p
                                class="text-xs text-slate-500 dark:text-slate-400 font-mono break-all text-center"
                            >
                                {{ playlist.first_playlist_id }}
                            </p>
                        </div>

                        <!-- Sync icon -->
                        <UIcon
                            name="lucide:arrow-left-right"
                            class="text-3xl text-slate-400 shrink-0"
                        />

                        <!-- Second provider -->
                        <div
                            class="flex flex-col items-center gap-3 flex-1 min-w-0"
                        >
                            <UIcon
                                v-if="secondProvider"
                                :name="secondProvider.icon"
                                class="text-5xl"
                                :style="{ color: secondProvider.color }"
                            />
                            <p
                                class="text-base font-semibold text-slate-900 dark:text-slate-50"
                            >
                                {{ secondProvider?.name }}
                            </p>
                            <p
                                class="text-xs text-slate-500 dark:text-slate-400 font-mono break-all text-center"
                            >
                                {{ playlist.second_playlist_id }}
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Metadata -->
                <div
                    class="bg-white dark:bg-slate-900 rounded-lg shadow-lg dark:shadow-xl p-6 mb-6"
                >
                    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
                        <div v-if="playlist.user">
                            <p
                                class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1"
                            >
                                Owner
                            </p>
                            <p
                                class="text-sm text-slate-900 dark:text-slate-50"
                            >
                                {{ playlist.user }}
                            </p>
                        </div>
                        <div v-if="playlist.created_at">
                            <p
                                class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1"
                            >
                                Created
                            </p>
                            <p
                                class="text-sm text-slate-900 dark:text-slate-50"
                            >
                                {{ formatDate(playlist.created_at) }}
                            </p>
                        </div>
                        <div v-if="playlist.updated_at">
                            <p
                                class="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide mb-1"
                            >
                                Last updated
                            </p>
                            <p
                                class="text-sm text-slate-900 dark:text-slate-50"
                            >
                                {{ formatDate(playlist.updated_at) }}
                            </p>
                        </div>
                    </div>
                </div>

                <!-- Actions -->
                <div class="flex gap-3">
                    <UButton
                        @click="router.push(`/playlists/${playlist.id}/edit`)"
                        color="primary"
                        size="lg"
                        class="flex-1"
                        icon="lucide:pen"
                    >
                        Edit
                    </UButton>
                    <UButton
                        @click="showDeleteModal = true"
                        color="error"
                        variant="soft"
                        size="lg"
                        class="flex-1"
                        icon="lucide:trash-2"
                    >
                        Delete
                    </UButton>
                </div>

                <DeletePlaylistModal
                    :playlist="playlist"
                    :open="showDeleteModal"
                    @update:open="showDeleteModal = $event"
                    @deleted="router.replace('/playlists')"
                />
            </template>

            <!-- Not found -->
            <template v-else>
                <div
                    class="bg-white dark:bg-slate-900 rounded-lg shadow-lg p-8 text-center"
                >
                    <p class="text-lg text-slate-600 dark:text-slate-300 mb-4">
                        Sync pair not found
                    </p>
                    <UButton @click="router.push('/playlists')" color="primary">
                        Back to Playlists
                    </UButton>
                </div>
            </template>
        </div>
    </div>
</template>

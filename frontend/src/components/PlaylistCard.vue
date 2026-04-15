<script lang="ts" setup>
import { computed } from "vue";
import type { PlaylistWithId } from "@/api/Playlist";
import { ProvidersInformations } from "@/types/SyncProviders";
import { usePlaylistProvider } from "@/composables/usePlaylistProvider";

defineEmits<{
    (e: "click", id: number): void;
    (e: "sync", id: number): void;
    (e: "edit", id: number): void;
    (e: "delete", id: number): void;
}>();

const props = defineProps<{
    playlist?: PlaylistWithId;
    isLoading: boolean;
    isSyncing: boolean;
}>();

const firstProvider = computed(() =>
    props.playlist
        ? ProvidersInformations[props.playlist.first_provider]
        : null,
);

const secondProvider = computed(() =>
    props.playlist
        ? ProvidersInformations[props.playlist.second_provider]
        : null,
);

const {
    providerPlaylist: firstProviderPlaylist,
    isProviderPlaylistLoading: isFirstProviderPlaylistLoading,
} = usePlaylistProvider(
    props.playlist?.first_provider ?? "spotify",
    props.playlist?.first_playlist_id ?? "",
);
const {
    providerPlaylist: secondProviderPlaylist,
    isProviderPlaylistLoading: isSecondProviderPlaylistLoading,
} = usePlaylistProvider(
    props.playlist?.second_provider ?? "spotify",
    props.playlist?.second_playlist_id ?? "",
);

const isLoadingInternal = computed(
    () =>
        props.isLoading ||
        isFirstProviderPlaylistLoading.value ||
        isSecondProviderPlaylistLoading.value,
);

const firstPlaylistName = computed(
    () =>
        firstProviderPlaylist.value?.data.title ||
        props.playlist?.first_playlist_id,
);
const secondPlaylistName = computed(
    () =>
        secondProviderPlaylist.value?.data.title ||
        props.playlist?.second_playlist_id,
);
</script>

<template>
    <template v-if="isLoadingInternal">
        <USkeleton class="w-full h-16" />
    </template>
    <template v-else>
        <div
            class="flex items-center gap-4 shadow rounded-lg p-4 bg-white hover:bg-gray-50 cursor-pointer dark:bg-slate-800 dark:hover:bg-slate-700"
            @click="$emit('click', playlist?.id || 0)"
        >
            <!-- Sync pair display -->
            <div class="flex items-center gap-3 flex-1 min-w-0">
                <!-- First provider -->
                <div class="flex items-center gap-2 min-w-0">
                    <UIcon
                        v-if="firstProvider"
                        :name="firstProvider.icon"
                        class="text-2xl shrink-0"
                        :style="{ color: firstProvider.color }"
                    />
                    <div class="min-w-0 hidden sm:block">
                        <p class="text-sm font-semibold leading-tight">
                            {{ firstProvider?.name }}
                        </p>
                        <p
                            class="text-xs text-gray-500 dark:text-gray-400 font-mono truncate max-w-32"
                        >
                            {{ firstPlaylistName }}
                        </p>
                    </div>
                </div>

                <!-- Sync arrow -->
                <UIcon
                    name="lucide:arrow-left-right"
                    class="text-base text-gray-400 shrink-0"
                />

                <!-- Second provider -->
                <div class="flex items-center gap-2 min-w-0">
                    <UIcon
                        v-if="secondProvider"
                        :name="secondProvider.icon"
                        class="text-2xl shrink-0"
                        :style="{ color: secondProvider.color }"
                    />
                    <div class="min-w-0 hidden sm:block">
                        <p class="text-sm font-semibold leading-tight">
                            {{ secondProvider?.name }}
                        </p>
                        <p
                            class="text-xs text-gray-500 dark:text-gray-400 font-mono truncate max-w-32"
                        >
                            {{ secondPlaylistName }}
                        </p>
                    </div>
                </div>
            </div>

            <!-- Actions -->
            <div class="ml-auto flex gap-2 shrink-0">
                <UButton
                    class="cursor-pointer"
                    size="sm"
                    icon="lucide:refresh-cw"
                    @click.stop="$emit('sync', playlist?.id || 0)"
                    :loading="isSyncing"
                >
                    Sync
                </UButton>
                <UButton
                    class="cursor-pointer"
                    size="sm"
                    icon="lucide:pen"
                    @click.stop="$emit('edit', playlist?.id || 0)"
                >
                    Edit
                </UButton>
                <UButton
                    color="error"
                    class="cursor-pointer"
                    size="sm"
                    icon="lucide:trash-2"
                    @click.stop="$emit('delete', playlist?.id || 0)"
                >
                    Delete
                </UButton>
            </div>
        </div>
    </template>
</template>

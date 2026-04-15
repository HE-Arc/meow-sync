<script lang="ts" setup>
import type { FormSubmitEvent } from "@nuxt/ui";
import { computed, onMounted, type Ref, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { PlaylistSchema, type PlaylistWithId } from "@/api/Playlist";
import {
    createPlaylist,
    usePlaylist,
    useUpdatePlaylist,
} from "@/composables/usePlaylist";
import {
    useFirstProviderPlaylists,
    useSecondProviderPlaylists,
} from "@/composables/usePlaylistProvider";
import {
    ProvidersInformations,
    type SyncProvider,
    SyncProviders,
} from "@/types/SyncProviders";

const props = defineProps<{
    isEditMode?: boolean;
}>();

const route = useRoute();
const router = useRouter();

const state: Ref<PlaylistWithId> = ref({
    id: route.params.id ? Number(route.params.id) : undefined,
    first_provider: "spotify",
    first_playlist_id: "",
    second_provider: "youtube",
    second_playlist_id: "",
});

const first_selected_provider = computed(() => state.value.first_provider);
const second_selected_provider = computed(() => state.value.second_provider);

const providers = SyncProviders.map((p) => ({
    label: ProvidersInformations[p].name,
    value: p,
    icon: ProvidersInformations[p].icon,
}));

// Provider playlist selection (not yet implemented in backend)
const {
    firstProvider,
    firstProviderPlaylists,
    isFirstProviderPlaylistsLoading,
} = useFirstProviderPlaylists();
const {
    secondProvider,
    secondProviderPlaylists,
    isSecondProviderPlaylistsLoading,
} = useSecondProviderPlaylists();

// Load existing data in edit mode
const {
    playlistId: playlistQueryId,
    playlist,
    isPlaylistLoading,
} = usePlaylist();

watch(
    playlist,
    (data) => {
        if (data && props.isEditMode) {
            state.value = {
                first_provider: data.first_provider,
                first_playlist_id: data.first_playlist_id,
                second_provider: data.second_provider,
                second_playlist_id: data.second_playlist_id,
            };
        }
    },
    { immediate: true },
);

onMounted(() => {
    if (props.isEditMode && state.value.id) {
        playlistQueryId.value = state.value.id;
    }
});

watch(
    first_selected_provider,
    (newProvider) => {
        // Clear the selected playlist when the provider changes
        state.value.first_playlist_id = "";
        firstProvider.value = newProvider;
    },
    { immediate: true },
);

watch(
    second_selected_provider,
    (newProvider) => {
        // Clear the selected playlist when the provider changes
        state.value.second_playlist_id = "";
        secondProvider.value = newProvider;
    },
    { immediate: true },
);

// Mutations
const { mutateAsync: create, asyncStatus: createStatus } = createPlaylist();
const { mutateAsync: update, asyncStatus: updateStatus } = useUpdatePlaylist();

// Computed values
const isLoading = computed(
    () =>
        (props.isEditMode && isPlaylistLoading.value) ||
        (!props.isEditMode &&
            isFirstProviderPlaylistsLoading.value &&
            isSecondProviderPlaylistsLoading.value),
);

const isSubmitting = computed(
    () => createStatus.value === "loading" || updateStatus.value === "loading",
);

async function submit(_event: FormSubmitEvent<PlaylistWithId>) {
    if (props.isEditMode && state.value.id) {
        await update({ id: state.value.id, data: state.value });
    } else {
        await create(state.value);
    }
    router.push("/playlists");
}
</script>

<template>
    <div v-if="isLoading" class="flex items-center justify-center">
        <span class="animate-spin">
            <UIcon name="lucide:loader-2" class="text-xl" />
        </span>
        <p>Loading...</p>
    </div>
    <div v-else>
        <div class="max-w-lg mx-auto">
            <div
                class="bg-white dark:bg-slate-900 rounded-lg shadow-lg dark:shadow-xl p-8"
            >
                <h1
                    class="text-3xl font-bold mb-2 text-slate-900 dark:text-slate-50 text-center"
                >
                    {{
                        props.isEditMode ? "Edit Sync Pair" : "Create Sync Pair"
                    }}
                </h1>
                <p class="text-slate-500 dark:text-slate-400 mb-8 text-center">
                    {{
                        props.isEditMode
                            ? "Update the playlists to synchronize"
                            : "Choose two playlists to keep in sync"
                    }}
                </p>

                <UForm
                    :schema="PlaylistSchema"
                    :state="state"
                    @submit="submit"
                    class="space-y-6"
                >
                    <!-- First provider -->
                    <div
                        class="rounded-lg border border-slate-200 dark:border-slate-700 p-4 space-y-4"
                    >
                        <p
                            class="text-sm font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wide"
                        >
                            First Playlist
                        </p>

                        <UFormField label="Provider" name="first_provider">
                            <USelect
                                v-model="state.first_provider"
                                :items="providers"
                                size="lg"
                                class="w-full"
                            />
                        </UFormField>

                        <UFormField label="Playlist" name="first_playlist_id">
                            <USelect
                                v-model="state.first_playlist_id"
                                :items="firstProviderPlaylists"
                                size="lg"
                                class="w-full"
                                :loading="isFirstProviderPlaylistsLoading"
                                :disabled="isFirstProviderPlaylistsLoading"
                            />
                        </UFormField>
                    </div>

                    <!-- Sync arrow divider -->
                    <div class="flex items-center justify-center">
                        <UIcon
                            name="lucide:arrow-down-up"
                            class="text-2xl text-slate-400"
                        />
                    </div>

                    <!-- Second provider -->
                    <div
                        class="rounded-lg border border-slate-200 dark:border-slate-700 p-4 space-y-4"
                    >
                        <p
                            class="text-sm font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wide"
                        >
                            Second Playlist
                        </p>

                        <UFormField label="Provider" name="second_provider">
                            <USelect
                                v-model="state.second_provider"
                                :items="providers"
                                size="lg"
                                class="w-full"
                            />
                        </UFormField>

                        <UFormField label="Playlist" name="second_playlist_id">
                            <USelect
                                v-model="state.second_playlist_id"
                                :items="secondProviderPlaylists"
                                size="lg"
                                class="w-full"
                                :loading="isSecondProviderPlaylistsLoading"
                                :disabled="isSecondProviderPlaylistsLoading"
                            />
                        </UFormField>
                    </div>

                    <div class="flex gap-3 pt-2">
                        <UButton
                            type="button"
                            color="neutral"
                            variant="outline"
                            size="lg"
                            class="flex-1 justify-center"
                            @click="router.push('/playlists')"
                        >
                            Cancel
                        </UButton>
                        <UButton
                            type="submit"
                            color="primary"
                            size="lg"
                            class="flex-1 justify-center"
                            :loading="isSubmitting || isLoading"
                        >
                            {{ props.isEditMode ? "Update" : "Create" }}
                        </UButton>
                    </div>
                </UForm>
            </div>
        </div>
    </div>
</template>

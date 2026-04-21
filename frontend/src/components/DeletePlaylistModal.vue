<script setup lang="ts">
import { computed } from "vue";
import type { PlaylistWithId } from "@/api/Playlist";
import { useDeletePlaylist } from "@/composables/usePlaylist";

interface Props {
    playlist: PlaylistWithId | null;
    open: boolean;
}

interface Emits {
    (e: "update:open", value: boolean): void;
    (e: "deleted"): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const { mutateAsync, asyncStatus } = useDeletePlaylist();
const isDeleting = computed(() => asyncStatus.value === "loading");

async function handleDelete() {
    if (!props.playlist) return;
    await mutateAsync(props.playlist.id ?? -1);
    emit("deleted");
    emit("update:open", false);
}
</script>

<template>
    <UModal
        :open="open"
        @update:open="(value: boolean) => emit('update:open', value)"
        title="Delete Playlist"
        description="This action cannot be undone. Are you sure you want to delete this playlist?"
        :ui="{ footer: 'justify-end gap-3' }"
    >
        <template #footer="{ close }">
            <UButton
                color="neutral"
                variant="outline"
                @click="close"
                :disabled="isDeleting"
            >
                Cancel
            </UButton>
            <UButton color="error" @click="handleDelete" :loading="isDeleting">
                Delete
            </UButton>
        </template>
    </UModal>
</template>

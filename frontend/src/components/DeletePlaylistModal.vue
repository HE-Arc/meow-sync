<script setup lang="ts">
import { useToast } from "@nuxt/ui/runtime/composables/useToast.js";
import { ref } from "vue";
import { deletePlaylist, type PlaylistWithId } from "@/api/Playlist";

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

const toast = useToast();
const isDeleting = ref(false);

async function handleDelete() {
  if (!props.playlist) return;

  isDeleting.value = true;
  try {
    await deletePlaylist(props.playlist.id);
    toast?.add({
      title: "Success",
      description: "Playlist deleted successfully",
      color: "green",
    });
    emit("deleted");
    emit("update:open", false);
  } catch (error) {
    console.error("Failed to delete playlist:", error);
    toast?.add({
      title: "Error",
      description: "Failed to delete playlist",
      color: "red",
    });
  } finally {
    isDeleting.value = false;
  }
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

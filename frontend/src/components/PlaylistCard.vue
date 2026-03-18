<script lang="ts" setup>
import { computed } from "vue";
import type { PlaylistWithId } from "@/api/Playlist";

defineEmits<{
  (e: "click", id: number): void;
  (e: "edit", id: number): void;
  (e: "delete", id: number): void;
}>();
const props = defineProps<{
  playlist?: PlaylistWithId;
  isLoading: boolean;
}>();

const playlistImage = computed(() => {
  return props.playlist?.img_url || "/default_playlist_image.png";
});

const truncatedDescription = computed(() => {
  const description = props.playlist?.description;
  if (!description) return "";
  const maxLength = 60;
  return description.length > maxLength
    ? `${description.substring(0, maxLength)}...`
    : description;
});
</script>

<template>
  <template v-if="isLoading">
    <USkeleton class="w-full h-10" />
  </template>
  <template v-else>
    <div
      class="flex items-center gap-4 shadow rounded-lg p-4 bg-white hover:bg-gray-50 cursor-pointer dark:bg-slate-800 dark:hover:bg-slate-700"
      @click="$emit('click', playlist?.id || 0)"
    >
      <UAvatar
        :src="playlistImage"
        size="lg"
        :alt="playlist?.title"
        class="rounded-sm"
      />
      <div>
        <h2 class="text-lg font-semibold">{{ playlist?.title }}</h2>
        <p class="text-sm text-gray-500">{{ truncatedDescription }}</p>
      </div>
      <div class="ml-auto flex gap-2">
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

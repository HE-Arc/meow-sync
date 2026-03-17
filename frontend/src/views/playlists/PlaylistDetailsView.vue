<script lang="ts" setup>
import { type Ref, ref } from "vue";
import { useRouter } from "vue-router";
import { getPlaylistById, type Playlist } from "@/api/Playlist";

const router = useRouter();
const props = defineProps<{
  id: string;
}>();

const isLoading = ref(true);
const playlistData: Ref<Playlist | null> = ref(null);
</script>
<template>
  <template v-if="isLoading">
    <p>Loading...</p>
  </template>
  <template v-else-if="playlistData">
    <h1 class="text-2xl font-bold mb-4">{{ playlistData.title }}</h1>
    <p>{{ playlistData.description }}</p>
  </template>
</template>

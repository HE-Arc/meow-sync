<script setup lang="ts">
import type { NavigationMenuItem } from "@nuxt/ui";
import { defineShortcuts } from "@nuxt/ui/runtime/composables/defineShortcuts.js";
import { computed } from "vue";
import { RouterLink, RouterView, useRoute, useRouter } from "vue-router";
import AppIconWithText from "./components/icons/AppIconWithText.vue";

const route = useRoute();
const router = useRouter();

const items = computed<NavigationMenuItem[]>(() => [
  {
    label: "Playlists",
    icon: "lucide:play",
    to: "/playlists",
    active: route.path.startsWith("/playlists"),
    tooltip: {
      text: "View your playlists",
      kbds: ["meta", "P"],
    },
  },
]);

defineShortcuts({
  meta_G: () => window.open("https://github.com/He-Arc/meow-sync", "_blank"),
  meta_H: () => router.push("/"),
  meta_J: () => document.querySelector("html")?.classList.toggle("dark"),
  meta_P: () => router.push("/playlists"),
});
</script>

<template>
  <Suspense>
    <UApp>
      <UHeader>
        <template #title>
          <UTooltip text="Go to home" :kbds="['meta', 'H']">
            <RouterLink to="/">
              <AppIconWithText />
            </RouterLink>
          </UTooltip>
        </template>

        <UNavigationMenu :items="items" />

        <template #right>
          <UTooltip text="Toggle color mode" :kbds="['meta', 'J']">
            <UColorModeButton />
          </UTooltip>

          <UTooltip text="Open on GitHub" :kbds="['meta', 'G']">
            <UButton
              color="neutral"
              variant="ghost"
              to="https://github.com/He-Arc/meow-sync"
              target="_blank"
              icon="mdi:github"
              aria-label="GitHub"
            />
          </UTooltip>
        </template>
        <template #body>
          <UNavigationMenu
            :items="items"
            orientation="vertical"
            class="-mx-2.5"
          />
        </template>
      </UHeader>

      <UMain class="flex w-screen">
        <RouterView class="w-full" />
      </UMain>

      <UFooter>
        <p class="text-center text-sm text-gray-500">
          &copy; {{ new Date().getFullYear() }} Haute-Ecole Arc. All rights
          reserved.
        </p>
      </UFooter>
    </UApp>
  </Suspense>
</template>

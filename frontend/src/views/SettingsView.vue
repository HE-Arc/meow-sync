<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import {
  type ProviderEnum,
  useApiToken,
  useDisconnectProvider,
  useGetLoginUrlAndRedirect,
} from "@/composables/useAuth";
import { useUserInfo } from "@/composables/useUserInfo";
import {
  ProvidersInformations,
  type SyncProvider,
  SyncProviders,
} from "@/types/SyncProviders";

const router = useRouter();
const { setToken } = useApiToken();
const { login } = useGetLoginUrlAndRedirect();
const { disconnect, isDisconnecting } = useDisconnectProvider();
const { user, isUserLoading, refetchUser } = useUserInfo();

const pendingDisconnect = ref<SyncProvider | null>(null);

function openConfirm(provider: SyncProvider) {
  pendingDisconnect.value = provider;
}

async function confirmDisconnect() {
  if (!pendingDisconnect.value) return;
  await disconnect(pendingDisconnect.value as ProviderEnum);
  await refetchUser();
  pendingDisconnect.value = null;
}

function connectionFor(provider: SyncProvider) {
  if (!user.value || !user.value.connections) return undefined;
  return user.value.connections.find((conn) => conn.provider === provider);
}

async function logout() {
  setToken(null);
  router.push("/");
}
</script>

<template>
  <div class="max-w-xl mx-auto px-4 py-8 flex flex-col gap-6">
    <h1 class="text-2xl font-bold">Settings</h1>

    <!-- User card -->
    <USkeleton v-if="isUserLoading" class="h-24 w-full rounded-lg" />
    <UCard v-else-if="user">
      <div class="flex items-center gap-4">
        <UAvatar :alt="user.username" size="lg" />
        <div>
          <p class="font-semibold">{{ user.username }}</p>
          <p class="text-sm text-gray-500">{{ user.email }}</p>
        </div>
      </div>
    </UCard>

    <!-- Providers -->
    <div class="flex flex-col gap-3">
      <h2 class="text-lg font-semibold">Connected accounts</h2>

      <USkeleton
        v-if="isUserLoading"
        v-for="i in SyncProviders.length"
        :key="i"
        class="h-16 w-full rounded-lg"
      />

      <UCard v-else v-for="provider in SyncProviders" :key="provider">
        <div class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-3">
            <UIcon
              :name="ProvidersInformations[provider].icon"
              class="text-2xl"
              :style="{ color: ProvidersInformations[provider].color }"
            />
            <div>
              <p class="font-medium">
                {{ ProvidersInformations[provider].name }}
              </p>
              <p v-if="connectionFor(provider)" class="text-sm text-gray-500">
                {{ connectionFor(provider)?.provider_user_id }}
              </p>
              <p v-else class="text-sm text-gray-400">Not linked</p>
            </div>
          </div>

          <UButton
            v-if="connectionFor(provider)"
            color="error"
            variant="outline"
            size="sm"
            :disabled="(user?.connections.length ?? 0) <= 1"
            @click="openConfirm(provider)"
          >
            Unlink
          </UButton>
          <UButton v-else variant="outline" size="sm" @click="login(provider)">
            Link account
          </UButton>
        </div>
      </UCard>
    </div>

    <UButton
      color="error"
      variant="outline"
      icon="lucide:log-out"
      class="self-start"
      @click="logout"
    >
      Log out
    </UButton>
  </div>

  <!-- Unlink confirmation modal -->
  <UModal
    :open="!!pendingDisconnect"
    @update:open="
      (v: boolean) => {
        if (!v) pendingDisconnect = null;
      }
    "
  >
    <template #content>
      <div class="p-6 flex flex-col gap-4">
        <div class="flex items-center gap-3">
          <UIcon
            v-if="pendingDisconnect"
            :name="ProvidersInformations[pendingDisconnect].icon"
            class="text-2xl"
            :style="{ color: ProvidersInformations[pendingDisconnect].color }"
          />
          <h3 class="text-lg font-semibold">
            Unlink
            {{
              pendingDisconnect
                ? ProvidersInformations[pendingDisconnect].name
                : ""
            }}
          </h3>
        </div>
        <p class="text-sm text-gray-500">
          Are you sure you want to unlink your
          <strong>{{
            pendingDisconnect
              ? ProvidersInformations[pendingDisconnect].name
              : ""
          }}</strong>
          account? You will need to re-authenticate to use it again.
        </p>
        <div class="flex justify-end gap-2">
          <UButton variant="outline" @click="pendingDisconnect = null"
            >Cancel</UButton
          >
          <UButton
            color="error"
            :loading="isDisconnecting"
            @click="confirmDisconnect"
          >
            Unlink
          </UButton>
        </div>
      </div>
    </template>
  </UModal>
</template>

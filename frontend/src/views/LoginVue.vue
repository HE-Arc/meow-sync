<script setup lang="ts">
import LoginSpotifyBtn from '../components/LoginSpotifyBtn.vue';
import LoginYoutubeBtn from '../components/LoginYoutubeBtn.vue';
</script>

<template>
  <div class="login">
    <h1>This is a login page</h1>
    <LoginSpotifyBtn/>
    <LoginYoutubeBtn/>
  </div>
</template>

<style>
@media (min-width: 1024px) {
  .login {
    min-height: 100vh;
    display: flex;
    align-items: center;
  }
}
</style>

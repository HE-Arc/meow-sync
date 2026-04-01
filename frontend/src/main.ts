import "./assets/main.css";

import ui from "@nuxt/ui/vue-plugin";
import { PiniaColada } from "@pinia/colada";
import { createPinia } from "pinia";
import { createApp } from "vue";
import App from "./App.vue";
import { authMiddleware, client, unauthorizedMiddleware } from "./api/client";
import router from "./router";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(PiniaColada);
app.use(router);
app.use(ui);

// Register API middlewares after pinia is installed so stores are available
client.use(authMiddleware);
client.use(unauthorizedMiddleware);

app.mount("#app");

import "./assets/main.css";

import { useToast } from "@nuxt/ui/runtime/composables/useToast.js";
import ui from "@nuxt/ui/vue-plugin";
import { PiniaColada, PiniaColadaQueryHooksPlugin } from "@pinia/colada";
import { createPinia } from "pinia";
import { createApp } from "vue";
import App from "./App.vue";
import {
	ApiError,
	authMiddleware,
	client,
	throwOnErrorMiddleware,
	unauthorizedMiddleware,
} from "./api/client";
import router from "./router";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.use(ui);
app.use(PiniaColada, {
	plugins: [
		PiniaColadaQueryHooksPlugin({
			onError(error, _entry) {
				const toast = useToast();
				if (error instanceof ApiError) {
					const errorDetails = error.errors
						.map((e) => `${e.attr ?? "non_field_error"}: ${e.detail}`)
						.join("\n");
					toast.add({
						title: `Error ${error.status}`,
						description: errorDetails || "An error occurred.",
						color: "error",
					});
				} else {
					toast.add({
						title: "Error",
						description: "An error occurred while processing your request.",
						color: "error",
					});
				}
			},
		}),
	],
});
// Register API middlewares after pinia is installed so stores are available
client.use(authMiddleware);
client.use(unauthorizedMiddleware);
client.use(throwOnErrorMiddleware);

// Restore user session if a token is already stored
app.mount("#app");

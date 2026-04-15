import "./assets/main.css";

import { useToast } from "@nuxt/ui/runtime/composables/useToast.js";
import ui from "@nuxt/ui/vue-plugin";
import { PiniaColada, PiniaColadaQueryHooksPlugin } from "@pinia/colada";
import { createPinia } from "pinia";
import { createApp } from "vue";
import { useRouter } from "vue-router";
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
function handleError(error: unknown) {
	const toast = useToast();
	const router = useRouter();

	if (error instanceof ApiError) {
		if (error.status === 404) {
			router.push("/404");
			return;
		}
		const errorDetails = error.errors
			.map((e) => `${e.attr ?? "non_field_error"}: ${e.detail}`)
			.join("\n");
		toast.add({
			title: `Error ${error.status}`,
			icon: "lucide:octagon-x",
			description: errorDetails || "An error occurred.",
			color: "error",
		});
	} else if (error instanceof TypeError) {
		if (error.message.includes("NetworkError")) {
			toast.add({
				title: "Error",
				icon: "lucide:wifi-off",
				description: "Failed to contact backend server.",
				color: "error",
			});
		} else {
			toast.add({
				title: "Error",
				icon: "lucide:octagon-x",
				description: error.message,
				color: "error",
			});
			console.error("An unexpected error occurred:", error);
		}
	} else {
		console.error("An unexpected error occurred:", error);
		toast.add({
			title: "Error",
			icon: "lucide:octagon-x",
			description: "An unexpected error occurred.",
			color: "error",
		});
	}
}

app.use(PiniaColada, {
	plugins: [
		PiniaColadaQueryHooksPlugin({
			onError(error, _entry) {
				console.error("Query error:", error);
				handleError(error);
			},
		}),
	],
	mutationOptions: {
		onError(error) {
			console.error("Mutation error:", error);
			handleError(error);
		},
	},
});
// Register API middlewares after pinia is installed so stores are available
client.use(authMiddleware);
client.use(unauthorizedMiddleware);
client.use(throwOnErrorMiddleware);

// Restore user session if a token is already stored
app.mount("#app");

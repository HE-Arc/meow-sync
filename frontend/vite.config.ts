import { fileURLToPath, URL } from "node:url";
import ui from "@nuxt/ui/vite";
import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";
import vueDevTools from "vite-plugin-vue-devtools";
import djangoBackendSync from "./vite-plugin-django-backend-sync";

// https://vite.dev/config/
export default defineConfig({
	plugins: [djangoBackendSync(), vue(), ui(), vueDevTools()],
	resolve: {
		alias: {
			"@": fileURLToPath(new URL("./src", import.meta.url)),
		},
	},
	server: {
		// port: 8000, // for spotify login callback
	},
});

import { existsSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath, URL } from "node:url";
import ui from "@nuxt/ui/vite";
import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";
import vueDevTools from "vite-plugin-vue-devtools";
import djangoBackendSync from "./vite-plugin-openapi-sync";

// https://vite.dev/config/
export default defineConfig({
	plugins: [
		djangoBackendSync({
			backendCommand: "uv run manage.py spectacular",
			isBackendCorrect: (backendPath) =>
				["manage.py", "uv.lock"].every((file) =>
					existsSync(join(backendPath, file)),
				),
			typeOutputPath: "src/api/schema.d.ts",
		}),
		vue(),
		ui(),
		vueDevTools(),
	],
	resolve: {
		alias: {
			"@": fileURLToPath(new URL("./src", import.meta.url)),
		},
	},
	server: {
		// port: 8000, // for spotify login callback
	},
});

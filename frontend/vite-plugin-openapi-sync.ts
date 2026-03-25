import { existsSync } from "node:fs";
import { resolve } from "node:path";
import parcel, { type AsyncSubscription } from "@parcel/watcher";
import type { Plugin, ViteDevServer } from "vite";
import { generateSchema, generateTypes } from "./utils/schema";

interface PluginOptions {
	backendDir?: string;
	typeOutputPath?: string;
	watchBackend?: boolean;
	backendCommand: string;
	isBackendCorrect: (backendPath: string) => boolean;
}

export default function djangoBackendSync(options: PluginOptions): Plugin {
	const {
		backendDir = "../api",
		typeOutputPath = "src/api/schema.d.ts",
		watchBackend = true,
		backendCommand,
		isBackendCorrect,
	} = options;

	const rootDir = process.cwd();
	const backendPath = resolve(rootDir, backendDir);
	const typesPath = resolve(rootDir, typeOutputPath);

	let server: ViteDevServer | undefined;
	let isGenerating = false;
	let watcher: AsyncSubscription | null = null;
	let debounceTimer: NodeJS.Timeout | null = null;

	function log(_logLevel: "info" | "warn" | "error", message: string) {
		const prefix = `[openapi-sync] ${_logLevel.toUpperCase()}:`;
		const time = new Date().toLocaleTimeString();

		console.log(`${time} ${prefix} ${message}`);
	}

	function checkAndGenerateSchema(): string | null {
		if (!isBackendCorrect(backendPath)) {
			log(
				"error",
				`Backend not found or incorrect at path: ${backendPath}. Check your configuration.`,
			);
			return null;
		}

		return generateSchema(backendPath, backendCommand);
	}

	async function regenerateAndReload() {
		if (isGenerating) return;
		isGenerating = true;

		try {
			const schemaGenerated = checkAndGenerateSchema();
			if (schemaGenerated) {
				await generateTypes(schemaGenerated, typesPath);

				if (server) {
					server.ws.send({
						type: "full-reload",
					});
					log(
						"info",
						`backend changed: Reloaded server after schema regeneration`,
					);
				}
			}
		} catch (error) {
			log(
				"error",
				`Regeneration failed: ${error instanceof Error ? error.message : String(error)}`,
			);
		} finally {
			isGenerating = false;
		}
	}
	async function setupWatcher() {
		if (!watchBackend || !existsSync(backendPath)) {
			return;
		}

		log("info", "Watching backend files for changes.");

		watcher = await parcel.subscribe(
			backendPath,
			async (err, events) => {
				if (err) {
					log(
						"error",
						`Watcher error: ${err instanceof Error ? err.message : String(err)}`,
					);
					return;
				}

				if (events) {
					if (!events.some((e) => e.path.endsWith(".py"))) {
						return;
					}

					// Debounce rapid updates
					if (debounceTimer) clearTimeout(debounceTimer);
					debounceTimer = setTimeout(async () => {
						await regenerateAndReload();
					}, 300);
				}
			},
			{
				ignore: [
					"**/.git/**",
					"**/dist/**",
					"**/.venv/**",
					"**/__pycache__/**",
				],
			},
		);
	}

	async function cleanupWatcher() {
		if (watcher) {
			await watcher.unsubscribe();
			watcher = null;
		}
	}

	return {
		name: "vite-plugin-openapi-sync",

		async config() {
			//log("info", `Starting Django backend sync plugin...`);
			const schemaGenerated = checkAndGenerateSchema();
			if (!schemaGenerated) {
				throw new Error(
					`Cannot proceed: no schema available and backend not accessible`,
				);
			}

			await generateTypes(schemaGenerated, typesPath);
			log("info", "Generated TypeScript types from django backend");
		},

		configureServer(srv) {
			server = srv;
			cleanupWatcher();

			if (watchBackend && existsSync(backendPath)) {
				setupWatcher();
			}
		},

		closeWatcher() {
			cleanupWatcher();
		},
		closeBundle() {
			cleanupWatcher();
		},
	} as Plugin;
}

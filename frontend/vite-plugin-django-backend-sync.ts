import { execSync } from "node:child_process";
import { existsSync, unwatchFile, watchFile, writeFileSync } from "node:fs";
import { glob } from "node:fs/promises";
import { join, resolve } from "node:path";
import openapiTS, { astToString } from "openapi-typescript";
import type { Plugin, ViteDevServer } from "vite";

interface PluginOptions {
	backendDir?: string;
	schemaOutputPath?: string;
	typeOutputPath?: string;
	watchBackend?: boolean;
}

export default function djangoBackendSync(options: PluginOptions = {}): Plugin {
	const {
		backendDir = "../api",
		schemaOutputPath = "openapi.yml",
		typeOutputPath = "src/api/schema.d.ts",
		watchBackend = true,
	} = options;

	const rootDir = process.cwd();
	const backendPath = resolve(rootDir, backendDir);
	const managePyPath = join(backendPath, "manage.py");
	const schemaPath = resolve(rootDir, schemaOutputPath);
	const typesPath = resolve(rootDir, typeOutputPath);

	let hasRun = false;
	let server: ViteDevServer | undefined;
	let isGenerating = false;
	let watchTimer: NodeJS.Timeout | undefined;
	const watchedFiles: Set<string> = new Set();

	function log(logLevel: "info" | "warn" | "error", message: string) {
		const prefix = `[vite-plugin-django-backend-sync]`;
		const time = new Date().toLocaleTimeString();

		console.log(`${time} ${prefix} ${message}`);
	}

	function generateSchema(): boolean {
		if (!existsSync(managePyPath)) {
			return existsSync(schemaPath);
		}

		try {
			execSync(`uv run manage.py spectacular --file ${schemaPath}`, {
				cwd: backendPath,
				stdio: "pipe",
			});
			return true;
		} catch (error) {
			log(
				"warn",
				`Failed to generate schema (uv/backend issue). Using cached schema.`,
			);
			return existsSync(schemaPath);
		}
	}

	async function generateTypes(): Promise<void> {
		if (!existsSync(schemaPath)) {
			throw new Error(
				`Schema not found at ${schemaPath}. Cannot generate types.`,
			);
		}

		try {
			const output = await openapiTS(
				new URL(`file://${schemaPath}`, import.meta.url),
				{
					exportType: true,
				},
			);
			const outputString = astToString(output);
			writeFileSync(typesPath, outputString);
		} catch (error) {
			throw new Error(
				`Failed to generate types: ${error instanceof Error ? error.message : String(error)}`,
			);
		}
	}

	async function regenerateAndReload() {
		if (isGenerating) return;
		isGenerating = true;

		try {
			const schemaGenerated = generateSchema();
			if (schemaGenerated) {
				await generateTypes();

				if (server) {
					server.ws.send({
						type: "update",
						updates: [
							{
								type: "js-update",
								path: typesPath,
								acceptedPath: typesPath,
								timestamp: Date.now(),
							},
						],
					});
					log("info", `Backend changes detected`);
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

		try {
			const pythonFiles = await glob("**/*.py", {
				cwd: backendPath,
				exclude: ["**/migrations/**", "**/__pycache__/**", "**/.venv/**"],
			});

			log("info", "Watching backend files for changes");

			for await (const file of pythonFiles) {
				const fullPath = join(backendPath, file);

				watchFile(fullPath, { interval: 1000 }, () => {
					if (watchTimer) clearTimeout(watchTimer);
					watchTimer = setTimeout(() => {
						log("info", `Backend file changed: ${file}`);
						regenerateAndReload();
					}, 500);
				});
				watchedFiles.add(fullPath);
			}
		} catch (error) {
			log("warn", `Failed to setup watcher: ${error}`);
		}
	}

	function cleanupWatcher() {
		watchedFiles.forEach((f) => {
			unwatchFile(f);
		});
		watchedFiles.clear();
		if (watchTimer) clearTimeout(watchTimer);
	}

	return {
		name: "vite-plugin-django-backend-sync",

		async config() {
			if (hasRun) return;
			hasRun = true;

			log("info", `Starting Django backend sync plugin...`);
			const schemaGenerated = generateSchema();
			if (!schemaGenerated) {
				throw new Error(
					`Cannot proceed: no schema available and backend not accessible`,
				);
			}

			await generateTypes();
			log("info", "Generated TypeScript types from django backend");
		},

		configureServer(srv) {
			server = srv;

			if (watchBackend && existsSync(backendPath)) {
				setupWatcher();
			}

			return () => {
				cleanupWatcher();
			};
		},
	};
}

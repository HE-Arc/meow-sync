import { exec } from "node:child_process";
import { generateSchema, generateTypes } from "../utils/schema";

async function main() {
	try {
		const schemaContent = generateSchema(
			"../api",
			"uv run manage.py spectacular --format openapi-json",
		);
		await generateTypes(schemaContent, "src/api/schema.d.ts");
	} catch (error) {
		console.error(
			"Error generating TypeScript types:",
			error instanceof Error ? error.message : String(error),
		);
		process.exit(1);
	}

	exec("vue-tsc --build", (error, stdout, stderr) => {
		if (error) {
			console.error(stdout);
			process.exit(1);
		}
		if (stderr) {
			console.error(`Type checking errors:\n${stderr}`);
			process.exit(1);
		}
	});
}

main();

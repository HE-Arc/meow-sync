import { execSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import openapiTS, { astToString } from "openapi-typescript";

export function generateSchema(
	backendPath: string,
	backendCommand: string,
): string {
	try {
		const output = execSync(backendCommand, {
			cwd: backendPath,
			stdio: ["ignore", "pipe", "inherit"],
		});

		return output.toString();
	} catch (error) {
		throw new Error(
			`Failed to generate schema: ${error instanceof Error ? error.message : String(error)}`,
		);
	}
}

export async function generateTypes(
	schemaContent: string,
	typesPath: string,
): Promise<void> {
	try {
		const output = await openapiTS(schemaContent, {
			exportType: true,
		});
		const outputString = astToString(output);
		writeFileSync(typesPath, outputString);
	} catch (error) {
		throw new Error(
			`Failed to generate types: ${error instanceof Error ? error.message : String(error)}`,
		);
	}
}

import createClient from "openapi-fetch";
import type { components, paths } from "./schema.d.ts";

export type Comment = components["schemas"]["Comment"];

export const client = createClient<paths>({
	baseUrl: import.meta.env.VITE_API_URL,
});

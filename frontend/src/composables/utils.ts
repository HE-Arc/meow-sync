type ApiError = {
	code: string;
	detail: string;
	attr: string;
};

export type ApiErrors = ApiError[];
export type BasicApiResponse<T> =
	| {
			data: T;
			error?: never;
	  }
	| {
			data?: never;
			error: {
				errors: ApiErrors;
			};
	  };

export async function handleFetchErrors<T>(
	fetch: () => Promise<BasicApiResponse<T>>,
	toast: ReturnType<typeof useToast>,
): Promise<T | undefined> {
	try {
		const response = await fetch();
		if (response.data) {
			return response.data;
		}
		if (response.error) {
			handleErrors(response.error.errors, toast);
		}
	} catch (error) {
		toast.add({
			title: "Error",
			description: error instanceof Error ? error.message : String(error),
			color: "error",
		});
		console.error("Unhandled error:", error);
	}
}

export function handleErrors(
	errors: { code: string; detail: string; attr: string }[],
	toast: ReturnType<typeof useToast>,
) {
	errors.forEach((err) => {
		toast.add({
			title: "API Error",
			description: err.detail,
			color: "error",
		});
	});
}

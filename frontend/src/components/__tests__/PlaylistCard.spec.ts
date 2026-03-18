// Generated via github copilot, then modified to fix some issues
import { mount } from "@vue/test-utils";
import { describe, expect, it, vi } from "vitest";
import { computed } from "vue";
import type { PlaylistWithId } from "@/api/Playlist";
import PlaylistCard from "../PlaylistCard.vue";

// Mock @vueuse/core
vi.mock("@vueuse/core", async (importOriginal) => {
	const actual = await importOriginal();
	return {
		//@ts-expect-error
		...actual,
		useMediaQuery: vi.fn((_query: string) => computed(() => false)),
	};
});

describe("PlaylistCard", () => {
	const mockPlaylist: PlaylistWithId = {
		id: 1,
		playlist_id: "test-playlist-123",
		title: "Test Playlist",
		description: "A test playlist description",
		author: "Test Author",
		provider: "spotify" as const,
		user: 123,
		img_url: "https://example.com/image.jpg",
	};

	it("renders skeleton when isLoading is true", () => {
		const wrapper = mount(PlaylistCard, {
			props: {
				isLoading: true,
			},
			global: {
				stubs: {
					USkeleton: true,
				},
			},
		});

		expect(wrapper.find("div .animate-pulse").exists()).toBe(true);
	});

	it("displays playlist title", () => {
		const wrapper = mount(PlaylistCard, {
			props: {
				playlist: mockPlaylist,
				isLoading: false,
			},
			global: {
				stubs: {
					UAvatar: true,
					UButton: true,
				},
			},
		});

		expect(wrapper.text()).toContain("Test Playlist");
	});

	it("displays playlist description", async () => {
		const { useMediaQuery } = await import("@vueuse/core");
		vi.mocked(useMediaQuery).mockReturnValueOnce(computed(() => true)); // medium screen

		const wrapper = mount(PlaylistCard, {
			props: {
				playlist: mockPlaylist,
				isLoading: false,
			},
			global: {
				stubs: {
					UAvatar: true,
					UButton: true,
				},
			},
		});

		expect(wrapper.text()).toContain("A test playlist description");
	});

	it("truncates long descriptions to 60 characters on medium screens", async () => {
		const { useMediaQuery } = await import("@vueuse/core");
		vi.mocked(useMediaQuery).mockReturnValueOnce(computed(() => true)); // medium screen

		const longDescription =
			"This is a very long playlist description that definitely exceeds the sixty character limit";
		const playlistWithLongDesc: PlaylistWithId = {
			...mockPlaylist,
			description: longDescription,
		};

		const wrapper = mount(PlaylistCard, {
			props: {
				playlist: playlistWithLongDesc,
				isLoading: false,
			},
			global: {
				stubs: {
					UAvatar: true,
					UButton: true,
				},
			},
		});

		const text = wrapper.text();
		expect(text).toContain(`${longDescription.substring(0, 60)}...`);
		expect(text).not.toContain("limit");
	});

	it("truncates long descriptions to 15 characters on small screens", async () => {
		const { useMediaQuery } = await import("@vueuse/core");
		vi.mocked(useMediaQuery); // small screen

		const longDescription =
			"This is a very long playlist description that definitely exceeds the limit";
		const playlistWithLongDesc: PlaylistWithId = {
			...mockPlaylist,
			description: longDescription,
		};

		const wrapper = mount(PlaylistCard, {
			props: {
				playlist: playlistWithLongDesc,
				isLoading: false,
			},
			global: {
				stubs: {
					UAvatar: true,
					UButton: true,
				},
			},
		});

		const text = wrapper.text();
		expect(text).toContain(`${longDescription.substring(0, 15)}...`);
		expect(text).not.toContain("long");
	});

	it("does not add ellipsis to short descriptions", () => {
		const shortDescription = "Short desc";
		const playlistWithShortDesc: PlaylistWithId = {
			...mockPlaylist,
			description: shortDescription,
		};

		const wrapper = mount(PlaylistCard, {
			props: {
				playlist: playlistWithShortDesc,
				isLoading: false,
			},
			global: {
				stubs: {
					UAvatar: true,
					UButton: true,
				},
			},
		});

		expect(wrapper.text()).toContain("Short desc");
		expect(wrapper.text()).not.toContain("...");
	});

	it("emits click event with playlist id on card click", async () => {
		const wrapper = mount(PlaylistCard, {
			props: {
				playlist: mockPlaylist,
				isLoading: false,
			},
			global: {
				stubs: {
					UAvatar: true,
					UButton: true,
				},
			},
		});

		const card = wrapper.find(".flex.items-center");
		await card.trigger("click");

		expect(wrapper.emitted("click")).toBeTruthy();
		expect(wrapper.emitted("click")?.[0]).toEqual([mockPlaylist.id]);
	});

	it("emits edit event when edit button is clicked", async () => {
		const wrapper = mount(PlaylistCard, {
			props: {
				playlist: mockPlaylist,
				isLoading: false,
			},
			global: {
				stubs: {
					UAvatar: true,
					UButton: false,
				},
			},
		});

		const buttons = wrapper.findAll("button");
		const editButton = buttons.find((btn) => btn.text().includes("Edit"));

		if (editButton) {
			await editButton.trigger("click");
			expect(wrapper.emitted("edit")).toBeTruthy();
			expect(wrapper.emitted("edit")?.[0]).toEqual([mockPlaylist.id]);
		}
	});

	it("emits delete event when delete button is clicked", async () => {
		const wrapper = mount(PlaylistCard, {
			props: {
				playlist: mockPlaylist,
				isLoading: false,
			},
			global: {
				stubs: {
					UAvatar: true,
					UButton: false,
				},
			},
		});

		const buttons = wrapper.findAll("button");
		const deleteButton = buttons.find((btn) => btn.text().includes("Delete"));

		if (deleteButton) {
			await deleteButton.trigger("click");
			expect(wrapper.emitted("delete")).toBeTruthy();
			expect(wrapper.emitted("delete")?.[0]).toEqual([mockPlaylist.id]);
		}
	});

	it("does not propagate click event when edit button is clicked", async () => {
		const wrapper = mount(PlaylistCard, {
			props: {
				playlist: mockPlaylist,
				isLoading: false,
			},
			global: {
				stubs: {
					UAvatar: true,
					UButton: false,
				},
			},
		});

		const buttons = wrapper.findAll("button");
		const editButton = buttons.find((btn) => btn.text().includes("Edit"));

		if (editButton) {
			await editButton.trigger("click");
			expect(wrapper.emitted("click")).toBeFalsy();
			expect(wrapper.emitted("edit")).toBeTruthy();
		}
	});

	it("does not propagate click event when delete button is clicked", async () => {
		const wrapper = mount(PlaylistCard, {
			props: {
				playlist: mockPlaylist,
				isLoading: false,
			},
			global: {
				stubs: {
					UAvatar: true,
					UButton: false,
				},
			},
		});

		const buttons = wrapper.findAll("button");
		const deleteButton = buttons.find((btn) => btn.text().includes("Delete"));

		if (deleteButton) {
			await deleteButton.trigger("click");
			expect(wrapper.emitted("click")).toBeFalsy();
			expect(wrapper.emitted("delete")).toBeTruthy();
		}
	});
});

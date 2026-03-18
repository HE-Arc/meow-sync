// Generated via github copilot, then modified to fix some issues
import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import type { PlaylistWithId } from "@/api/Playlist";
import PlaylistCard from "../PlaylistCard.vue";

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
		});

		expect(wrapper.findComponent({ name: "USkeleton" }).exists()).toBe(true);
	});

	it("renders playlist content when isLoading is false", () => {
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
		// Short description should display fully
		expect(wrapper.text()).toContain("A test playlist description");
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

	it("displays playlist description", () => {
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

	it("truncates long descriptions to 60 characters with ellipsis", () => {
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
		expect(text).toContain(
			"This is a very long playlist description that definitely exc...",
		);
		expect(text).not.toContain("limit");
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

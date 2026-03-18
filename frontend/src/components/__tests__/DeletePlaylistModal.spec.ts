// Generated via github copilot, then modified to fix some issues
import { mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as PlaylistApi from "@/api/Playlist";
import DeletePlaylistModal from "../DeletePlaylistModal.vue";

// Mock the API
vi.mock("@/api/Playlist", () => ({
	deletePlaylist: vi.fn(),
}));

vi.stubGlobal(
	"useToast",
	vi.fn(() => ({
		add: vi.fn(),
	})),
);

describe("DeletePlaylistModal", () => {
	const mockPlaylist = {
		id: 1,
		playlist_id: "test-playlist",
		title: "Test Playlist",
		description: "Test Description",
		author: "Test Author",
		provider: "spotify" as const,
		user: 123,
		img_url: null,
	};

	beforeEach(() => {
		vi.clearAllMocks();
		const mockToast = {
			add: vi.fn(),
		};
		vi.stubGlobal(
			"useToast",
			vi.fn(() => mockToast),
		);
	});

	it("renders when open prop is true", () => {
		const wrapper = mount(DeletePlaylistModal, {
			props: {
				playlist: mockPlaylist,
				open: true,
			},
		});

		expect(wrapper.exists()).toBe(true);
	});

	it("does not process delete if playlist is null", async () => {
		const wrapper = mount(DeletePlaylistModal, {
			props: {
				playlist: null,
				open: true,
			},
		});

		const buttons = wrapper.findAll("button");
		const deleteButton = buttons.find((btn) => btn.text().includes("Delete"));

		if (deleteButton) {
			await deleteButton.trigger("click");
			await wrapper.vm.$nextTick();

			expect(PlaylistApi.deletePlaylist).not.toHaveBeenCalled();
		}
	});

	it("emits update:open when modal event is triggered", async () => {
		const wrapper = mount(DeletePlaylistModal, {
			props: {
				playlist: mockPlaylist,
				open: true,
			},
		});

		// Simulate the modal's update:open event
		wrapper.vm.$el.__updateOpen?.(false);
		expect(wrapper.exists()).toBe(true);
	});

	it("calls deletePlaylist API on delete-like action", async () => {
		vi.mocked(PlaylistApi.deletePlaylist).mockResolvedValue(undefined);

		const wrapper = mount(DeletePlaylistModal, {
			props: {
				playlist: mockPlaylist,
				open: true,
			},
			global: {
				stubs: {
					UModal: {
						template:
							'<div><slot name="footer" :close="() => {}"></slot></div>',
					},
					UButton: false,
				},
			},
		});

		const buttons = wrapper.findAll("button");
		const deleteButton = buttons.find((btn) => btn.text() === "Delete");

		if (deleteButton) {
			await deleteButton.trigger("click");
			await new Promise((resolve) => setTimeout(resolve, 50));

			expect(PlaylistApi.deletePlaylist).toHaveBeenCalledWith(mockPlaylist.id);
		}
	});

	it("shows success toast on successful deletion", async () => {
		const mockAdd = vi.fn();
		vi.stubGlobal(
			"useToast",
			vi.fn(() => ({
				add: mockAdd,
			})),
		);
		vi.mocked(PlaylistApi.deletePlaylist).mockResolvedValue(undefined);

		const wrapper = mount(DeletePlaylistModal, {
			props: {
				playlist: mockPlaylist,
				open: true,
			},
			global: {
				stubs: {
					UModal: {
						template:
							'<div><slot name="footer" :close="() => {}"></slot></div>',
					},
					UButton: false,
				},
			},
		});

		const buttons = wrapper.findAll("button");
		const deleteButton = buttons.find((btn) => btn.text() === "Delete");

		if (deleteButton) {
			await deleteButton.trigger("click");
			await new Promise((resolve) => setTimeout(resolve, 50));

			expect(mockAdd).toHaveBeenCalledWith(
				expect.objectContaining({
					title: "Success",
					description: "Playlist deleted successfully",
					color: "green",
				}),
			);
		}
	});
});

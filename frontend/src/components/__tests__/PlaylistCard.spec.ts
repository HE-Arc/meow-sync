import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import type { PlaylistWithId } from "@/api/Playlist";
import PlaylistCard from "../PlaylistCard.vue";

const samplePlaylist: PlaylistWithId = {
	id: 1,
	first_playlist_id: "spotify123abc",
	first_provider: "spotify",
	second_playlist_id: "youtube456def",
	second_provider: "youtube",
};

const globalStubs = {
	USkeleton: true,
	UIcon: {
		template: '<span :data-icon="name" />',
		props: ["name"],
	},
	UButton: {
		template: "<button @click=\"$emit('click')\"><slot /></button>",
		emits: ["click"],
	},
};

function mountCard(props: { isLoading: boolean; playlist?: PlaylistWithId }) {
	return mount(PlaylistCard, {
		props,
		global: { stubs: globalStubs },
	});
}

describe("PlaylistCard", () => {
	it("does not render card content when isLoading is true", () => {
		const wrapper = mountCard({ isLoading: true });
		expect(wrapper.find(".cursor-pointer").exists()).toBe(false);
	});

	it("renders card content when not loading", () => {
		const wrapper = mountCard({ isLoading: false, playlist: samplePlaylist });
		expect(wrapper.find(".cursor-pointer").exists()).toBe(true);
	});

	it("renders both provider names when not loading", () => {
		const wrapper = mountCard({ isLoading: false, playlist: samplePlaylist });
		expect(wrapper.text()).toContain("Spotify");
		expect(wrapper.text()).toContain("YouTube Music");
	});

	it("emits click with the playlist id when card is clicked", async () => {
		const wrapper = mountCard({ isLoading: false, playlist: samplePlaylist });
		await wrapper.find(".cursor-pointer").trigger("click");
		expect(wrapper.emitted("click")).toBeTruthy();
		expect(wrapper.emitted("click")?.[0]).toEqual([1]);
	});

	it("emits edit with the playlist id when edit button is clicked", async () => {
		const wrapper = mountCard({ isLoading: false, playlist: samplePlaylist });
		const editButton = wrapper
			.findAll("button")
			.find((b) => b.text() === "Edit");
		expect(editButton).toBeTruthy();
		await editButton?.trigger("click");
		expect(wrapper.emitted("edit")).toBeTruthy();
		expect(wrapper.emitted("edit")?.[0]).toEqual([1]);
	});

	it("emits delete with the playlist id when delete button is clicked", async () => {
		const wrapper = mountCard({ isLoading: false, playlist: samplePlaylist });
		const deleteButton = wrapper
			.findAll("button")
			.find((b) => b.text() === "Delete");
		expect(deleteButton).toBeTruthy();
		await deleteButton?.trigger("click");
		expect(wrapper.emitted("delete")).toBeTruthy();
		expect(wrapper.emitted("delete")?.[0]).toEqual([1]);
	});
});

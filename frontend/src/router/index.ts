import { createRouter, createWebHistory } from "vue-router";
import LoginCallback from "@/views/LoginCallback.vue";
import NewPlaylistView from "@/views/playlists/NewPlaylistView.vue";
import PlaylistsView from "@/views/playlists/PlaylistDetailsView.vue";
import PlaylistDetailsView from "@/views/playlists/PlaylistDetailsView.vue";
import HomeView from "../views/HomeView.vue";

function isAuthenticated(): boolean {
	const token = localStorage.getItem("token");
	return !!token;
}

const router = createRouter({
	history: createWebHistory(import.meta.env.BASE_URL),
	routes: [
		{
			path: "/",
			name: "home",
			component: HomeView,
		},
		{
			path: "/login_callback",
			name: "login_callback",
			component: LoginCallback,
		},
		{
			path: "/playlists",
			name: "playlists",
			beforeEnter: (to, from, next) => {
				if (!isAuthenticated()) {
					next({ name: "home" });
				} else {
					next();
				}
			},
			props: true,
			children: [
				{
					path: "view",
					name: "playlists_view",
					component: PlaylistsView,
					alias: "",
				},
				{
					path: "new",
					name: "playlist_new",
					component: NewPlaylistView,
				},
				{
					path: ":id",
					name: "playlist_details",
					component: PlaylistDetailsView,
				},
				{
					path: ":id/edit",
					name: "playlist_edit",
					component: NewPlaylistView,
					props: { isEditMode: true },
				},
			],
		},
		{
			path: "/about",
			name: "about",
			// route level code-splitting
			// this generates a separate chunk (About.[hash].js) for this route
			// which is lazy-loaded when the route is visited.
			component: () => import("../views/AboutView.vue"),
		},
	],
});

export default router;

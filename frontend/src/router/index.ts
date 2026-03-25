import { createRouter, createWebHistory } from "vue-router";
import LoginCallback from "@/views/LoginCallback.vue";
import NewPlaylistView from "@/views/playlists/NewPlaylistView.vue";
import PlaylistDetailsView from "@/views/playlists/PlaylistDetailsView.vue";
import PlaylistsView from "@/views/playlists/PlaylistsView.vue";
import HomeView from "../views/HomeView.vue";

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
			props: true,
			//meta: { requiresAuth: true }, //TODO: Uncomment when authentication is implemented
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
					props: true,
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
		{
			path: "/403",
			name: "forbidden",
			component: () => import("../views/ErrorView.vue"),
			props: { errorCode: 403, errorMessage: "Forbidden" },
		},
		{
			path: "/404",
			name: "not_found",
			component: () => import("../views/ErrorView.vue"),
			props: { errorCode: 404, errorMessage: "Page Not Found" },
		},
		{
			path: "/:catchAll(.*)",
			redirect: "/404",
		},
	],
});

router.beforeEach((to, _from, next) => {
	const requiresAuth = to.matched.some((record) => record.meta.requiresAuth);
	const isAuthenticated = !!localStorage.getItem("access_token");

	if (requiresAuth && !isAuthenticated) {
		next("/403");
	} else {
		next();
	}
});

export default router;

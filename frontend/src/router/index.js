import { createRouter, createWebHistory } from "vue-router"

const routes = [
  { path: "/follow-list", name: "FollowList", component: () => import("../views/FollowList.vue") },
  { path: "/", name: "Home", component: () => import("../views/Home.vue") },
  { path: "/user/:id", name: "UserProfile", component: () => import("../views/UserProfile.vue") },
  { path: "/settings", name: "ProfileSettings", component: () => import("../views/ProfileSettings.vue") },
  { path: "/note/:id", name: "NoteDetail", component: () => import("../views/NoteDetail.vue") },
  { path: "/create", name: "CreateNote", component: () => import("../views/CreateNote.vue") },
  { path: "/edit/:id", name: "EditNote", component: () => import("../views/CreateNote.vue") },
  { path: "/search", name: "Search", component: () => import("../views/Search.vue") },
  { path: "/message", name: "Message", component: () => import("../views/Message.vue") },
  { path: "/chat/:userId", name: "Chat", component: () => import("../views/Chat.vue") },
  { path: "/recycle", name: "RecycleBin", component: () => import("../views/RecycleBin.vue") },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router


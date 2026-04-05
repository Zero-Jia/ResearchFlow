import { createRouter, createWebHistory } from "vue-router";
import Login from "../views/Login.vue";
import Register from "../views/Register.vue";
import ChatPage from "../views/ChatPage.vue";
import { isLoggedIn } from "../utils/auth";

const routes = [
  {
    path: "/",
    redirect: "/chat",
  },
  {
    path: "/login",
    name: "Login",
    component: Login,
  },
  {
    path: "/register",
    name: "Register",
    component: Register,
  },
  {
    path: "/chat",
    name: "ChatPage",
    component: ChatPage,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !isLoggedIn()) {
    next("/login");
    return;
  }

  if ((to.path === "/login" || to.path === "/register") && isLoggedIn()) {
    next("/chat");
    return;
  }

  next();
});

export default router;
import { createRouter, createWebHistory } from "vue-router";
import JobRecommend from "../views/JobRecommend.vue";
import JobResult from "../views/JobResult.vue";

const routes = [
  {
    path: "/",
    redirect: "/job/recommend",
  },
  {
    path: "/job/recommend",
    name: "JobRecommend",
    component: JobRecommend,
  },
  {
    path: "/job/result/:taskId",
    name: "JobResult",
    component: JobResult,
    props: true,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
import { createRouter, createWebHistory } from "vue-router";
import JobRecommend from "../views/JobRecommend.vue";
import JobResult from "../views/JobResult.vue";
import JobHistory from "../views/JobHistory.vue";
import JobDetail from "../views/JobDetail.vue";
import GraphView from "../views/GraphView.vue";

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
  {
    path: "/job/history",
    name: "JobHistory",
    component: JobHistory,
  },
  {
    path: "/job/detail/:taskId",
    name: "JobDetail",
    component: JobDetail,
    props: true,
  },
  {
    path: "/graph/view",
    name: "GraphView",
    component: GraphView,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
<template>
    <div class="page">
      <div class="top-actions">
        <button @click="$router.push('/job/history')">返回历史页</button>
        <button @click="$router.push('/job/recommend')">返回输入页</button>
        <button @click="$router.push('/graph/view')">查看图谱关系</button>
      </div>
  
      <LoadingState v-if="loading" text="正在加载任务详情..." />
      <ErrorState v-else-if="error" :text="error" />
      <div v-else-if="!result" class="content">
        <EmptyState text="暂无任务详情" />
      </div>
      <div v-else class="content">
        <div class="card">
          <h2>任务详情</h2>
          <p><strong>任务 ID：</strong>{{ result.task_id }}</p>
          <p><strong>问题：</strong>{{ result.question }}</p>
          <p><strong>任务类型：</strong>{{ result.task_type }}</p>
          <p>
            <strong>标准化技能：</strong>
            <span
              v-for="skill in result.normalized_skills"
              :key="skill"
              class="tag"
            >
              {{ skill }}
            </span>
          </p>
        </div>
  
        <div v-if="isRecommendTask" class="card">
          <h2>推荐岗位详情</h2>
          <JobCard
            v-for="job in result.job_cards"
            :key="job.job_name"
            :job="job"
          />
        </div>
  
        <ComparisonPanel
          v-if="isCompareTask && result.comparison"
          :comparison="result.comparison"
        />
  
        <div
          class="card"
          v-if="result.suggestions && result.suggestions.length > 0"
        >
          <h2>建议</h2>
          <ul>
            <li v-for="(item, index) in result.suggestions" :key="index">
              {{ item }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { getJobTaskView } from "../api/job";
  import LoadingState from "../components/LoadingState.vue";
  import ErrorState from "../components/ErrorState.vue";
  import EmptyState from "../components/EmptyState.vue";
  import JobCard from "../components/JobCard.vue";
  import ComparisonPanel from "../components/ComparisonPanel.vue";
  
  export default {
    name: "JobDetail",
    components: {
      LoadingState,
      ErrorState,
      EmptyState,
      JobCard,
      ComparisonPanel,
    },
    props: {
      taskId: {
        type: String,
        required: true,
      },
    },
    data() {
      return {
        loading: true,
        error: "",
        result: null,
      };
    },
    computed: {
      isCompareTask() {
        return this.result?.task_type === "compare_job";
      },
      isRecommendTask() {
        return this.result?.task_type !== "compare_job";
      },
    },
    async mounted() {
      await this.fetchDetail();
    },
    methods: {
      async fetchDetail() {
        this.loading = true;
        this.error = "";
  
        try {
          const res = await getJobTaskView(this.taskId);
          this.result = res.data;
        } catch (err) {
          this.error =
            err?.response?.data?.detail || "加载任务详情失败，请检查后端服务。";
        } finally {
          this.loading = false;
        }
      },
    },
  };
  </script>
  
  <style scoped>
  .page {
    max-width: 1000px;
    margin: 0 auto;
  }
  
  .top-actions {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
  }
  
  button {
    background: #1f4e79;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    cursor: pointer;
  }
  
  .content {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  
  .card {
    background: white;
    border-radius: 12px;
    padding: 22px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  }
  
  .tag {
    display: inline-block;
    margin-right: 8px;
    margin-top: 6px;
    padding: 4px 10px;
    border-radius: 999px;
    background: #e5e7eb;
    font-size: 13px;
  }
  </style>
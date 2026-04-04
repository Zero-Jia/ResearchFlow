<template>
    <div class="page">
      <div class="top-actions">
        <button @click="$router.push('/job/recommend')">返回输入页</button>
        <button @click="$router.push('/job/history')">查看历史记录</button>
      </div>
  
      <div class="card search-card">
        <h2>知识图谱关系展示</h2>
  
        <div class="form-row">
          <label>岗位名称</label>
          <input
            v-model="jobName"
            type="text"
            placeholder="例如：数据分析师"
          />
          <button @click="fetchGraph" :disabled="loading">
            {{ loading ? "加载中..." : "查看图谱关系" }}
          </button>
        </div>
      </div>
  
      <LoadingState v-if="loading" text="正在加载图谱关系..." />
      <ErrorState v-else-if="error" :text="error" />
      <EmptyState
        v-else-if="hasSearched && !graphData"
        text="未找到该岗位的图谱关系"
      />
  
      <div v-else-if="graphData" class="card">
        <GraphRelationCard :data="graphData" />
      </div>
    </div>
  </template>
  
  <script>
  import { getJobGraphView } from "../api/graph";
  import LoadingState from "../components/LoadingState.vue";
  import ErrorState from "../components/ErrorState.vue";
  import EmptyState from "../components/EmptyState.vue";
  import GraphRelationCard from "../components/GraphRelationCard.vue";
  
  export default {
    name: "GraphView",
    components: {
      LoadingState,
      ErrorState,
      EmptyState,
      GraphRelationCard,
    },
    data() {
      return {
        jobName: "数据分析师",
        loading: false,
        error: "",
        hasSearched: false,
        graphData: null,
      };
    },
    methods: {
      async fetchGraph() {
        this.loading = true;
        this.error = "";
        this.hasSearched = true;
        this.graphData = null;

        try {
          const cleanJobName = this.jobName.trim();
          if (!cleanJobName) {
            this.error = "岗位名称不能为空";
            return;
          }

          const res = await getJobGraphView(cleanJobName);
          this.graphData = res.data;
        } catch (err) {
          this.error =
            err?.response?.data?.detail || "加载图谱关系失败，请检查后端服务。";
        } finally {
          this.loading = false;
        }
      }
    },
  };
  </script>
  
  <style scoped>
  .page {
    max-width: 1100px;
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
  
  .card {
    background: white;
    border-radius: 12px;
    padding: 22px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    margin-bottom: 16px;
  }
  
  .form-row {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  
  label {
    font-weight: 600;
  }
  
  input {
    border: 1px solid #d0d7de;
    border-radius: 8px;
    padding: 10px 12px;
    flex: 1;
  }
  </style>
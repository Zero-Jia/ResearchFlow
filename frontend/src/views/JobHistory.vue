<template>
    <div class="page">
      <div class="top-actions">
        <button @click="$router.push('/job/recommend')">返回输入页</button>
      </div>
  
      <div class="card search-card">
        <h2>历史推荐任务</h2>
  
        <div class="form-row">
          <label>用户 ID</label>
          <input v-model.number="userId" type="number" />
          <button @click="fetchHistory" :disabled="loading">
            {{ loading ? "加载中..." : "查询历史" }}
          </button>
        </div>
      </div>
  
      <LoadingState v-if="loading" text="正在加载历史记录..." />
      <ErrorState v-else-if="error" :text="error" />
      <div v-else-if="historyItems.length === 0 && hasSearched">
        <EmptyState text="当前用户暂无历史记录" />
      </div>
      <div v-else-if="historyItems.length > 0" class="card">
        <h2>历史记录列表</h2>
  
        <table class="history-table">
          <thead>
            <tr>
              <th>任务 ID</th>
              <th>任务类型</th>
              <th>主题</th>
              <th>状态</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in historyItems" :key="item.task_id">
              <td>{{ item.task_id }}</td>
              <td>{{ item.task_type }}</td>
              <td>{{ item.topic }}</td>
              <td>{{ item.status }}</td>
              <td>{{ item.created_at }}</td>
              <td>
                <button class="small-btn" @click="goToDetail(item.task_id)">
                  查看详情
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </template>
  
  <script>
  import { getJobTaskHistory } from "../api/job";
  import LoadingState from "../components/LoadingState.vue";
  import ErrorState from "../components/ErrorState.vue";
  import EmptyState from "../components/EmptyState.vue";
  
  export default {
    name: "JobHistory",
    components: {
      LoadingState,
      ErrorState,
      EmptyState,
    },
    data() {
      return {
        userId: 1,
        loading: false,
        error: "",
        hasSearched: false,
        historyItems: [],
      };
    },
    methods: {
      async fetchHistory() {
        this.loading = true;
        this.error = "";
        this.hasSearched = true;
  
        try {
          const res = await getJobTaskHistory(this.userId);
          this.historyItems = res.data.items || [];
        } catch (err) {
          this.error =
            err?.response?.data?.detail || "加载历史记录失败，请检查后端服务。";
          this.historyItems = [];
        } finally {
          this.loading = false;
        }
      },
      goToDetail(taskId) {
        this.$router.push(`/job/detail/${taskId}`);
      },
    },
  };
  </script>
  
  <style scoped>
  .page {
    max-width: 1100px;
    margin: 0 auto;
  }
  
  .top-actions {
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
  
  .small-btn {
    padding: 6px 12px;
    font-size: 13px;
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
    width: 120px;
  }
  
  .history-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 12px;
  }
  
  .history-table th,
  .history-table td {
    border-bottom: 1px solid #e5e7eb;
    text-align: left;
    padding: 12px 10px;
  }
  
  .history-table th {
    background: #f8fafc;
  }
  </style>
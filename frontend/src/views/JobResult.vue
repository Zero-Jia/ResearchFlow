<template>
  <div class="page">
    <div class="top-actions">
      <button @click="$router.push('/job/recommend')">返回输入页</button>
      <button @click="$router.push('/job/history')">查看历史记录</button>
    </div>

    <div v-if="loading" class="card">加载中...</div>
    <div v-else-if="error" class="card error">{{ error }}</div>

    <div v-else class="content">
      <div class="card">
        <h2>职位推荐结果</h2>
        <p><strong>任务 ID：</strong>{{ result.task_id }}</p>
        <p><strong>问题：</strong>{{ result.question }}</p>
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
        <p><strong>任务类型：</strong>{{ result.task_type }}</p>
      </div>

      <div class="card" v-if="result.job_cards && result.job_cards.length > 0">
        <h2>推荐岗位</h2>

        <div
          v-for="job in result.job_cards"
          :key="job.job_name"
          class="job-card"
        >
          <h3>{{ job.job_name }}</h3>
          <p><strong>匹配分数：</strong>{{ job.score }}</p>

          <div class="section">
            <strong>已匹配技能：</strong>
            <span
              v-for="skill in job.matched_skills"
              :key="skill"
              class="tag success"
            >
              {{ skill }}
            </span>
          </div>

          <div class="section">
            <strong>缺失技能：</strong>
            <span
              v-for="skill in job.missing_skills"
              :key="skill"
              class="tag warning"
            >
              {{ skill }}
            </span>
          </div>

          <div class="section">
            <strong>推荐课程：</strong>
            <span
              v-for="course in job.recommended_courses"
              :key="course"
              class="tag info"
            >
              {{ course }}
            </span>
          </div>
        </div>
      </div>

      <div class="card" v-if="result.comparison">
        <h2>岗位对比</h2>
        <p class="multiline">{{ result.comparison }}</p>
      </div>

      <div
        class="card"
        v-if="result.suggestions && result.suggestions.length > 0"
      >
        <h2>总体建议</h2>
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

export default {
  name: "JobResult",
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
  async mounted() {
    await this.fetchResult();
  },
  methods: {
    async fetchResult() {
      this.loading = true;
      this.error = "";

      try {
        const res = await getJobTaskView(this.taskId);
        this.result = res.data;
      } catch (err) {
        this.error =
          err?.response?.data?.detail || "加载结果失败，请检查后端服务。";
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
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
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

.error {
  color: #c0392b;
}

.job-card {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 16px;
  margin-top: 16px;
}

.job-card h3 {
  margin-top: 0;
}

.section {
  margin-top: 12px;
  line-height: 2;
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

.success {
  background: #d1fae5;
}

.warning {
  background: #fef3c7;
}

.info {
  background: #dbeafe;
}

.multiline {
  white-space: pre-wrap;
}
</style>
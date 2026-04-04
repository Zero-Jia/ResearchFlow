<template>
  <div class="page">
    <div class="card">
      <div class="top-actions">
        <button @click="$router.push('/job/history')">查看历史记录</button>
        <button @click="$router.push('/graph/view')">查看图谱关系</button>
      </div>

      <h2>职位推荐输入</h2>

      <div class="form-item">
        <label>用户 ID</label>
        <input v-model.number="form.user_id" type="number" />
      </div>

      <div class="form-item">
        <label>会话 ID</label>
        <input v-model.number="form.session_id" type="number" />
      </div>

      <div class="form-item">
        <label>技能列表（用中文逗号或英文逗号分隔）</label>
        <input
          v-model="skillsInput"
          type="text"
          placeholder="例如：Python, SQL, Pandas"
        />
      </div>

      <div class="form-item">
        <label>问题描述</label>
        <textarea
          v-model="form.question"
          rows="4"
          placeholder="例如：我会 Python、SQL、Pandas，适合什么岗位？"
        ></textarea>
      </div>

      <div class="actions">
        <button @click="handleSubmit" :disabled="loading">
          {{ loading ? "提交中..." : "开始推荐" }}
        </button>
      </div>

      <p v-if="error" class="error">{{ error }}</p>
    </div>
  </div>
</template>

<script>
import { createJobTask } from "../api/job";

export default {
  name: "JobRecommend",
  data() {
    return {
      loading: false,
      error: "",
      skillsInput: "Python, SQL, Pandas",
      form: {
        user_id: 1,
        session_id: 1,
        question: "我会 Python、SQL、Pandas，适合什么岗位？",
      },
    };
  },
  methods: {
    parseSkills() {
      return this.skillsInput
        .split(/[,，]/)
        .map((item) => item.trim())
        .filter((item) => item.length > 0);
    },
    async handleSubmit() {
      this.loading = true;
      this.error = "";

      try {
        const payload = {
          user_id: this.form.user_id,
          session_id: this.form.session_id,
          question: this.form.question,
          skills: this.parseSkills(),
        };

        const res = await createJobTask(payload);
        const taskId = res.data.task_id;

        this.$router.push(`/job/result/${taskId}`);
      } catch (err) {
        this.error =
          err?.response?.data?.detail || "提交失败，请检查后端服务是否正常。";
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
.page {
  max-width: 900px;
  margin: 0 auto;
}

.card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.top-actions {
  margin-bottom: 16px;
}

h2 {
  margin-top: 0;
  margin-bottom: 20px;
}

.form-item {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
}

label {
  margin-bottom: 8px;
  font-weight: 600;
}

input,
textarea {
  border: 1px solid #d0d7de;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 14px;
}

textarea {
  resize: vertical;
}

.actions {
  margin-top: 20px;
}

button {
  background: #1f4e79;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 18px;
  cursor: pointer;
  font-size: 14px;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.error {
  color: #c0392b;
  margin-top: 16px;
}
</style>
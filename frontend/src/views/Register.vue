<template>
    <div class="auth-page">
      <div class="auth-card">
        <h2>注册 JobKG-Agent</h2>
  
        <div class="form-item">
          <label>用户名</label>
          <input v-model="form.username" type="text" />
        </div>
  
        <div class="form-item">
          <label>邮箱</label>
          <input v-model="form.email" type="email" />
        </div>
  
        <div class="form-item">
          <label>密码</label>
          <input v-model="form.password" type="password" />
        </div>
  
        <button @click="handleRegister" :disabled="loading">
          {{ loading ? "注册中..." : "注册" }}
        </button>
  
        <p v-if="error" class="error">{{ error }}</p>
  
        <p class="tip">
          已有账号？
          <span class="link" @click="$router.push('/login')">去登录</span>
        </p>
      </div>
    </div>
  </template>
  
  <script>
  import { register } from "../api/auth";
  import { saveAuth } from "../utils/auth";
  
  export default {
    name: "Register",
    data() {
      return {
        loading: false,
        error: "",
        form: {
          username: "",
          email: "",
          password: "",
        },
      };
    },
    methods: {
      async handleRegister() {
        this.loading = true;
        this.error = "";
  
        try {
          const res = await register(this.form);
          saveAuth(res.data);
          this.$router.push("/chat");
        } catch (err) {
          this.error = err?.response?.data?.detail || "注册失败";
        } finally {
          this.loading = false;
        }
      },
    },
  };
  </script>
  
  <style scoped>
  .auth-page {
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    background: #f5f7fb;
  }
  .auth-card {
    width: 420px;
    background: white;
    border-radius: 12px;
    padding: 28px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
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
  input {
    border: 1px solid #d0d7de;
    border-radius: 8px;
    padding: 10px 12px;
  }
  button {
    width: 100%;
    background: #1f4e79;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 16px;
    cursor: pointer;
  }
  button:disabled {
    background: #94a3b8;
    cursor: not-allowed;
  }
  .error {
    color: #c0392b;
    margin-top: 14px;
  }
  .tip {
    margin-top: 16px;
    text-align: center;
  }
  .link {
    color: #1f4e79;
    cursor: pointer;
  }
  </style>
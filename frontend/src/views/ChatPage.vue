<template>
  <div class="chat-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2>会话</h2>
        <button @click="handleCreateSession">+ 新建</button>
      </div>

      <div class="session-list">
        <div
          v-for="item in sessions"
          :key="item.id"
          class="session-item"
          :class="{ active: currentSession && currentSession.id === item.id }"
          @click="selectSession(item)"
        >
          <div class="session-title">{{ item.title }}</div>
          <div class="session-time">{{ formatTime(item.updated_at) }}</div>
        </div>
      </div>
    </aside>

    <main class="chat-main">
      <div class="chat-topbar">
        <div class="topbar-left">
          <h2>{{ currentSession ? currentSession.title : "请选择或新建会话" }}</h2>
          <p class="welcome-text" v-if="currentUser">
            当前用户：{{ currentUser.username }}
          </p>
        </div>
        <button class="logout-btn" @click="logout">退出登录</button>
      </div>

      <div class="messages-container" ref="messageContainer">
        <div v-if="loadingMessages" class="state-text">加载消息中...</div>
        <div v-else-if="!currentSession" class="state-text">
          请先在左侧新建或选择一个会话
        </div>
        <template v-else>
          <div
            v-for="msg in messages"
            :key="msg.id"
            class="message-row"
            :class="msg.role === 'user' ? 'user-row' : 'assistant-row'"
          >
            <div
              class="message-bubble"
              :class="msg.role === 'user' ? 'user-bubble' : 'assistant-bubble'"
            >
              <div class="message-role">
                {{ msg.role === "user" ? "你" : "助手" }}
              </div>
              <pre>{{ msg.content }}</pre>
            </div>
          </div>
        </template>
      </div>

      <div class="input-area">
        <textarea
          v-model="inputText"
          placeholder="输入你的问题，例如：我会 Python、SQL、Pandas，适合什么岗位？"
          rows="3"
          @keydown.enter.exact.prevent="handleSend"
        />
        <div class="input-actions">
          <button @click="handleSend" :disabled="sending || !currentSession">
            {{ sending ? "发送中..." : "发送" }}
          </button>
        </div>
        <p v-if="error" class="error">{{ error }}</p>
      </div>
    </main>
  </div>
</template>

<script>
import { clearAuth, getUser } from "../utils/auth";
import {
  listSessions,
  createSession,
  listMessages,
  streamMessage,
} from "../api/chat";

export default {
  name: "ChatPage",
  data() {
    return {
      sessions: [],
      currentSession: null,
      messages: [],
      inputText: "",
      loadingSessions: false,
      loadingMessages: false,
      sending: false,
      error: "",
      currentUser: getUser(),
    };
  },

  async mounted() {
    await this.fetchSessions();
  },

  methods: {
    async fetchSessions() {
      this.loadingSessions = true;
      this.error = "";

      try {
        const res = await listSessions();
        this.sessions = res.data.items || [];

        if (this.sessions.length > 0) {
          await this.selectSession(this.sessions[0]);
        }
      } catch (err) {
        this.error = err?.response?.data?.detail || "加载会话失败";
      } finally {
        this.loadingSessions = false;
      }
    },

    async handleCreateSession() {
      this.error = "";

      const inputTitle = prompt("请输入会话名称：", "新会话");
      if (inputTitle === null) return;

      const title = inputTitle.trim() || "新会话";

      try {
        const res = await createSession({ title });
        const session = res.data;

        this.sessions.unshift(session);
        await this.selectSession(session);
      } catch (err) {
        this.error = err?.response?.data?.detail || "创建会话失败";
      }
    },

    async selectSession(session) {
      this.currentSession = session;
      this.loadingMessages = true;
      this.error = "";

      try {
        const res = await listMessages(session.id);
        this.messages = res.data.messages || [];
        this.$nextTick(() => this.scrollToBottom());
      } catch (err) {
        this.error = err?.response?.data?.detail || "加载消息失败";
      } finally {
        this.loadingMessages = false;
      }
    },

    async handleSend() {
      const text = this.inputText.trim();
      if (!text || !this.currentSession) return;

      this.sending = true;
      this.error = "";

      const userLocalId = `user-${Date.now()}`;
      const assistantLocalId = `assistant-${Date.now()}`;

      // 1. 先把用户消息显示到页面上
      this.messages.push({
        id: userLocalId,
        role: "user",
        content: text,
        created_at: new Date().toISOString(),
      });

      // 2. 再创建一个空的 assistant 气泡
      const assistantMessage = {
        id: assistantLocalId,
        role: "assistant",
        content: "",
        created_at: new Date().toISOString(),
      };
      this.messages.push(assistantMessage);

      this.inputText = "";
      this.$nextTick(() => this.scrollToBottom());

      try {
        const response = await streamMessage(this.currentSession.id, {
          question: text,
          skills: [],
        });

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          assistantMessage.content += chunk;

          // 强制触发视图更新
          this.messages = [...this.messages];
          this.$nextTick(() => this.scrollToBottom());
        }

        // 如果当前标题还是默认标题，就用首条问题更新标题
        if (this.currentSession.title === "新会话") {
          const newTitle = text.slice(0, 20);
          this.currentSession.title = newTitle;

          const idx = this.sessions.findIndex(
            (s) => s.id === this.currentSession.id
          );
          if (idx >= 0) {
            this.sessions[idx].title = newTitle;
          }
        }
      } catch (err) {
        assistantMessage.content = err.message || "发送失败";
        this.messages = [...this.messages];
        this.error = err.message || "发送失败";
      } finally {
        this.sending = false;
      }
    },

    scrollToBottom() {
      const el = this.$refs.messageContainer;
      if (el) {
        el.scrollTop = el.scrollHeight;
      }
    },

    formatTime(value) {
      if (!value) return "";
      return value.replace("T", " ").slice(0, 19);
    },

    logout() {
      clearAuth();
      this.$router.push("/login");
    },
  },
};
</script>

<style scoped>
.chat-layout {
  height: 100vh;
  display: flex;
  background: #f5f7fb;
}

.sidebar {
  width: 300px;
  border-right: 1px solid #e5e7eb;
  background: #ffffff;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header button {
  background: #1f4e79;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  cursor: pointer;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.session-item {
  padding: 12px;
  border-radius: 10px;
  cursor: pointer;
  margin-bottom: 10px;
  background: #f8fafc;
  transition: all 0.2s;
}

.session-item:hover {
  background: #eef4fb;
}

.session-item.active {
  background: #dbeafe;
}

.session-title {
  font-weight: 600;
  margin-bottom: 6px;
}

.session-time {
  font-size: 12px;
  color: #666;
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-topbar {
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  background: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.topbar-left h2 {
  margin: 0;
}

.welcome-text {
  margin-top: 6px;
  font-size: 13px;
  color: #666;
}

.logout-btn {
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 12px;
  cursor: pointer;
}

.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.message-row {
  display: flex;
  margin-bottom: 16px;
}

.user-row {
  justify-content: flex-end;
}

.assistant-row {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 72%;
  padding: 14px 16px;
  border-radius: 14px;
}

.user-bubble {
  background: #1f4e79;
  color: white;
}

.assistant-bubble {
  background: white;
  border: 1px solid #e5e7eb;
}

.message-role {
  font-size: 12px;
  margin-bottom: 8px;
  opacity: 0.8;
}

.message-bubble pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: inherit;
  line-height: 1.7;
}

.input-area {
  border-top: 1px solid #e5e7eb;
  background: white;
  padding: 16px 20px;
}

textarea {
  width: 100%;
  resize: none;
  border: 1px solid #d0d7de;
  border-radius: 10px;
  padding: 12px;
  font-size: 14px;
  box-sizing: border-box;
}

.input-actions {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
}

.input-actions button {
  background: #1f4e79;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 16px;
  cursor: pointer;
}

.input-actions button:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.state-text {
  color: #666;
}

.error {
  color: #c0392b;
  margin-top: 10px;
}
</style>
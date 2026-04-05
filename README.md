# JobKG-Agent

基于 **知识图谱（Neo4j） + LangChain v1 Agent** 的智能职业推荐系统
支持 **多会话聊天 + 流式输出（类 ChatGPT）+ 用户系统**

---

## 🚀 1. 项目简介

JobKG-Agent 是一个面向计算机及人工智能专业学生的 **AI 职业助手系统**。

系统结合：

* 知识图谱（Neo4j）
* LangChain Agent + LangGraph
* 多轮对话系统
* 流式输出（Streaming）

实现从“输入技能 → 职业推荐 → 能力提升路径”的完整闭环。

用户登录后可进入类似 **ChatGPT 的聊天界面**，在不同会话中进行职业咨询与规划。

---

## ✨ 2. 核心功能

### 🤖 AI 职业推荐能力

* 职位推荐（基于技能匹配）
* 技能差距分析（Skill Gap Analysis）
* 学习路径规划（课程推荐）
* 岗位对比（Job Comparison）
* 结构化结果输出（JSON）

---

### 💬 多会话聊天系统（类 ChatGPT）

* 多 Session 管理
* 聊天记录持久化（MySQL）
* 会话标题自动生成 / 自定义命名
* 上下文记忆（基于 LangGraph Checkpointer）

---

### ⚡ 流式输出（Streaming）

* 基于 LangChain Agent 实现 **Token 级流式输出**
* FastAPI `StreamingResponse` 实现后端流式返回
* 前端基于 `ReadableStream` 实时渲染
* 显著提升用户交互体验（降低感知延迟）

---

### 👤 用户系统

* 用户注册 / 登录（JWT）
* 接口鉴权（Bearer Token）
* 会话与用户隔离

---

## 🧠 3. 系统架构

```text
用户输入
   ↓
前端 Chat UI（Vue3）
   ↓
FastAPI 后端
   ↓
LangChain Agent
   ↓
工具调用（Neo4j / Service）
   ↓
知识图谱查询
   ↓
生成结果（流式返回）
```

---

## 🛠️ 4. 技术栈

### 后端

* FastAPI（Web 框架）
* SQLAlchemy（ORM）
* MySQL（数据存储）
* Neo4j（知识图谱）
* LangChain v1（Agent 框架）
* LangGraph（状态管理 / Memory）

---

### 前端

* Vue3（Composition API）
* Vite
* Axios
* Fetch + ReadableStream（流式处理）

---

## ⚙️ 5. 核心设计

### 1️⃣ Agent 架构拆分

* `job_memory_agent`：结构化任务（推荐 / 分析）
* `job_streaming_agent`：聊天流式输出

👉 两者共享：

* LangGraph Checkpointer（实现会话级记忆）

---

### 2️⃣ 流式输出实现

后端：

```python
StreamingResponse(generator())
```

Agent：

```python
agent.stream(..., stream_mode="messages")
```

前端：

```javascript
response.body.getReader()
```

---

### 3️⃣ 会话记忆机制

* 基于 `thread_id = session_id`
* 自动复用上下文技能信息
* 支持多轮对话推理

---

## ▶️ 6. 启动方式

### 后端

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

---

### 前端

```bash
cd frontend
npm install
npm run dev
```

---

## 📸 7. 功能展示（可自行补截图）

* 聊天界面（类 ChatGPT）
* 职位推荐结果
* 技能差距分析
* 流式输出效果

---

## 🌟 8. 项目亮点（面试重点）

* ✅ 实现类 ChatGPT 的多会话聊天系统
* ✅ 基于 LangChain Agent 的工具调用决策能力
* ✅ 知识图谱 + Agent 融合（非简单问答）
* ✅ Token 级流式输出（Streaming）
* ✅ 会话级上下文记忆（LangGraph）
* ✅ 前后端完整工程化实现

---

## 🔮 9. 后续优化方向

* 长期记忆（向量数据库 / 用户画像）
* RAG 检索增强
* Agent 推理过程可视化（工具调用过程流）
* Markdown 渲染（代码块 / 高亮）
* 会话管理增强（删除 / 重命名）

---

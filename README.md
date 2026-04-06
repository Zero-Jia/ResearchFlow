# JobKG-Agent

基于 **知识图谱（Neo4j） + LangChain v1 + LangGraph** 的智能职业推荐系统
支持 **多会话聊天 + 推理过程可视化 + 流式输出（类 ChatGPT）+ 短期记忆**

---

## 🚀 1. 项目简介

JobKG-Agent 是一个面向计算机及人工智能专业学生的 **AI 职业助手系统**。

系统融合：

* 知识图谱（Neo4j）
* LangChain Agent + LangGraph（多步推理）
* 多轮对话系统
* 流式输出（Streaming）
* 会话级短期记忆（Session Memory）

实现从：

```text
用户输入 → 技能解析 → 职业推荐 → 能力提升路径 → 个性化建议
```

的完整智能决策闭环。

用户登录后可进入类似 **ChatGPT 的聊天界面**，在不同会话中进行职业咨询与规划。

---

## ✨ 2. 核心功能

### 🤖 AI 职业推荐能力

* 职位推荐（基于技能匹配）
* 技能差距分析（Skill Gap Analysis）
* 学习路径规划（课程推荐）
* 岗位对比（Job Comparison）
* 综合建议生成（LLM + 结构化数据融合）

---

### 🧠 Agent 多步推理（LangGraph）

系统基于 LangGraph 构建 **可控多步推理流程**：

```text
prepare_context → planner → tool调用 → summarize
```

支持：

* 自动任务拆解（Planner）
* 多工具调用（Neo4j / Service）
* 动态路径选择（条件分支）
* 可解释推理过程

---

### 🔀 多分支智能决策

Agent 不再局限于固定流程，而是支持：

* `recommend`：岗位推荐
* `gap`：技能差距分析
* `course`：课程推荐
* `compare`：岗位对比
* `memory_update`：技能纠正 / 更新
* `fallback_llm`：开放式问题（非结构化）

👉 避免“所有问题都强行推荐岗位”的问题

---

### 💬 多会话聊天系统（类 ChatGPT）

* 多 Session 管理
* 聊天记录持久化（MySQL）
* 会话标题自动生成
* 用户隔离（JWT）
* 支持连续追问（Follow-up）

---

### 🧠 短期记忆机制（Session Memory）

系统支持会话级记忆：

* 自动读取历史消息（MySQL）
* 从上一轮结果恢复技能（report_json）
* 支持技能纠正（如：我不会 SQL）

示例：

```text
我会 Python、SQL、Pandas
→ 记录技能

我不会 SQL
→ 更新为 Python、Pandas
```

---

### ⚡ 推理过程流式输出（Reasoning Streaming）

后端基于：

```python
LangGraph.stream(stream_mode="updates")
```

实现：

* 每个节点实时输出（planner / recommend / summarize）
* 推理过程可视化
* 类 ChatGPT “思考过程展示”

---

### ⚡ Token 流式输出（基础）

* FastAPI `StreamingResponse`
* 前端 `ReadableStream`
* 降低响应延迟，提升交互体验

---

## 🧠 3. 系统架构

```text
用户输入
   ↓
Vue3 Chat UI
   ↓
FastAPI 后端
   ↓
LangGraph Agent
   ↓
Planner（任务拆解）
   ↓
工具调用（Neo4j / Service）
   ↓
知识图谱查询
   ↓
LLM 总结生成
   ↓
流式返回（推理 + 结果）
```

---

## 🛠️ 4. 技术栈

### 后端

* FastAPI（Web 框架）
* SQLAlchemy（ORM）
* MySQL（聊天数据存储）
* Neo4j（知识图谱）
* LangChain v1（Agent 框架）
* LangGraph（多步推理 + 状态管理）

---

### 前端

* Vue3（Composition API）
* Vite
* Axios
* Fetch + ReadableStream（流式渲染）

---

## ⚙️ 5. 核心设计

### 1️⃣ Agent 架构升级（重点）

原本：

```text
固定工具调用
```

升级为：

```text
LangGraph + Planner + 多分支决策
```

实现：

* 可解释推理
* 灵活任务分配
* 非结构化问题处理能力

---

### 2️⃣ 推理过程可视化

后端输出：

```json
{"type":"reasoning","step":"planner","text":"..."}
{"type":"final","text":"..."}
```

前端实时渲染：

```text
[prepare_context]
[planner]
[recommend]
[course]
[summarize]
```

---

### 3️⃣ 短期记忆实现（关键）

```text
session_id → 查询 ChatMessage
          → 读取 report_json
          → 恢复 input_skills
          → 合并当前输入（支持否定）
```

👉 解决：

* 技能丢失问题
* 多轮对话不连贯问题

---

### 4️⃣ 技能纠正机制（亮点）

支持：

* “我不会 SQL”
* “去掉 Python”
* “我说错了”

实现：

```python
merge_skills_with_correction(...)
```

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

## 📸 7. 功能展示（建议补图）

* Chat 页面（类 ChatGPT）
* 推理过程流式输出
* 职位推荐结果
* 技能差距分析

---

## 🌟 8. 项目亮点（面试重点）

* ✅ LangGraph 多步推理 Agent（不是简单调用 LLM）
* ✅ Agent 推理过程可视化（reasoning streaming）
* ✅ 知识图谱 + Agent 深度融合
* ✅ 支持技能纠正的短期记忆系统
* ✅ 多分支任务决策（非死板流程）
* ✅ 前后端完整工程化实现
* ✅ 类 ChatGPT 交互体验（流式输出）

---

## 🔮 9. 后续优化方向

* 长期记忆（用户技能画像）
* 向量数据库 + RAG 检索增强
* Token 级流式输出（逐字生成）
* Markdown 渲染（代码高亮）
* 会话管理（删除 / 重命名）
* Agent 调用链可视化（LangSmith）

---

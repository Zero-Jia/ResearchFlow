# JobKG-Agent

基于 **知识图谱（Neo4j） + LangChain v1 + LangGraph** 的智能职业推荐系统  
支持 **多会话聊天 + 推理过程可视化 + 流式输出 + LLM短期记忆**

---

## 🚀 项目简介

JobKG-Agent 是一个面向计算机及人工智能专业学生的 **AI 职业助手系统**。

系统融合：

- 知识图谱（Neo4j）
- LangGraph 多步推理 Agent
- LLM 语义理解
- 多轮对话系统
- 会话级短期记忆

实现完整流程：

用户输入 → 技能理解 → 职业推荐 → 能力提升路径 → 个性化建议

---

## ✨ 核心功能

### 🤖 职业推荐能力

- 职位推荐（基于技能匹配）
- 技能差距分析
- 学习路径规划
- 岗位对比
- 综合建议生成（LLM + 图谱）

---

### 🧠 LLM技能记忆系统（重点）

系统引入 **基于 LLM 的技能记忆更新机制**：

#### 功能：

- 自动识别技能（我会 Python）
- 技能补充（我还会 FastAPI）
- 技能删除（我不会 SQL）
- 技能纠正（你记错了）

#### 流程：

用户输入 → LLM抽取技能变化 → 更新技能集合

#### 优势：

- 避免关键词误判
- 支持自然语言理解
- 提升多轮对话一致性

---

### 🧠 Agent 多步推理（LangGraph）

流程：

prepare_context → planner → route → tool → summarize

支持：

- 多步骤推理
- 条件分支
- 工具调用
- 推理可解释

---

### 💬 多会话聊天

- 多 Session 管理
- 聊天记录持久化（MySQL）
- 用户隔离（JWT）
- 支持连续追问

---

### ⚡ 流式输出

- 推理过程流式展示
- Token级输出
- 类 ChatGPT 体验

---

## 🧠 系统架构

用户 → 前端(Vue3) → FastAPI → LangGraph → Neo4j → LLM → 返回结果

---

## 🛠 技术栈

### 后端

- FastAPI
- SQLAlchemy
- MySQL
- Neo4j
- LangChain
- LangGraph

### 前端

- Vue3
- Vite
- Axios
- Streaming API

---

## 🌟 项目亮点

- LangGraph 多步推理 Agent
- 推理过程可视化
- 知识图谱融合
- LLM技能记忆系统（核心亮点）
- 多分支任务决策
- 类 ChatGPT 交互体验

---

## 🔮 后续优化

- 长期记忆（用户画像）
- RAG 检索增强
- LLM Planner
- Agent 可视化（LangSmith）

---


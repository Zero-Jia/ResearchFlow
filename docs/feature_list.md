# ResearchFlow 功能清单

## 一、核心功能

### 1. 研究任务输入
- 用户输入自然语言研究任务
- 系统识别任务类型

### 2. 多工具调用
- search_tool：搜索资料
- summarize_tool：总结长文本
- compare_tool：对比两个概念
- planning_tool：生成学习建议

### 3. 结构化研究报告
输出字段包括：
- topic
- task_type
- summary
- key_points
- comparison
- sources
- suggestions

### 4. 会话记忆
- 保存当前会话上下文
- 支持多轮研究任务连续执行

### 5. 用户偏好
- 记住输出风格
- 记住展示顺序
- 记住关注重点

### 6. 流式执行过程展示
- 正在分析任务
- 正在调用工具
- 正在整理结果
- 最终报告生成完成

### 7. 历史记录
- 保存历史研究任务
- 查看历史报告详情

### 8. Agent 可观测
- LangSmith 追踪模型调用
- 追踪工具调用链路
- 分析执行失败原因

## 二、项目亮点
- 基于 LangChain / LangGraph 的多工具 Agent
- 支持结构化输出
- 支持 WebSocket 流式展示
- 支持会话级上下文记忆
- 支持个性化偏好
- 支持 LangSmith tracing
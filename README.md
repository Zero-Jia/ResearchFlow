# JobKG-Agent

基于知识图谱与 LangChain v1 Agent 的智能职位推荐系统。

## 1. 项目简介

JobKG-Agent 面向计算机及人工智能相关专业学生，结合 知识图谱 与 LangChain
Agent，实现岗位推荐、技能差距分析、课程推荐、岗位对比和图谱可视化展示。

系统支持用户输入已有技能和职业问题，通过 Agent
调用图谱查询工具，返回结构化职位推荐结果，并支持任务历史记录和结果回溯。

## 2. 核心功能

-   职位推荐：根据用户技能推荐适合岗位
-   技能差距分析：识别目标岗位的缺失技能
-   课程推荐：根据缺失技能推荐学习课程
-   岗位对比：对比两个岗位的技能要求与匹配情况
-   历史任务记录：保存职位推荐任务与结果
-   图谱关系展示：展示 Job -\> Skill -\> Course 的知识图谱关系
-   前后端联调：提供输入页、结果页、历史页、详情页和图谱展示页

## 3. 技术栈

### 后端

-   FastAPI
-   SQLAlchemy
-   MySQL
-   Neo4j
-   LangChain v1
-   LangGraph
-   Pydantic

### 前端

-   Vue3
-   Vite
-   Vue Router
-   Axios

## 4. 启动方式

### 后端

cd backend source venv/bin/activate uvicorn app.main:app --reload

### 前端

cd frontend npm install npm run dev

## 5. 项目亮点

-   知识图谱与 Agent 结合
-   工具调用驱动推荐流程
-   结构化输出 + 数据库存储
-   历史记录与图谱展示增强可解释性

## 6. 后续扩展

-   引入真实数据集
-   增加用户节点
-   优化推荐算法
-   升级图谱可视化

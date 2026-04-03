# JobKG-Agent 模块迁移计划

## 1. 迁移目标
在现有 ResearchFlow Agent 项目基础上，将业务场景从“研究助理”迁移为“知识图谱职位推荐 Agent”。

## 2. 保留的模块
- FastAPI 项目骨架
- MySQL 数据库连接
- SQLAlchemy ORM
- llm_service
- LangChain v1 create_agent 调用方式
- 结构化输出能力
- research_task / research_report 的落库模式
- 历史任务查询接口模式

## 3. 需要替换的模块
### 旧 research 业务能力
- search_research_knowledge
- summarize_research_content
- compare_research_topics
- classify_research_task
- ResearchReport

### 新 job recommendation 业务能力
- recommend_jobs_by_skills
- analyze_skill_gap_for_job
- recommend_courses_for_missing_skills
- compare_jobs
- classify_job_task
- JobRecommendationReport

## 4. 迁移顺序
1. 业务定义与 schema 重构
2. 本地职位知识库版本跑通
3. Neo4j 接入
4. 图谱查询工具封装
5. 推荐算法接入
6. 历史记录与前端展示联通

## 5. 表层策略
短期内数据库表可以先不重命名，优先保证功能闭环。
后续如果需要再做语义层面的统一重构。

## 6. 迁移原则
- 优先复用已有 Agent 骨架
- 优先复用已有 route / service / schema 分层
- 先保证功能闭环，再逐步增强图谱与推荐算法
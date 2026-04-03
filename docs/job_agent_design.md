# JobKG-Agent 项目设计说明

## 1. 项目名称
JobKG-Agent：基于知识图谱与 LangChain Agent 的智能职位推荐系统

## 2. 项目定位
本项目面向计算机及人工智能相关专业学生，构建“岗位—技能—课程”知识图谱，并结合 LangChain v1 Agent 的工具调用、任务分类、结构化输出能力，实现岗位推荐、技能差距分析、课程补全建议和岗位对比。

## 3. 系统核心目标
- 根据用户已有技能推荐适合的岗位方向
- 分析推荐岗位与用户当前能力之间的差距
- 给出缺失技能及课程学习建议
- 支持自然语言交互式职业咨询
- 提供可解释的推荐结果

## 4. 核心实体与关系
### 实体
- User
- Job
- Skill
- Course

### 关系
- User -[:HAS]-> Skill
- Job -[:REQUIRES]-> Skill
- Course -[:TEACHES]-> Skill
- Job -[:SIMILAR_TO]-> Job
- Skill -[:RELATED_TO]-> Skill

## 5. 用户输入
- 技能列表输入，例如：Python、SQL、机器学习
- 自然语言输入，例如：我会 Python 和 SQL，适合什么岗位？

## 6. 系统输出
- Top-K 推荐岗位
- 岗位匹配度
- 已匹配技能
- 缺失技能
- 课程推荐
- 对比分析
- 学习建议

## 7. Agent 任务类型
- recommend_job
- analyze_gap
- recommend_course
- compare_job
- general_career_question

## 8. 目标工具清单
- recommend_jobs_by_skills
- analyze_skill_gap_for_job
- recommend_courses_for_missing_skills
- compare_jobs
- classify_job_task
- explain_agent_role
- get_current_project_name

## 9. 结构化输出设计
- task_type
- input_skills
- recommended_jobs
- job_match_scores
- matched_skills
- missing_skills
- course_recommendations
- comparison
- suggestions

## 10. 项目最终价值
本项目不仅实现职位推荐，还通过知识图谱与 Agent 的结合，让推荐过程具备可解释性、交互性与扩展性，适合作为知识图谱和 AI Agent 结合的综合项目。
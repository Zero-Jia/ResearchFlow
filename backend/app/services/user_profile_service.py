from typing import List
import re

from app.data.job_kg_mock import SKILL_ALIASES


class UserProfileService:
    def normalize_skills(self, skills: List[str]) -> List[str]:
        normalized = []
        for skill in skills:
            if not skill or not skill.strip():
                continue
            skill_key = skill.strip().lower()
            standard_skill = SKILL_ALIASES.get(skill_key, skill.strip())
            if standard_skill and standard_skill not in normalized:
                normalized.append(standard_skill)
        return normalized

    def extract_skills_from_question(self, question: str) -> List[str]:
        """
        规则版技能抽取（fallback 用）：
        只在“明确表达我会/我掌握/我熟悉/我的技能有”等语境下抽取技能，
        避免把“数据分析师”“后端开发”这种岗位/方向讨论误识别为已有技能。
        """
        if not question:
            return []

        question_lower = question.lower()

        positive_cues = [
            "我会", "我还会", "我掌握", "我熟悉", "我擅长",
            "我会用", "我使用过", "我学过", "我做过",
            "我的技能", "我的技能有", "我目前会", "我现在会",
            "i know", "i can", "i'm good at", "my skills", "i have experience in",
        ]

        if not any(cue in question_lower for cue in positive_cues):
            return []

        found_skills = []
        for alias, standard_skill in SKILL_ALIASES.items():
            alias_lower = alias.lower()

            if alias_lower not in question_lower:
                continue

            # 尽量避免把明显的岗位讨论抽成技能
            alias_pattern = re.escape(alias_lower)
            blocked_patterns = [
                alias_pattern + r"师",     # 如 数据分析师
                alias_pattern + r"岗位",
                alias_pattern + r"职位",
                alias_pattern + r"方向",
                alias_pattern + r"工作",
                alias_pattern + r"开发工程师",
                alias_pattern + r"工程师",
            ]
            if any(re.search(p, question_lower) for p in blocked_patterns):
                continue

            if standard_skill not in found_skills:
                found_skills.append(standard_skill)

        return found_skills

    def merge_skills(self, explicit_skills: List[str], question: str) -> List[str]:
        normalized_explicit = self.normalize_skills(explicit_skills)
        extracted_from_question = self.extract_skills_from_question(question)

        merged = list(normalized_explicit)
        for skill in extracted_from_question:
            if skill not in merged:
                merged.append(skill)

        return merged

    def build_skill_prompt(self, skills: List[str], question: str) -> str:
        clean_question = question.strip() if question else ""

        if not clean_question:
            clean_question = "请根据当前技能给出职位推荐建议。"

        if not skills:
            return clean_question

        skill_text = "、".join(skills)
        return f"用户当前技能：{skill_text}。问题：{clean_question}"


user_profile_service = UserProfileService()
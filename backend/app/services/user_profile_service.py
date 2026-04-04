from typing import List

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
        if not question:
            return []

        question_lower = question.lower()
        found_skills = []

        for alias, standard_skill in SKILL_ALIASES.items():
            if alias.lower() in question_lower and standard_skill not in found_skills:
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
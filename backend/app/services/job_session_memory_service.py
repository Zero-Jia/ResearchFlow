from __future__ import annotations

from typing import Dict, List


class JobSessionMemoryService:
    """
    基于 session_id 的简易技能记忆服务（进程内内存版）
    特点：
    1. 同一个 session_id 下，技能会持续累积
    2. 去重，保留原有顺序
    3. 适合当前原型阶段，服务重启后会丢失
    """

    def __init__(self):
        self._session_skills: Dict[int, List[str]] = {}

    @staticmethod
    def _normalize_skill(skill: str) -> str:
        return skill.strip()

    def _deduplicate(self, skills: List[str]) -> List[str]:
        seen = set()
        result = []
        for skill in skills:
            normalized = self._normalize_skill(skill)
            if not normalized:
                continue
            key = normalized.lower()
            if key in seen:
                continue
            seen.add(key)
            result.append(normalized)
        return result

    def get_skills(self, session_id: int) -> List[str]:
        return list(self._session_skills.get(session_id, []))

    def save_skills(self, session_id: int, skills: List[str]) -> List[str]:
        cleaned = self._deduplicate(skills)
        self._session_skills[session_id] = cleaned
        return list(cleaned)

    def merge_and_save_skills(self, session_id: int, new_skills: List[str]) -> List[str]:
        history_skills = self.get_skills(session_id)
        merged = history_skills + new_skills
        return self.save_skills(session_id, merged)

    def clear_session(self, session_id: int) -> None:
        self._session_skills.pop(session_id, None)


job_session_memory_service = JobSessionMemoryService()
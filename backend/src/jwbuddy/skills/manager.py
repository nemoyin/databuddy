from __future__ import annotations
from pathlib import Path
from jwbuddy.skills.loader import SkillLoader, SkillDefinition


class SkillManager:
    """管理所有已加载的 Skill"""

    def __init__(self, skills_dir: str):
        self._skills: dict[str, SkillDefinition] = {}
        self._skills_dir = Path(skills_dir)

    def discover(self) -> list[SkillDefinition]:
        """扫描 skills 目录，发现并加载所有 skill"""
        loaded = []
        if not self._skills_dir.exists():
            return loaded
        for item in self._skills_dir.iterdir():
            if item.is_dir():
                skill = SkillLoader.load_from_dir(item)
                if skill:
                    self._skills[skill.name] = skill
                    loaded.append(skill)
        return loaded

    def get(self, name: str) -> SkillDefinition | None:
        return self._skills.get(name)

    def list_skills(self) -> list[SkillDefinition]:
        return list(self._skills.values())

    def match_trigger(self, message: str) -> list[SkillDefinition]:
        """根据用户消息匹配触发词"""
        matched = []
        for skill in self._skills.values():
            for trigger in skill.triggers:
                import fnmatch
                if fnmatch.fnmatch(message, trigger):
                    matched.append(skill)
                    break
        return matched

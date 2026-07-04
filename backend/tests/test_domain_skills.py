"""Tests for domain-specific sample skills."""
from __future__ import annotations

from pathlib import Path
from jwbuddy.skills.loader import SkillLoader
from jwbuddy.skills.manager import SkillManager


def test_pension_skill_yaml_exists():
    """养老资金分析 skill.yaml 存在且可解析"""
    skills_dir = Path(__file__).parent.parent / "skills" / "pension-analysis"
    yaml_file = skills_dir / "skill.yaml"
    assert yaml_file.exists(), f"Expected {yaml_file}"

    skill = SkillLoader.load_from_dir(skills_dir)
    assert skill is not None
    assert skill.name == "pension-analysis"
    assert "养老" in skill.description
    assert len(skill.triggers) > 0
    assert len(skill.tools) > 0


def test_bidding_skill_yaml_exists():
    """招投标分析 skill.yaml 存在且可解析"""
    skills_dir = Path(__file__).parent.parent / "skills" / "bidding-analysis"
    yaml_file = skills_dir / "skill.yaml"
    assert yaml_file.exists(), f"Expected {yaml_file}"

    skill = SkillLoader.load_from_dir(skills_dir)
    assert skill is not None
    assert skill.name == "bidding-analysis"
    assert "招投标" in skill.description
    assert len(skill.triggers) > 0
    assert len(skill.tools) > 0


def test_skill_manager_discovers_domain_skills():
    """SkillManager 可发现所有领域 Skill"""
    skills_dir = Path(__file__).parent.parent / "skills"
    mgr = SkillManager(str(skills_dir))
    skills = mgr.discover()
    names = [s.name for s in skills]
    assert "pension-analysis" in names
    assert "bidding-analysis" in names


def test_sample_skill_still_loads():
    """原有 sample skill 仍然可加载"""
    skills_dir = Path(__file__).parent.parent / "skills" / "sample"
    skill = SkillLoader.load_from_dir(skills_dir)
    assert skill is not None
    assert skill.name == "sample-analysis"

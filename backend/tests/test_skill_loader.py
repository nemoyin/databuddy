import pytest
from jwbuddy.skills.manager import SkillManager
from jwbuddy.skills.loader import SkillLoader, SkillDefinition
from pathlib import Path


def _skills_dir() -> Path:
    """Resolve the skills directory relative to this test file."""
    # __file__ is backend/tests/test_skill_loader.py
    # parent.parent -> backend/
    d = Path(__file__).parent.parent / "skills"
    if d.exists():
        return d
    # fallback when CWD is backend/
    d = Path("skills")
    if d.exists():
        return d
    return Path(__file__).parent.parent / "skills"


@pytest.mark.asyncio
async def test_discover_skills():
    skills_dir = _skills_dir()
    mgr = SkillManager(str(skills_dir))
    skills = mgr.discover()
    names = [s.name for s in skills]
    assert "sample-analysis" in names


def test_load_skill_from_dir():
    skills_dir = _skills_dir()
    sample_dir = skills_dir / "sample"
    skill_def = SkillLoader.load_from_dir(sample_dir)
    assert skill_def is not None
    assert skill_def.name == "sample-analysis"
    assert skill_def.description == "示例数据分析 Skill"
    assert "示例*分析" in skill_def.triggers
    assert len(skill_def.tools) == 1
    assert skill_def.tools[0]["name"] == "sample_hello"


def test_skill_manager_get_and_list():
    skills_dir = _skills_dir()
    mgr = SkillManager(str(skills_dir))
    mgr.discover()
    assert mgr.get("sample-analysis") is not None
    assert mgr.get("nonexistent") is None
    assert len(mgr.list_skills()) >= 1


def test_skill_manager_match_trigger():
    skills_dir = _skills_dir()
    mgr = SkillManager(str(skills_dir))
    mgr.discover()
    matched = mgr.match_trigger("sample query")
    assert len(matched) >= 1
    assert matched[0].name == "sample-analysis"


def test_skill_manager_no_match():
    skills_dir = _skills_dir()
    mgr = SkillManager(str(skills_dir))
    mgr.discover()
    matched = mgr.match_trigger("unrelated message")
    assert len(matched) == 0


def test_load_nonexistent_dir():
    skill_def = SkillLoader.load_from_dir("/nonexistent/path")
    assert skill_def is None


def test_load_missing_yaml(tmp_path):
    skill_def = SkillLoader.load_from_dir(tmp_path)
    assert skill_def is None

from __future__ import annotations
import importlib.util
import yaml
from pathlib import Path
from pydantic import BaseModel


class SkillDefinition(BaseModel):
    name: str
    description: str = ""
    version: str = "0.1.0"
    triggers: list[str] = []
    tools: list[dict] = []
    mcp_servers: list[dict] = []
    workflow: list[dict] = []
    module_path: str = ""


class SkillLoader:
    """动态加载 Skill 目录"""

    @staticmethod
    def load_from_dir(dir_path: str | Path) -> SkillDefinition | None:
        path = Path(dir_path)
        yaml_file = path / "skill.yaml"
        if not yaml_file.exists():
            return None

        with open(yaml_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        skill_def = SkillDefinition(
            name=data.get("name", path.name),
            description=data.get("description", ""),
            version=data.get("version", "0.1.0"),
            triggers=data.get("triggers", []),
            tools=data.get("tools", []),
            mcp_servers=data.get("mcp_servers", []),
            workflow=data.get("workflow", []),
            module_path=str(path),
        )

        # Try loading Python module
        init_file = path / "__init__.py"
        if init_file.exists():
            spec = importlib.util.spec_from_file_location(
                f"skills.{skill_def.name}", init_file
            )
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)

        return skill_def

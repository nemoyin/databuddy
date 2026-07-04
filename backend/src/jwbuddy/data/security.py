from __future__ import annotations
import re

# SQL 关键字黑名单 — 禁止写操作
FORBIDDEN_PATTERNS = [
    r'\bINSERT\b', r'\bUPDATE\b', r'\bDELETE\b', r'\bDROP\b',
    r'\bALTER\b', r'\bCREATE\b', r'\bTRUNCATE\b', r'\bREPLACE\b',
    r'\bGRANT\b', r'\bREVOKE\b', r'\bEXEC\b', r'\bEXECUTE\b',
]


def validate_readonly(sql: str) -> bool:
    """检查 SQL 是否只读，通过则返回 True"""
    # Remove string literals to avoid false positives
    cleaned = re.sub(r"'[^']*'", '', sql)
    cleaned = re.sub(r'"[^"]*"', '', cleaned)
    cleaned = re.sub(r'--.*$', '', cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)

    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, cleaned, re.IGNORECASE):
            return False
    return True

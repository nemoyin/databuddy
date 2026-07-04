from __future__ import annotations
from pathlib import Path
from jwbuddy.tools.base import BaseTool, ToolSpec, ToolResult


class DocumentTool(BaseTool):
    """文档解析工具：支持 PDF、Word、图片文本提取"""

    def __init__(self, upload_dir: str = "data/uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="document_parse",
            description="解析上传的文档 (PDF/Word/图片)，提取文本内容",
            parameters={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "上传文件的路径",
                    },
                    "extract_mode": {
                        "type": "string",
                        "description": "提取模式 (预留)",
                        "enum": ["text", "structured", "ocr"],
                        "default": "text",
                    },
                },
                "required": ["file_path"],
            },
        )

    async def execute(self, **kwargs) -> ToolResult:
        file_path = kwargs.get("file_path", "")

        path = Path(file_path)

        # Block path traversal via parent directory references
        if ".." in path.parts:
            return ToolResult(success=False, error="文件路径不允许")

        # Resolve non-absolute paths within upload_dir
        if not path.is_absolute():
            path = (self.upload_dir / path).resolve()

        if not path.exists():
            return ToolResult(success=False, error=f"文件不存在: {file_path}")

        suffix = path.suffix.lower()
        try:
            if suffix == ".pdf":
                text = self._extract_pdf(path)
            elif suffix in (".docx", ".doc"):
                text = self._extract_docx(path)
            elif suffix in (".txt", ".md", ".csv", ".json"):
                text = path.read_text(encoding="utf-8")
            elif suffix in (".xlsx", ".xls"):
                text = self._extract_excel(path)
            elif suffix in (".png", ".jpg", ".jpeg"):
                text = f"[图片文件: {path.name}] 需要 OCR 服务"
            else:
                return ToolResult(success=False, error=f"不支持的文件格式: {suffix}")

            return ToolResult(
                success=True,
                data={"filename": path.name, "content": text[:10000], "length": len(text)},
                format="text",
            )
        except Exception as e:
            return ToolResult(success=False, error=f"文档解析失败: {e}")

    def _extract_pdf(self, path: Path) -> str:
        """提取 PDF 文本（MVP 用 pypdf 简单提取）"""
        try:
            from pypdf import PdfReader
        except ImportError:
            return f"[需要安装 pypdf 来解析 PDF: {path.name}]"
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    def _extract_docx(self, path: Path) -> str:
        """提取 Word 文本"""
        try:
            from docx import Document
        except ImportError:
            return f"[需要安装 python-docx 来解析 Word: {path.name}]"
        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs)

    def _extract_excel(self, path: Path) -> str:
        """提取 Excel 表格内容"""
        try:
            from openpyxl import load_workbook
        except ImportError:
            return f"[需要安装 openpyxl 来解析 Excel: {path.name}]"
        wb = load_workbook(str(path), read_only=True, data_only=True)
        parts = []
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            rows = list(ws.iter_rows(values_only=True))
            if not rows:
                continue
            parts.append(f"--- Sheet: {sheet_name} ---")
            parts.append(" | ".join(str(c or "") for c in rows[0]))
            parts.append("-" * 60)
            for row in rows[1:21]:  # 最多 20 行
                parts.append(" | ".join(str(c or "") for c in row))
            if len(rows) > 21:
                parts.append(f"... (共 {len(rows)-1} 行数据)")
        wb.close()
        return "\n".join(parts)

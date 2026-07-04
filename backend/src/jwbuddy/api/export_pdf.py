"""PDF 导出 API — 将分析报告导出为 PDF（支持中文）"""
from __future__ import annotations

import os
from datetime import datetime
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from fpdf import FPDF

router = APIRouter(prefix="/export", tags=["export"])


class ExportRequest(BaseModel):
    title: str = "JWBuddy 分析报告"
    content: str = ""
    tables: list[dict] = []


def _find_chinese_font() -> tuple[str | None, str | None]:
    """返回 (字体路径, 粗体路径)"""
    # 优先使用 .ttf 字体（fpdf2 对 .ttc 支持有限）
    ttf_candidates = [
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\SIMFANG.ttf",
        r"C:\Windows\Fonts\SIMLI.ttf",
    ]
    ttc_candidates = [
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\msyhbd.ttc",
    ]
    for path in ttf_candidates:
        if os.path.exists(path):
            return path, None  # 粗体复用同一字体
    for path in ttc_candidates:
        if os.path.exists(path):
            return path, None
    return None, None


@router.post("/pdf")
async def export_pdf(req: ExportRequest):
    """将文本分析报告导出为 PDF 文件"""
    if not req.content.strip():
        raise HTTPException(status_code=400, detail="内容不能为空")

    pdf = FPDF()
    pdf.add_page()

    # 注册中文字体
    font_path, bold_path = _find_chinese_font()
    if font_path:
        pdf.add_font("zh", "", font_path, )
        try:
            pdf.add_font("zh", "B", font_path, )
        except Exception:
            pass  # 无独立粗体文件时复用常规
        FONT = "zh"
    else:
        # 无中文字体时使用 DejaVu（fpdf2 内置，支持基本 Unicode）
        pdf.add_font("zh", "", "DejaVuSans.ttf", )
        pdf.add_font("zh", "B", "DejaVuSans-Bold.ttf", )
        FONT = "zh"

    # 标题
    pdf.set_font(FONT, "B", 16)
    pdf.cell(0, 15, req.title, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(3)

    # 日期
    pdf.set_font(FONT, "", 8)
    pdf.cell(0, 8, f"生成日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}", new_x="LMARGIN", new_y="NEXT", align="R")
    pdf.ln(3)

    # 分隔线
    pdf.set_draw_color(180, 180, 180)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(5)

    # 正文 — 按 Markdown 结构渲染
    pdf.set_font(FONT, "", 10)
    for line in req.content.split("\n"):
        line = line.strip()
        if not line:
            pdf.ln(2)
            continue

        # 二级标题
        if line.startswith("##"):
            pdf.set_font(FONT, "B", 12)
            clean = line.lstrip("#").strip().lstrip("*").strip()
            pdf.multi_cell(0, 8, clean)
            pdf.set_font(FONT, "", 10)

        # 粗体行（强调）
        elif line.startswith("**") and line.endswith("**"):
            pdf.set_font(FONT, "B", 10)
            pdf.multi_cell(0, 6, line.strip("*"))
            pdf.set_font(FONT, "", 10)

        # 无序列表
        elif line.startswith("-") or line.startswith("*"):
            pdf.set_x(20)
            pdf.multi_cell(0, 6, line[1:].strip())

        # 表格行（用空格模拟）
        elif line.startswith("|"):
            continue

        # 普通段落
        else:
            pdf.multi_cell(0, 6, line)

    # 表格 — 渲染 tool_result 中的表格数据
    for table in req.tables:
        rows = table.get("rows", [])
        if not rows:
            continue
        cols = table.get("columns", [])
        if not cols and rows:
            cols = list(rows[0].keys()) if isinstance(rows[0], dict) else []
        if not cols:
            continue

        pdf.ln(4)
        summary = table.get("summary", "")
        if summary:
            pdf.set_font(FONT, "B", 9)
            pdf.multi_cell(0, 6, summary[:80])
            pdf.ln(2)

        # 表头
        pdf.set_font(FONT, "B", 7)
        pdf.set_fill_color(230, 230, 240)
        col_w = max(18, min(50, 180 // max(len(cols), 1)))
        for col in cols:
            pdf.cell(col_w, 7, str(col)[:10], border=1, fill=True, align="C")
        pdf.ln()

        # 数据行（最多 15 行）
        pdf.set_font(FONT, "", 7)
        for row in rows[:15]:
            for col in cols:
                val = str(row.get(col, "") if isinstance(row, dict) else "")[:12]
                pdf.cell(col_w, 6, val, border=1)
            pdf.ln()

        total = table.get("total_rows", 0)
        if total > 15:
            pdf.set_font(FONT, "", 7)
            pdf.cell(0, 6, f"... 共 {total} 行", new_x="LMARGIN", new_y="NEXT")

    # 图表无法直接导出为 PDF 图片，在末尾添加说明
    pdf.ln(5)
    pdf.set_font(FONT, "", 8)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 5, "注：交互式图表可在 JWBuddy Web 端查看", new_x="LMARGIN", new_y="NEXT")

    pdf_bytes = bytes(pdf.output())
    from urllib.parse import quote
    safe_filename = f"{quote(req.title)}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{safe_filename}",
        },
    )

"""Build GOST-ish DOCX from the coursework markdown + screenshots."""
from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Cm, Mm, Pt, Inches

STORE_MD = Path(
    r"C:\Users\batma\AppData\Local\Cursor\AgentStores\cursor_agent_stores"
    r"\bc-d722bd0a-0447-4b63-aad2-3cd2e9b5400f\files\docs\kursovaya-swaga-batmanov.md"
)
STORE_MEDIA = Path(
    r"C:\Users\batma\AppData\Local\Cursor\AgentStores\cursor_agent_stores"
    r"\bc-d722bd0a-0447-4b63-aad2-3cd2e9b5400f\files\media\kursovaya"
)
OUT_STORE = STORE_MD.with_suffix(".docx")
OUT_REPO = Path(r"C:\Users\batma\Projects\kurscach\docs\kursovaya\kursovaya-swaga-batmanov.docx")


def set_run_font(run, size=12, bold=False, italic=False):
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic


def style_doc(doc: Document) -> None:
    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.left_margin = Mm(30)
    section.right_margin = Mm(15)
    section.top_margin = Mm(20)
    section.bottom_margin = Mm(20)
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(12)
    style._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    pf = style.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.space_after = Pt(0)
    pf.space_before = Pt(0)


def add_para(doc, text, *, size=12, bold=False, italic=False, align="justify", first_line=True):
    p = doc.add_paragraph()
    if align == "center":
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif align == "right":
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    else:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if first_line and align == "justify":
        p.paragraph_format.first_line_indent = Cm(1.25)
    else:
        p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(text)
    set_run_font(run, size=size, bold=bold, italic=italic)
    return p


def add_heading_custom(doc, text, level=1):
    sizes = {0: 14, 1: 14, 2: 13, 3: 12}
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if level <= 1 else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(text)
    set_run_font(run, size=sizes.get(level, 12), bold=True)
    return p


def insert_image(doc, filename: str, caption: str) -> None:
    path = STORE_MEDIA / filename
    if path.exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        run = p.add_run()
        # keep width reasonable for A4 with margins
        run.add_picture(str(path), width=Cm(15.5))
    add_para(doc, caption, size=12, bold=False, align="center", first_line=False)


def parse_md_to_docx(md_text: str, doc: Document) -> None:
    lines = md_text.splitlines()
    i = 0
    in_code = False
    table_buf: list[str] = []

    def flush_table():
        nonlocal table_buf
        if not table_buf:
            return
        rows = []
        for row in table_buf:
            if re.match(r"^\|?\s*-+", row):
                continue
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            rows.append(cells)
        table_buf = []
        if not rows:
            return
        cols = max(len(r) for r in rows)
        table = doc.add_table(rows=len(rows), cols=cols)
        table.style = "Table Grid"
        for r_idx, row in enumerate(rows):
            for c_idx in range(cols):
                cell = table.cell(r_idx, c_idx)
                cell.text = row[c_idx] if c_idx < len(row) else ""
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        set_run_font(run, size=10, bold=(r_idx == 0))
        doc.add_paragraph()

    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            flush_table()
            in_code = not in_code
            i += 1
            continue
        if in_code:
            add_para(doc, line, size=10, align="left", first_line=False)
            i += 1
            continue
        if line.strip().startswith("|"):
            table_buf.append(line)
            i += 1
            continue
        else:
            flush_table()

        img = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line.strip())
        if img:
            alt, src = img.group(1), img.group(2)
            name = Path(src).name
            # caption may be previous "Рисунок..." line already added; still add short note
            insert_image(doc, name, alt if alt.startswith("Рисунок") else f"({name})")
            i += 1
            continue

        if line.startswith("# "):
            add_heading_custom(doc, line[2:].strip(), 0)
        elif line.startswith("## "):
            add_heading_custom(doc, line[3:].strip(), 1)
        elif line.startswith("### "):
            add_heading_custom(doc, line[4:].strip(), 2)
        elif line.startswith("#### "):
            add_heading_custom(doc, line[5:].strip(), 3)
        elif line.startswith("---"):
            pass
        elif line.strip().startswith("> "):
            add_para(doc, line.strip()[2:], size=11, italic=True, align="left", first_line=False)
        elif line.strip().startswith("- "):
            add_para(doc, "– " + line.strip()[2:], align="justify", first_line=False)
        elif re.match(r"^\d+\.\s", line.strip()):
            add_para(doc, line.strip(), align="justify", first_line=False)
        elif line.strip() == "":
            pass
        else:
            # strip simple markdown bold/italic markers for body
            text = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)
            text = re.sub(r"`([^`]+)`", r"\1", text)
            text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
            add_para(doc, text, align="justify", first_line=True)
        i += 1
    flush_table()


def main() -> None:
    md = STORE_MD.read_text(encoding="utf-8")
    doc = Document()
    style_doc(doc)
    parse_md_to_docx(md, doc)
    OUT_STORE.parent.mkdir(parents=True, exist_ok=True)
    OUT_REPO.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUT_STORE))
    doc.save(str(OUT_REPO))
    print("wrote", OUT_STORE)
    print("wrote", OUT_REPO)


if __name__ == "__main__":
    main()

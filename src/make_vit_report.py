"""Build the VIT project report -> VIT_REPORT.docx

Runs in two passes. The first lays the document out with blank page numbers, renders it to
PDF and reads back which page each heading, figure and table landed on; the second rebuilds
it with those numbers filled into the contents, list of figures and list of tables.

    python src/make_vit_report.py            # two passes, real page numbers
    python src/make_vit_report.py --fast     # one pass, page numbers left blank
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

import vit_content as C
from config import FIGURES, ROOT
from vit_format import (BODY, bullets, body_section, caption, code, figure,
                        front_matter_numbering, para, setup, table)

OUT = ROOT / "VIT_REPORT.docx"
LOGO = ROOT / "assets" / "vit_logo.png"
SOFFICE = "/Applications/LibreOffice.app/Contents/MacOS/soffice"


# ---------------------------------------------------------------- front matter

def cover(doc, m):
    para(doc, m["course"], align="center", size=14, bold=True, space_after=26)
    para(doc, m["title"].upper(), align="center", size=18, bold=True, line=1.5, space_after=26)
    para(doc, "Submitted in partial fulfillment of the requirements for the degree of",
         align="center", size=12, space_after=12)
    para(doc, m["degree"], align="center", size=14, bold=True, space_after=10)
    para(doc, "in", align="center", size=12, space_after=10)
    para(doc, m["programme"], align="center", size=14, bold=True, space_after=20)
    para(doc, "by", align="center", size=12, space_after=12)
    t = doc.add_table(rows=len(m["students"]), cols=2)
    t.alignment = 1
    for i, (reg, name) in enumerate(m["students"]):
        for j, text in enumerate((reg, name)):
            cell = t.cell(i, j)
            cell.text = ""
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(2)
            run = p.add_run(text)
            run.font.name = BODY
            run.font.size = Pt(13)
            run.bold = True
        t.rows[i].cells[0].width = Cm(4.5)
        t.rows[i].cells[1].width = Cm(7.5)
    para(doc, "", space_after=18)
    para(doc, "Under the Supervision of", align="center", size=12, space_after=10)
    para(doc, m["guide"], align="center", size=14, bold=True, space_after=4)
    para(doc, m["designation"], align="center", size=12, space_after=4)
    para(doc, m["school"], align="center", size=12, space_after=22)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(6)
    p.add_run().add_picture(str(LOGO), width=Cm(5.4))
    para(doc, "Vellore Institute of Technology, Vellore - 632 014", align="center", size=12,
         space_after=16)
    para(doc, m["month"], align="center", size=13, bold=True, space_after=0)


def declaration(doc, m):
    para(doc, "DECLARATION", align="center", size=16, bold=True, line=1.5, space_after=22)
    names = ", ".join(f"{n} ({r})" for r, n in m["students"])
    para(doc,
         f"We hereby declare that the project entitled “{m['title']}” submitted by "
         f"us, for the award of the degree of {m['degree']} in {m['programme']} to Vellore "
         f"Institute of Technology, is a record of bonafide work carried out by us under the "
         f"supervision of {m['guide']}.",
         line=1.5, space_after=14)
    para(doc,
         "We further declare that the work reported in this project has not been submitted "
         "and will not be submitted, either in part or in full, for the award of any other "
         "degree or diploma in this institute or any other institute or university.",
         line=1.5, space_after=30)
    para(doc, f"Place : {m['place']}", align="left", space_after=4)
    para(doc, "Date  :", align="left", space_after=40)
    para(doc, names, align="left", size=11, space_after=6)
    para(doc, "Signature of the Candidates", align="left", space_after=0)


def certificate(doc, m):
    para(doc, "CERTIFICATE", align="center", size=16, bold=True, line=1.5, space_after=22)
    names = ", ".join(f"{n} ({r})" for r, n in m["students"])
    para(doc,
         f"This is to certify that the project entitled “{m['title']}” submitted by "
         f"{names}, {m['school']}, Vellore Institute of Technology, for the award of the "
         f"degree of {m['degree']} in {m['programme']}, is a record of bonafide work carried "
         f"out by them under my supervision during {m['semester']}, as per the VIT code of "
         f"academic and research ethics.",
         line=1.5, space_after=14)
    para(doc,
         "The contents of this report have not been submitted and will not be submitted "
         "either in part or in full, for the award of any other degree or diploma in this "
         "institute or any other institute or university. The project fulfills the "
         "requirements and regulations of the University and in my opinion meets the "
         "necessary standards for submission.",
         line=1.5, space_after=36)
    para(doc, f"Place : {m['place']}", align="left", space_after=4)
    para(doc, "Date  :", align="left", space_after=36)
    para(doc, m["guide"], align="left", space_after=2)
    para(doc, "Signature of the Guide", align="left", space_after=40)
    para(doc, "Examiner(s)", align="right", space_after=30)
    para(doc, "Head of the Department", align="center", space_after=2)
    para(doc, m["programme"], align="center", space_after=0)


def contents_table(doc, entries):
    para(doc, "TABLE OF CONTENTS", align="center", size=16, bold=True, line=1.5, space_after=16)
    rows = [[sl, title, page] for sl, title, page in entries]
    table(doc, ["Sl. No.", "Contents", "Page No."], rows, widths=[12, 72, 14], size=11,
          align_left=(1,))


def list_table(doc, heading, header, rows):
    para(doc, heading, align="center", size=16, bold=True, line=1.5, space_after=16)
    if rows:
        table(doc, header, rows, widths=[14, 72, 14], size=11, align_left=(1,))
    else:
        para(doc, "None.", align="left")


def two_col_table(doc, heading, rows, note=None):
    para(doc, heading, align="center", size=16, bold=True, line=1.5, space_after=16)
    table(doc, ["Abbreviation", "Expansion"] if "ABBREV" in heading else ["Symbol", "Meaning"],
          rows, widths=[22, 64], size=11, align_left=(0, 1))
    if note:
        para(doc, note, align="left", size=10, italic=True)


def abstract(doc):
    para(doc, "ABSTRACT", align="center", size=16, bold=True, line=1.5, space_after=16)
    for text in C.ABSTRACT:
        para(doc, text, line=1.15, space_after=8)


# ---------------------------------------------------------------- body

def render_blocks(doc, blocks, chapter, index):
    """Render one chapter's blocks, numbering its figures and tables as chapter.n."""
    fig_n = tab_n = 0
    section_n = sub_n = 0
    for block in blocks:
        kind = block[0]
        if kind == "h2":
            section_n += 1
            sub_n = 0
            text = f"{chapter}.{section_n} {block[1]}"
            para(doc, text, align="left", size=13, bold=True, space_after=8, line=1.0,
                 keep_with_next=True)
            index["headings"].append((f"{chapter}.{section_n} {block[1]}", text))
        elif kind == "h3":
            sub_n += 1
            text = f"{chapter}.{section_n}.{sub_n} {block[1]}"
            para(doc, text, align="left", size=12, bold=True, italic=True, space_after=6,
                 line=1.0, keep_with_next=True)
            index["headings"].append((text, text))
        elif kind == "p":
            para(doc, block[1])
        elif kind == "bullet":
            bullets(doc, block[1])
        elif kind == "num":
            bullets(doc, block[1], numbered=True)
        elif kind == "quote":
            para(doc, block[1], italic=True, indent=1.0, space_after=10)
        elif kind == "code":
            code(doc, block[1])
        elif kind == "table":
            tab_n += 1
            label = f"Table {chapter}.{tab_n}  {block[1]}"
            caption(doc, label, keep_with_next=True)
            widths = block[4] if len(block) > 4 else None
            table(doc, block[2], block[3], widths=widths)
            index["tables"].append((f"{chapter}.{tab_n}", block[1], label))
        elif kind == "figure":
            fig_n += 1
            path = FIGURES / block[1]
            width = block[3] if len(block) > 3 else 14.0
            figure(doc, path, width_cm=width)
            label = f"Figure {chapter}.{fig_n}  {block[2]}"
            caption(doc, label)
            index["figures"].append((f"{chapter}.{fig_n}", block[2], label))
        else:
            raise ValueError(f"unknown block kind {kind!r}")


def chapter_heading(doc, number, title, first=False):
    p = para(doc, f"CHAPTER {number}", align="center", size=14, bold=True, space_after=10,
             line=1.5, keep_with_next=True)
    if not first:
        p.paragraph_format.page_break_before = True
    para(doc, f"{number}. {title}", align="center", size=14, bold=True, space_after=16,
         line=1.5, keep_with_next=True)


def references(doc, index, number):
    chapter_heading(doc, number, "REFERENCES")
    index["headings"].append((f"{number}. REFERENCES", f"{number}. REFERENCES"))
    for i, ref in enumerate(C.REFERENCES, start=1):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.left_indent = Cm(1.0)
        p.paragraph_format.first_line_indent = Cm(-1.0)
        run = p.add_run(f"[{i}]\t{ref}")
        run.font.name = BODY
        run.font.size = Pt(11)


def appendix(doc, index):
    p = para(doc, "APPENDIX A - SAMPLE CODE", align="center", size=14, bold=True,
             space_after=16, line=1.5, keep_with_next=True)
    p.paragraph_format.page_break_before = True
    index["headings"].append(("APPENDIX A - SAMPLE CODE", "APPENDIX A - SAMPLE CODE"))
    for block in C.APPENDIX:
        if block[0] == "h2":
            para(doc, block[1], align="left", size=12, bold=True, space_after=6, line=1.0,
                 keep_with_next=True)
        elif block[0] == "p":
            para(doc, block[1])
        elif block[0] == "code":
            code(doc, block[1], size=7.5)


# ---------------------------------------------------------------- assembly

def build(pages):
    """Assemble the document. `pages` maps a lookup key to a page number string."""
    doc = Document()
    setup(doc)
    index = {"headings": [], "figures": [], "tables": []}

    cover(doc, C.META)
    for fn in (declaration, certificate):
        doc.add_page_break()
        fn(doc, C.META)

    # Render the body into a throwaway run first so the contents can be built from it.
    body = []
    for number, title, key in C.CHAPTERS:
        body.append((number, title, getattr(C, key)))

    toc_entries = []
    for number, title, blocks in body:
        toc_entries.append((f"{number}.", f"{title}", pages.get(f"{number}. {title}", "")))
        sec = sub = 0
        for block in blocks:
            if block[0] == "h2":
                sec += 1
                sub = 0
                label = f"{number}.{sec} {block[1]}"
                toc_entries.append(("", label, pages.get(label, "")))
            elif block[0] == "h3":
                sub += 1
                label = f"{number}.{sec}.{sub} {block[1]}"
                toc_entries.append(("", label, pages.get(label, "")))
    toc_entries.insert(0, ("", "Abstract", pages.get("ABSTRACT", "")))
    toc_entries.append(("9.", "REFERENCES", pages.get("9. REFERENCES", "")))
    toc_entries.append(("", "APPENDIX A - SAMPLE CODE", pages.get("APPENDIX A - SAMPLE CODE", "")))

    doc.add_page_break()
    contents_table(doc, toc_entries)

    doc.add_page_break()
    list_table(doc, "LIST OF FIGURES", ["Figure No.", "Title", "Page No."],
               [[n, t, pages.get(f"FIG {n}", "")] for n, t, _ in FIG_INDEX])
    doc.add_page_break()
    list_table(doc, "LIST OF TABLES", ["Table No.", "Title", "Page No."],
               [[n, t, pages.get(f"TAB {n}", "")] for n, t, _ in TAB_INDEX])
    doc.add_page_break()
    two_col_table(doc, "LIST OF ABBREVIATIONS", [list(x) for x in C.ABBREVIATIONS])
    doc.add_page_break()
    two_col_table(doc, "SYMBOLS AND NOTATIONS", [list(x) for x in C.SYMBOLS])
    doc.add_page_break()
    abstract(doc)

    front_matter_numbering(doc)
    body_section(doc)

    for i, (number, title, blocks) in enumerate(body):
        chapter_heading(doc, number, title, first=(i == 0))
        index["headings"].append((f"{number}. {title}", f"{number}. {title}"))
        render_blocks(doc, blocks, number, index)
    references(doc, index, 9)
    appendix(doc, index)

    doc.save(OUT)
    return index


def page_map(index):
    """Render to PDF and read back the page each labelled item landed on."""
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([SOFFICE, "--headless", "--convert-to", "pdf", "--outdir", tmp, str(OUT)],
                       check=True, capture_output=True, timeout=600)
        pdf = next(Path(tmp).glob("*.pdf"))
        txt = Path(tmp) / "out.txt"
        subprocess.run(["pdftotext", "-layout", str(pdf), str(txt)], check=True)
        pages = txt.read_text(errors="replace").split("\f")

    def norm(s):
        return re.sub(r"\s+", " ", s).strip().lower()

    # Front matter is numbered in roman, the body in arabic restarting at 1.
    body_start = next((i for i, p in enumerate(pages) if norm("CHAPTER 1") in norm(p)), 0)
    normed = [norm(p) for p in pages]

    def find(needle, start=0):
        n = norm(needle)
        for i in range(start, len(normed)):
            if n in normed[i]:
                return i
        return None

    out = {}
    for key, text in index["headings"]:
        i = find(text, body_start)
        if i is not None:
            out[key] = str(i - body_start + 1)
    for num, title, label in index["figures"]:
        i = find(label, body_start)
        if i is not None:
            out[f"FIG {num}"] = str(i - body_start + 1)
    for num, title, label in index["tables"]:
        i = find(label, body_start)
        if i is not None:
            out[f"TAB {num}"] = str(i - body_start + 1)
    for i in range(body_start - 1, -1, -1):
        if "machine-learning models are widely used" in normed[i]:
            out["ABSTRACT"] = _roman(i + 1)
            break
    return out


def _roman(n):
    vals = ((10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i"))
    s = ""
    for v, sym in vals:
        while n >= v:
            s += sym
            n -= v
    return s


def collect_index():
    """Figure and table numbers, derived from the content without rendering."""
    figs, tabs = [], []
    for number, title, key in C.CHAPTERS:
        f = t = 0
        for block in getattr(C, key):
            if block[0] == "figure":
                f += 1
                figs.append((f"{number}.{f}", block[2], f"Figure {number}.{f}  {block[2]}"))
            elif block[0] == "table":
                t += 1
                tabs.append((f"{number}.{t}", block[1], f"Table {number}.{t}  {block[1]}"))
    return figs, tabs


FIG_INDEX, TAB_INDEX = collect_index()


def main():
    fast = "--fast" in sys.argv
    index = build({})
    print(f"pass 1: {len(FIG_INDEX)} figures, {len(TAB_INDEX)} tables, "
          f"{len(index['headings'])} headings")
    if fast:
        print("wrote", OUT, "(page numbers left blank)")
        return
    if not Path(SOFFICE).exists():
        print("LibreOffice not found; page numbers left blank")
        return
    pages = page_map(index)
    build(pages)
    print(f"pass 2: resolved {len(pages)} page references")
    print("wrote", OUT)


if __name__ == "__main__":
    main()

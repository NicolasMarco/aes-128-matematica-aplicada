"""
Ajusta reference.docx y convierte informe_aes_draft.md a informe_aes.docx
con estilos profesionales (Times New Roman, justificado, encabezados centrados).
"""

import subprocess
import sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

PANDOC = r"C:\Users\Nicolás\AppData\Local\Microsoft\WinGet\Packages\JohnMacFarlane.Pandoc_Microsoft.Winget.Source_8wekyb3d8bbwe\pandoc-3.10\pandoc.exe"
BASE_DIR = r"C:\Repositorios\AES - Criptografia\docs"
REF_IN   = BASE_DIR + r"\reference.docx"
REF_OUT  = BASE_DIR + r"\reference_custom.docx"
MD_IN    = BASE_DIR + r"\informe_aes_draft.md"
DOCX_OUT = BASE_DIR + r"\informe_aes.docx"


def set_font(run_or_rpr, name, size_pt, bold=False, italic=False, underline=False, color=None):
    run_or_rpr.font.name = name
    run_or_rpr.font.size = Pt(size_pt)
    run_or_rpr.font.bold = bold
    run_or_rpr.font.italic = italic
    run_or_rpr.font.underline = underline
    if color:
        run_or_rpr.font.color.rgb = RGBColor(*color)


def style_paragraph(style, font_name, font_size, bold=False, italic=False,
                     underline=False, align=WD_ALIGN_PARAGRAPH.LEFT,
                     space_before=0, space_after=6, first_indent=0):
    pf = style.paragraph_format
    pf.alignment = align
    pf.space_before = Pt(space_before)
    pf.space_after = Pt(space_after)
    pf.first_line_indent = Cm(first_indent)
    pf.widow_control = True

    rf = style.font
    rf.name = font_name
    rf.size = Pt(font_size)
    rf.bold = bold
    rf.italic = italic
    rf.underline = underline


def build_reference():
    doc = Document(REF_IN)

    # ── Márgenes de página ──────────────────────────────────────────────────
    for section in doc.sections:
        section.top_margin    = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin   = Cm(3.0)
        section.right_margin  = Cm(2.5)

    styles = doc.styles

    # ── Normal (cuerpo) ──────────────────────────────────────────────────────
    style_paragraph(styles["Normal"],
                    font_name="Times New Roman", font_size=11,
                    align=WD_ALIGN_PARAGRAPH.JUSTIFY,
                    space_before=0, space_after=6, first_indent=0)

    # ── Heading 1  →  # en md  (título del documento) ────────────────────────
    style_paragraph(styles["Heading 1"],
                    font_name="Times New Roman", font_size=14,
                    bold=True, align=WD_ALIGN_PARAGRAPH.CENTER,
                    space_before=0, space_after=12)

    # ── Heading 2  →  ## en md  (secciones principales: I. CONTEXTO, etc.) ──
    style_paragraph(styles["Heading 2"],
                    font_name="Times New Roman", font_size=12,
                    bold=True, underline=True,
                    align=WD_ALIGN_PARAGRAPH.CENTER,
                    space_before=14, space_after=6)

    # ── Heading 3  →  ### en md  (subsecciones: A. El Problema, etc.) ────────
    style_paragraph(styles["Heading 3"],
                    font_name="Times New Roman", font_size=11,
                    bold=True,
                    align=WD_ALIGN_PARAGRAPH.LEFT,
                    space_before=10, space_after=4)

    # ── Verbatim / Code Block ─────────────────────────────────────────────────
    from docx.enum.style import WD_STYLE_TYPE
    for sname in ("Verbatim", "Source Code", "Compact"):
        if sname in [s.name for s in styles]:
            s = styles[sname]
            if s.type == WD_STYLE_TYPE.PARAGRAPH:
                style_paragraph(s, font_name="Courier New", font_size=9,
                                align=WD_ALIGN_PARAGRAPH.LEFT,
                                space_before=4, space_after=4)

    doc.save(REF_OUT)
    print(f"  Plantilla guardada: {REF_OUT}")


def convert():
    cmd = [
        PANDOC,
        MD_IN,
        "--from", "markdown",
        "--to", "docx",
        f"--reference-doc={REF_OUT}",
        "--output", DOCX_OUT,
        "--standalone",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("ERROR pandoc:", result.stderr)
        sys.exit(1)
    print(f"  Documento generado: {DOCX_OUT}")


if __name__ == "__main__":
    print("1/2  Construyendo plantilla de estilos...")
    build_reference()
    print("2/2  Convirtiendo markdown a docx...")
    convert()
    print("\nListo.")

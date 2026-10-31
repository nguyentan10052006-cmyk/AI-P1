"""Dựng docs/report/Report.pdf từ các file Markdown trong docs/report.

    python3 build.py              # pandoc chuyển Markdown sang LaTeX (chapters/), rồi XeLaTeX 3 lượt
    python3 build.py --tex-only   # chỉ biên dịch lại LaTeX, không cần pandoc (sau khi sửa info.tex)

Cần: pandoc 3.x (hoặc `pip install pypandoc_binary`) và XeLaTeX (MiKTeX, TeX Live hoặc Overleaf).
Trên WSL, script tự tìm xelatex.exe của MiKTeX bên Windows.
"""
from __future__ import annotations

import glob
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # docs/report/latex
MD = HERE.parent                                # docs/report
OUT = HERE / "chapters"

# (tên file .tex, file Markdown hoặc (file, phần), độ dời cấp tiêu đề)
# "##" là chương khi dời -1; các mục 3.x và 5.4.x viết "##"/"###" nên giữ nguyên cấp (0).
PARTS = [
    ("00-tom-tat", "0-tom-tat.md", -1),
    ("01-phan-cong", "1-phan-cong.md", -1),
    ("02-mo-hinh-hoa", "2-mo-hinh-hoa.md", -1),
    ("03-thuat-toan", "3-thuat-toan.md", -1),
    ("03-1-bfs", "3.1-bfs.md", 0),
    ("03-2-dfs", "3.2-dfs.md", 0),
    ("03-3-ucs", "3.3-ucs.md", 0),
    ("03-4-astar", "3.4-astar.md", 0),
    ("04-cai-dat", "4-cai-dat-giao-dien.md", -1),
    ("05-thuc-nghiem-a", ("5-thuc-nghiem.md", "truoc-5.5"), -1),
    ("05-4-1-bfs", "5.4-nhan-xet-bfs.md", 0),
    ("05-4-2-dfs", "5.4-nhan-xet-dfs.md", 0),
    ("05-4-3-ucs", "5.4-nhan-xet-ucs.md", 0),
    ("05-4-4-astar", "5.4-nhan-xet-astar.md", 0),
    ("05-thuc-nghiem-b", ("5-thuc-nghiem.md", "tu-5.5"), -1),
    ("06-ket-luan", "6-ket-luan.md", -1),
    ("90-tai-lieu", "tai-lieu-tham-khao.md", -1),
    ("A-ket-qua", "phu-luc-a-ket-qua.md", -1),
    ("B-ai", "phu-luc-b-ai.md", -1),
]
APPENDIX_FROM = "A-ket-qua"
LANDSCAPE = {"A-ket-qua"}

MAIN = r"""%!TEX program = xelatex
% File sinh bởi build.py. Sửa nội dung ở docs/report/*.md, thông tin bìa ở info.tex.
\documentclass[12pt,a4paper]{article}
\newcommand{\reportpdftitle}{CSC14003 Project 1 – Bloxorz Solver – Nhóm 9}
\newcommand{\reportpdfauthor}{Võ Quốc Trung, Bùi Quang Tiến, Nguyễn Bảo Trọng, Trịnh Vỹ Triết, Trần Nguyên Tân}
\newcommand{\headerleft}{Project 1 – Bloxorz Solver}
\newcommand{\headerright}{CSC14003 · Nhóm 9}
\input{preamble}
\graphicspath{{../}}   % hình nằm ở docs/report/hinh
\input{info}
\begin{document}
\input{cover}
\newpage
{\hypersetup{linkcolor=darkneutral}\tableofcontents}
%BODY%
\end{document}
"""


def find_pandoc() -> str:
    exe = os.environ.get("PANDOC") or shutil.which("pandoc")
    if exe:
        return exe
    try:
        import pypandoc  # type: ignore
        return pypandoc.get_pandoc_path()
    except Exception:
        sys.exit("Không tìm thấy pandoc. Cài pandoc 3.x hoặc chạy: pip install pypandoc_binary")


def find_xelatex() -> str:
    exe = os.environ.get("XELATEX") or shutil.which("xelatex")
    if exe:
        return exe
    for pattern in ("/mnt/c/Users/*/AppData/Local/Programs/MiKTeX/miktex/bin/x64/xelatex.exe",
                    "/mnt/c/Program Files/MiKTeX/miktex/bin/x64/xelatex.exe"):
        hits = sorted(glob.glob(pattern))
        if hits:
            return hits[0]
    sys.exit("Không tìm thấy XeLaTeX. Cài MiKTeX hoặc TeX Live, hoặc tải thư mục docs/report lên Overleaf "
             "(Compiler = XeLaTeX, Main document = latex/Report.tex).")


def read_part(spec) -> str:
    if isinstance(spec, str):
        return (MD / spec).read_text(encoding="utf-8")
    name, which = spec
    text = (MD / name).read_text(encoding="utf-8")
    cut = text.index("\n### 5.5.")
    return text[:cut] + "\n" if which == "truoc-5.5" else text[cut + 1:]


def to_latex(pandoc: str, md: str, shift: int, line: int = 72) -> str:
    cmd = [pandoc, "-f", "markdown-auto_identifiers-implicit_figures+pipe_tables+tex_math_dollars+lists_without_preceding_blankline",
           "-t", "latex", "--wrap=preserve", "--syntax-highlighting=none",
           f"--shift-heading-level-by={shift}", "--lua-filter", str(HERE / "filter.lua")]
    res = subprocess.run(cmd, input=md, capture_output=True, text=True, encoding="utf-8",
                         env={**os.environ, "TABLE_LINE": str(line)})
    if res.returncode != 0:
        sys.exit(res.stderr)
    if res.stderr.strip():
        print(res.stderr.strip(), file=sys.stderr)
    return res.stdout


def convert() -> None:
    pandoc = find_pandoc()
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.tex"):
        old.unlink()
    body = []
    for name, spec, shift in PARTS:
        tex = to_latex(pandoc, read_part(spec), shift, 118 if name in LANDSCAPE else 72)
        (OUT / f"{name}.tex").write_text(tex, encoding="utf-8")
        if name == APPENDIX_FROM:
            body.append("\\appendix")
        if name in LANDSCAPE:
            body.append(f"\\begin{{landscape}}\\renewcommand{{\\tablefont}}{{\\footnotesize}}"
                        f"\\input{{chapters/{name}}}\\end{{landscape}}")
        else:
            body.append(f"\\input{{chapters/{name}}}")
    (HERE / "Report.tex").write_text(MAIN.replace("%BODY%", "\n".join(body)), encoding="utf-8")


def compile_tex(passes: int = 3) -> None:
    xelatex = find_xelatex()
    for i in range(passes):
        res = subprocess.run([xelatex, "-interaction=nonstopmode", "-halt-on-error", "Report.tex"],
                             cwd=HERE, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if res.returncode != 0:
            log = (HERE / "Report.log").read_text(encoding="utf-8", errors="replace")
            m = [m.start() for m in re.finditer(r"^! ", log, re.M)]
            print(log[m[0]:m[0] + 1500] if m else res.stdout[-3000:])
            sys.exit(f"XeLaTeX lỗi ở lượt {i + 1}")
    log = (HERE / "Report.log").read_text(encoding="utf-8", errors="replace")
    missing = sorted(set(re.findall(r"Missing character: There is no (.) ", log)))
    overfull = len(re.findall(r"^Overfull \\hbox", log, re.M))
    pages = re.search(r"Output written on Report\.pdf \((\d+) pages", log)
    shutil.copyfile(HERE / "Report.pdf", MD / "Report.pdf")
    print(f"docs/report/Report.pdf: {pages.group(1) if pages else '?'} trang; overfull hbox: {overfull}; "
          f"thiếu ký tự: {''.join(missing) or 'không'}")


if __name__ == "__main__":
    if "--tex-only" not in sys.argv:
        convert()
    compile_tex()

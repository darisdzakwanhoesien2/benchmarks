from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVISION_ROOT = ROOT / "report_standardized" / "revision"
REVISION_CHAPTERS = REVISION_ROOT / "Chapters"


HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")
NUMBER_PREFIX_RE = re.compile(r"^\d+(?:\.\d+)*\s+")
TABLE_CAPTION_RE = re.compile(r"^Table\s+(\d+(?:\.\d+)?)\.\s+(.*)$")


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "table"


def strip_number_prefix(text: str) -> str:
    return NUMBER_PREFIX_RE.sub("", text).strip()


def rewrite_includegraphics_path(path: str) -> str:
    if path.startswith("results/"):
        return f"../../{path}"
    if path.startswith("report_standardized/"):
        return f"../{path.removeprefix('report_standardized/')}"
    return path


def rewrite_figure_block(block: str) -> str:
    def repl(match: re.Match[str]) -> str:
        prefix, img_path, suffix = match.groups()
        return f"{prefix}{rewrite_includegraphics_path(img_path)}{suffix}"

    pattern = re.compile(r"(\\includegraphics\*?\[.*?\]\{)([^}]+)(\})")
    return pattern.sub(repl, block)


def escape_latex_text(text: str) -> str:
    placeholders: dict[str, str] = {}

    def keep_code(match: re.Match[str]) -> str:
        key = f"@@CODE{len(placeholders)}@@"
        placeholders[key] = r"\texttt{" + escape_latex_text(match.group(1)) + "}"
        return key

    text = re.sub(r"`([^`]+)`", keep_code, text)

    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    for key, value in placeholders.items():
        text = text.replace(key, value)
    return text


def convert_heading(line: str) -> str | None:
    match = HEADING_RE.match(line)
    if not match:
        return None
    level = len(match.group(1))
    title = strip_number_prefix(match.group(2))
    if level == 1:
        return None
    if level == 2:
        return rf"\section{{{escape_latex_text(title)}}}"
    if level == 3:
        return rf"\subsection{{{escape_latex_text(title)}}}"
    if level == 4:
        return rf"\subsubsection{{{escape_latex_text(title)}}}"
    return rf"\paragraph{{{escape_latex_text(title)}}}"


def parse_markdown_table(lines: list[str], start: int) -> tuple[list[list[str]], int]:
    rows: list[list[str]] = []
    i = start
    while i < len(lines) and lines[i].lstrip().startswith("|"):
        raw = lines[i].strip().strip("|")
        cells = [cell.strip() for cell in raw.split("|")]
        rows.append(cells)
        i += 1
    return rows, i


def convert_table(rows: list[list[str]], pending_caption: tuple[str, str] | None) -> str:
    if len(rows) < 2:
        return "\n".join(escape_latex_text(" | ".join(row)) for row in rows)

    header = rows[0]
    body = [row for row in rows[2:] if any(cell.strip() for cell in row)]
    cols = len(header)
    colspec = "|" + "|".join("X" for _ in range(cols)) + "|"

    caption = "Converted markdown table"
    label = "tab:converted-markdown-table"
    if pending_caption:
        number, title = pending_caption
        caption = f"Table {number}. {title}"
        label = f"tab:{slugify(title)}"

    out = [
        r"\begin{table}[htbp]",
        r"\centering",
        rf"\caption{{{escape_latex_text(caption)}}}",
        rf"\label{{{label}}}",
        r"\footnotesize",
        r"\setlength{\tabcolsep}{4pt}",
        r"\renewcommand{\arraystretch}{1.15}",
        rf"\begin{{tabularx}}{{\linewidth}}{{{colspec}}}",
        r"\hline",
        " & ".join(rf"\textbf{{{escape_latex_text(cell)}}}" for cell in header) + r" \\ \hline",
    ]
    for row in body:
        padded = row + [""] * (cols - len(row))
        out.append(" & ".join(escape_latex_text(cell) for cell in padded[:cols]) + r" \\ \hline")
    out.extend([r"\end{tabularx}", r"\end{table}"])
    return "\n".join(out)


def convert_markdown(md_text: str) -> str:
    lines = md_text.splitlines()
    out: list[str] = []
    paragraph: list[str] = []
    pending_table_caption: tuple[str, str] | None = None
    i = 0

    def flush_paragraph() -> None:
        nonlocal paragraph, pending_table_caption
        if not paragraph:
            return
        text = " ".join(part.strip() for part in paragraph).strip()
        paragraph = []
        if not text:
            return
        match = TABLE_CAPTION_RE.match(text)
        if match:
            pending_table_caption = (match.group(1), match.group(2))
            return
        out.append(escape_latex_text(text))
        out.append("")

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith(r"\begin{figure}"):
            flush_paragraph()
            block_lines = [line]
            i += 1
            while i < len(lines):
                block_lines.append(lines[i])
                if lines[i].strip().startswith(r"\end{figure}"):
                    break
                i += 1
            out.append(rewrite_figure_block("\n".join(block_lines)))
            out.append("")
            i += 1
            continue

        if stripped.startswith("!["):
            i += 1
            continue

        if stripped.startswith("*Figure ") and stripped.endswith("*"):
            i += 1
            continue

        heading = convert_heading(line)
        if heading is not None:
            flush_paragraph()
            out.append(heading)
            out.append("")
            i += 1
            continue

        if stripped.startswith("|"):
            flush_paragraph()
            rows, i = parse_markdown_table(lines, i)
            out.append(convert_table(rows, pending_table_caption))
            out.append("")
            pending_table_caption = None
            continue

        if not stripped:
            flush_paragraph()
            i += 1
            continue

        paragraph.append(line)
        i += 1

    flush_paragraph()
    return "\n".join(out).rstrip() + "\n"


def convert_file(input_path: Path, output_path: Path) -> None:
    input_path = input_path.resolve()
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    converted = convert_markdown(input_path.read_text(encoding="utf-8"))
    header = [
        "% Auto-generated from converted markdown.",
        f"% Source: {input_path.relative_to(ROOT)}",
        "",
    ]
    output_path.write_text("\n".join(header) + converted, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert converted_markdown chapter files into revision LaTeX chapter files.")
    parser.add_argument(
        "--input",
        default=str(ROOT / "converted_markdown" / "discussion.md"),
        help="Input markdown file.",
    )
    parser.add_argument(
        "--output",
        default=str(REVISION_CHAPTERS / "discussion.tex"),
        help="Output LaTeX file.",
    )
    args = parser.parse_args()

    convert_file(Path(args.input), Path(args.output))
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()

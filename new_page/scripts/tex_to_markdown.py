#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


HEADING_COMMANDS = {
    "chapter": "#",
    "section": "##",
    "subsection": "###",
    "subsubsection": "####",
    "paragraph": "#####",
}


INLINE_COMMANDS = [
    (re.compile(r"\\textbf\{([^{}]*)\}"), r"**\1**"),
    (re.compile(r"\\emph\{([^{}]*)\}"), r"*\1*"),
    (re.compile(r"\\textit\{([^{}]*)\}"), r"*\1*"),
    (re.compile(r"\\underline\{([^{}]*)\}"), r"<u>\1</u>"),
    (re.compile(r"\\cite\{([^{}]*)\}"), r"[@\1]"),
    (re.compile(r"\\ref\{([^{}]*)\}"), r"`\1`"),
    (re.compile(r"\\label\{([^{}]*)\}"), r""),
    (re.compile(r"\\newline"), r"  \n"),
    (re.compile(r"\\%"), "%"),
    (re.compile(r"\\_"), "_"),
    (re.compile(r"\\&"), "&"),
    (re.compile(r"\\#"), "#"),
]


LIST_ENVIRONMENTS = {"itemize": "-", "enumerate": "1."}


def strip_comments(text: str) -> str:
    cleaned = []
    for line in text.splitlines():
        line = re.sub(r"(?<!\\)%.*$", "", line)
        cleaned.append(line.rstrip())
    return "\n".join(cleaned)


def replace_headings(text: str) -> str:
    for command, prefix in HEADING_COMMANDS.items():
        pattern = re.compile(rf"\\{command}\*?\{{([^{{}}]+)\}}")
        text = pattern.sub(lambda m: f"\n{prefix} {m.group(1).strip()}\n", text)
    return text


def replace_inline_commands(text: str) -> str:
    previous = None
    while previous != text:
        previous = text
        for pattern, replacement in INLINE_COMMANDS:
            text = pattern.sub(replacement, text)
    return text


def replace_special_blocks(text: str) -> str:
    text = re.sub(r"\\begin\{abstract\}", "\n## Abstract\n", text)
    text = re.sub(r"\\end\{abstract\}", "\n", text)
    text = re.sub(r"\\tableofcontents", "", text)
    text = re.sub(r"\\maketitle", "", text)
    return text


def convert_lists(text: str) -> str:
    lines = text.splitlines()
    output: list[str] = []
    stack: list[str] = []

    begin_pattern = re.compile(r"\\begin\{(itemize|enumerate)\}")
    end_pattern = re.compile(r"\\end\{(itemize|enumerate)\}")
    item_pattern = re.compile(r"\\item\s*(.*)")

    for raw_line in lines:
        line = raw_line.strip()
        begin_match = begin_pattern.fullmatch(line)
        end_match = end_pattern.fullmatch(line)
        item_match = item_pattern.fullmatch(line)

        if begin_match:
            stack.append(begin_match.group(1))
            continue
        if end_match:
            if stack:
                stack.pop()
            output.append("")
            continue
        if item_match and stack:
            marker = LIST_ENVIRONMENTS[stack[-1]]
            indent = "  " * (len(stack) - 1)
            content = item_match.group(1).strip()
            output.append(f"{indent}{marker} {content}".rstrip())
            continue

        output.append(raw_line)

    return "\n".join(output)


def convert_figures_and_tables(text: str) -> str:
    text = re.sub(r"\\begin\{figure\*?\}(\[[^\]]*\])?", "\n", text)
    text = re.sub(r"\\end\{figure\*?\}", "\n", text)
    text = re.sub(r"\\begin\{table\*?\}(\[[^\]]*\])?", "\n", text)
    text = re.sub(r"\\end\{table\*?\}", "\n", text)
    text = re.sub(r"\\caption\{([^{}]*)\}", r"\n*Caption: \1*\n", text)
    text = re.sub(r"\\includegraphics(?:\[[^\]]*\])?\{([^{}]+)\}", r"\n![\1](\1)\n", text)
    text = re.sub(r"\\centering", "", text)
    return text


def remove_remaining_commands(text: str) -> str:
    text = re.sub(r"\\begin\{[^{}]+\}", "", text)
    text = re.sub(r"\\end\{[^{}]+\}", "", text)
    text = re.sub(r"\\[a-zA-Z]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})?", "", text)
    text = text.replace("\\\\", "\n")
    return text


def normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"(?m)^\s*(\$\$|\{|\}|\[\]|\(\))\s*$", "", text)
    text = re.sub(r"(?m)^\s*[\{\}]+\s*$", "", text)
    text = re.sub(r"(?m)^\s*[+|&]\s*$", "", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    paragraphs = [part.strip() for part in text.split("\n\n")]
    return "\n\n".join(part for part in paragraphs if part).strip() + "\n"


def tex_to_markdown(text: str) -> str:
    text = strip_comments(text)
    text = replace_special_blocks(text)
    text = replace_headings(text)
    text = convert_figures_and_tables(text)
    text = convert_lists(text)
    text = replace_inline_commands(text)
    text = text.replace("~", " ")
    text = text.replace("``", '"').replace("''", '"')
    text = remove_remaining_commands(text)
    return normalize_whitespace(text)


def convert_file(input_path: Path, output_path: Path) -> None:
    markdown = tex_to_markdown(input_path.read_text(encoding="utf-8"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")


def convert_directory(input_dir: Path, output_dir: Path | None = None) -> list[Path]:
    tex_files = sorted(input_dir.rglob("*.tex"))
    if not tex_files:
        raise FileNotFoundError(f"No .tex files found in {input_dir}")

    written_files: list[Path] = []

    for tex_file in tex_files:
        if output_dir is None:
            md_path = tex_file.with_suffix(".md")
        else:
            relative_path = tex_file.relative_to(input_dir)
            md_path = output_dir / relative_path.with_suffix(".md")

        convert_file(tex_file, md_path)
        written_files.append(md_path)

    return written_files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert LaTeX .tex files into Markdown .md files."
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to a .tex file or a directory containing .tex files",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Optional output file or directory. For a directory input, this should be a directory.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    input_path = args.input
    if not input_path.exists():
        parser.error(f"input path not found: {input_path}")

    output_path = args.output

    if input_path.is_file():
        if input_path.suffix.lower() != ".tex":
            parser.error(f"input file must be a .tex file: {input_path}")
        final_output = output_path or input_path.with_suffix(".md")
        convert_file(input_path, final_output)
        print(final_output)
        return 0

    written_files = convert_directory(input_path, output_path)
    for path in written_files:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

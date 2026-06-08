#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


INLINE_COMMANDS = [
    (re.compile(r"\\textbf\{([^{}]*)\}"), r"**\1**"),
    (re.compile(r"\\emph\{([^{}]*)\}"), r"*\1*"),
    (re.compile(r"\\textit\{([^{}]*)\}"), r"*\1*"),
    (re.compile(r"\\underline\{([^{}]*)\}"), r"<u>\1</u>"),
    (re.compile(r"\\cite\{([^{}]*)\}"), r"[@\1]"),
    (re.compile(r"\\parencite\{([^{}]*)\}"), r"[@\1]"),
    (re.compile(r"\\textcite\{([^{}]*)\}"), r"[@\1]"),
    (re.compile(r"\\ref\{([^{}]*)\}"), r"`\1`"),
    (re.compile(r"\\autoref\{([^{}]*)\}"), r"`\1`"),
    (re.compile(r"\\label\{([^{}]*)\}"), r""),
    (re.compile(r"\\alt\{([^{}]*)\}"), r""),
    (re.compile(r"\\newline"), "  \n"),
    (re.compile(r"\\copyrightstring"), ""),
    (re.compile(r"\\spc"), " "),
    (re.compile(r"\\%"), "%"),
    (re.compile(r"\\_"), "_"),
    (re.compile(r"\\&"), "&"),
    (re.compile(r"\\#"), "#"),
]

LIST_ENVIRONMENTS = {"itemize": "-", "enumerate": "1."}


def extract_braced_content(text: str, start_index: int) -> tuple[str, int] | None:
    if start_index >= len(text) or text[start_index] != "{":
        return None

    depth = 0
    content: list[str] = []
    for index in range(start_index, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
            if depth > 1:
                content.append(char)
            continue
        if char == "}":
            depth -= 1
            if depth == 0:
                return "".join(content), index + 1
            content.append(char)
            continue
        if depth >= 1:
            content.append(char)
    return None


def extract_command_argument(text: str, command: str) -> str | None:
    marker = f"\\{command}"
    start = text.find(marker)
    if start == -1:
        return None

    brace_start = text.find("{", start)
    if brace_start == -1:
        return None

    extracted = extract_braced_content(text, brace_start)
    if extracted is None:
        return None

    content, _ = extracted
    return content


def strip_comments(text: str) -> str:
    cleaned = []
    for line in text.splitlines():
        line = re.sub(r"(?<!\\)%.*$", "", line)
        cleaned.append(line.rstrip())
    return "\n".join(cleaned)


def parse_main_tex(main_tex_path: Path) -> dict[str, tuple[int, str]]:
    if not main_tex_path.exists():
        return {}

    text = main_tex_path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"\\chapter\{([^{}]+)\}.*?\\input\{Chapters/([^{}]+)\}",
        re.DOTALL,
    )

    chapter_map: dict[str, tuple[int, str]] = {}
    for index, match in enumerate(pattern.finditer(text), start=1):
        chapter_title = match.group(1).strip()
        chapter_file = Path(match.group(2).strip()).stem
        chapter_map[chapter_file] = (index, chapter_title)

    return chapter_map


def infer_chapter_info(input_path: Path) -> tuple[int, str] | None:
    if input_path.parent.name != "Chapters":
        return None

    main_tex_path = input_path.parent.parent / "main.tex"
    chapter_map = parse_main_tex(main_tex_path)
    return chapter_map.get(input_path.stem)


def sanitize_text(text: str) -> str:
    text = re.sub(r"\\href\{[^{}]*\}\{([^{}]*)\}", r"\1", text)
    text = re.sub(r"\\copyrightstring", "", text)
    text = re.sub(r"\\\s*CC\s*BY\s*4\.0", "CC BY 4.0", text)
    text = re.sub(r"\bCC\s*BY\s*4\.0\b.*$", "CC BY 4.0", text)
    text = text.replace("\\", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip().rstrip(".")


def replace_special_blocks(text: str) -> str:
    text = re.sub(r"\\begin\{abstract\}", "\n## Abstract\n", text)
    text = re.sub(r"\\end\{abstract\}", "\n", text)
    text = re.sub(r"\\tableofcontents", "", text)
    text = re.sub(r"\\maketitle", "", text)
    text = re.sub(r"\\contents", "", text)
    text = re.sub(r"\\mainmatter", "", text)
    return text


def build_heading(command: str, title: str, counters: dict[str, int], chapter_number: int | None) -> str:
    title = title.strip()
    if chapter_number is None:
        prefix_map = {
            "section": "##",
            "subsection": "###",
            "subsubsection": "####",
            "paragraph": "#####",
        }
        return f"{prefix_map[command]} {title}"

    if command == "section":
        counters["section"] += 1
        counters["subsection"] = 0
        counters["subsubsection"] = 0
        counters["paragraph"] = 0
        return f"## {chapter_number}.{counters['section']} {title}"
    if command == "subsection":
        counters["subsection"] += 1
        counters["subsubsection"] = 0
        counters["paragraph"] = 0
        return f"### {chapter_number}.{counters['section']}.{counters['subsection']} {title}"
    if command == "subsubsection":
        counters["subsubsection"] += 1
        counters["paragraph"] = 0
        return (
            f"#### {chapter_number}.{counters['section']}.{counters['subsection']}."
            f"{counters['subsubsection']} {title}"
        )

    counters["paragraph"] += 1
    return (
        f"##### {chapter_number}.{counters['section']}.{counters['subsection']}."
        f"{counters['subsubsection']}.{counters['paragraph']} {title}"
    )


def replace_headings(
    text: str,
    chapter_number: int | None = None,
    chapter_title: str | None = None,
) -> str:
    pattern = re.compile(r"\\(section|subsection|subsubsection|paragraph)\*?\{([^{}]+)\}")
    counters = {"section": 0, "subsection": 0, "subsubsection": 0, "paragraph": 0}

    output: list[str] = []
    if chapter_number is not None and chapter_title:
        output.append(f"# Chapter {chapter_number} {chapter_title}\n")

    last_end = 0
    for match in pattern.finditer(text):
        output.append(text[last_end:match.start()])
        output.append("\n" + build_heading(match.group(1), match.group(2), counters, chapter_number) + "\n")
        last_end = match.end()

    output.append(text[last_end:])
    return "".join(output)


def replace_inline_commands(text: str) -> str:
    previous = None
    while previous != text:
        previous = text
        for pattern, replacement in INLINE_COMMANDS:
            text = pattern.sub(replacement, text)
    return text


def convert_lists(text: str) -> str:
    def replace_env(match: re.Match[str]) -> str:
        env_name = match.group(1)
        body = match.group(2).strip()
        parts = re.split(r"\\item(?:\s+)?", body)
        items = [part.strip() for part in parts if part.strip()]
        marker = LIST_ENVIRONMENTS[env_name]
        return "\n" + "\n".join(f"{marker} {item}" for item in items) + "\n"

    pattern = re.compile(r"\\begin\{(itemize|enumerate)\}(.*?)\\end\{\1\}", re.DOTALL)
    previous = None
    while previous != text:
        previous = text
        text = pattern.sub(replace_env, text)
    return text


def convert_figures_and_tables(text: str) -> str:
    def figure_to_markdown(match: re.Match[str]) -> str:
        body = match.group(1)
        image_match = re.search(r"\\includegraphics\*?(?:\[[^\]]*\])?\{([^{}]+)\}", body)
        caption = extract_command_argument(body, "caption")

        chunks: list[str] = []
        if image_match:
            image_path = image_match.group(1).strip()
            alt_text = sanitize_text(caption or image_path)
            chunks.append(f"![{alt_text}]({image_path})")
        if caption:
            chunks.append(f"*Figure: {sanitize_text(caption)}*")
        return "\n" + "\n\n".join(chunks) + "\n" if chunks else "\n"

    def table_to_markdown(match: re.Match[str]) -> str:
        body = match.group(1)
        caption = extract_command_argument(body, "caption")
        if caption:
            return f"\n*Table: {sanitize_text(caption)}*\n"
        return "\n"

    text = re.sub(r"\\begin\{figure\*?\}(.*?)\\end\{figure\*?\}", figure_to_markdown, text, flags=re.DOTALL)
    text = re.sub(r"\\begin\{table\*?\}(.*?)\\end\{table\*?\}", table_to_markdown, text, flags=re.DOTALL)
    text = re.sub(r"\\begin\{center\}|\s*\\end\{center\}", "\n", text)
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
    text = re.sub(r"(?m)^\s*\\\s*$", "", text)
    text = re.sub(r"(?m)^\s*\[[^\]]*\]\s*$", "", text)
    text = re.sub(r"(?m)^\s*\{[^{}]*\\[^{}]*\}\s*$", "", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    paragraphs = [part.strip() for part in text.split("\n\n")]
    return "\n\n".join(part for part in paragraphs if part).strip() + "\n"


def tex_to_markdown(
    text: str,
    chapter_number: int | None = None,
    chapter_title: str | None = None,
) -> str:
    text = strip_comments(text)
    text = replace_special_blocks(text)
    text = convert_figures_and_tables(text)
    text = convert_lists(text)
    text = replace_headings(text, chapter_number=chapter_number, chapter_title=chapter_title)
    text = replace_inline_commands(text)
    text = text.replace("~", " ")
    text = text.replace("``", '"').replace("''", '"')
    text = remove_remaining_commands(text)
    return normalize_whitespace(text)


def convert_file(input_path: Path, output_path: Path) -> None:
    chapter_info = infer_chapter_info(input_path)
    markdown = tex_to_markdown(
        input_path.read_text(encoding="utf-8"),
        chapter_number=chapter_info[0] if chapter_info else None,
        chapter_title=chapter_info[1] if chapter_info else None,
    )
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

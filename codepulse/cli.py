"""CLI entry point for CodePulse."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console

from .analyzer import analyze
from .display import display_results

console = Console()


@click.command()
@click.argument("path", default=".", type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option("--max-file-size", "-m", default=1_000_000, help="Skip files larger than this (bytes).")
@click.option("--json", "output_json", is_flag=True, help="Output results as JSON.")
@click.version_option(package_name="codepulse")
def main(path: str, max_file_size: int, output_json: bool) -> None:
    """Analyze a codebase and display beautiful stats in your terminal.

    PATH is the directory to analyze (defaults to current directory).
    """
    target = Path(path)

    with console.status("[bold cyan]Scanning codebase...", spinner="dots"):
        result = analyze(target, max_file_size=max_file_size)

    if output_json:
        import json

        data = {
            "root": str(result.root),
            "total_files": result.total_files,
            "total_lines": result.total_lines,
            "total_code_lines": result.total_code_lines,
            "total_blank_lines": result.total_blank_lines,
            "total_comment_lines": result.total_comment_lines,
            "total_size_bytes": result.total_size_bytes,
            "languages": {
                name: {
                    "files": s.files,
                    "code_lines": s.code_lines,
                    "comment_lines": s.comment_lines,
                    "blank_lines": s.blank_lines,
                    "total_lines": s.lines,
                    "size_bytes": s.size_bytes,
                }
                for name, s in sorted(
                    result.languages.items(),
                    key=lambda x: x[1].code_lines,
                    reverse=True,
                )
            },
            "largest_files": [
                {
                    "path": str(f.path),
                    "language": f.language,
                    "lines": f.lines,
                    "code_lines": f.code_lines,
                    "size_bytes": f.size_bytes,
                }
                for f in result.largest_files[:10]
            ],
        }
        console.print_json(json.dumps(data))
    else:
        display_results(result)


if __name__ == "__main__":
    main()

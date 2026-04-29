"""Rich-based terminal display for analysis results."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns

from .analyzer import AnalysisResult

console = Console()

LANG_COLORS: dict[str, str] = {
    "Python": "yellow",
    "JavaScript": "bright_yellow",
    "TypeScript": "blue",
    "Java": "red",
    "C": "cyan",
    "C++": "cyan",
    "C#": "green",
    "Go": "bright_cyan",
    "Rust": "bright_red",
    "Ruby": "red",
    "PHP": "magenta",
    "Swift": "bright_red",
    "Kotlin": "bright_magenta",
    "Shell": "green",
    "HTML": "bright_red",
    "CSS": "bright_blue",
    "SCSS": "bright_magenta",
    "SQL": "bright_yellow",
    "Markdown": "white",
    "JSON": "bright_green",
    "YAML": "bright_green",
    "TOML": "bright_green",
    "Dart": "bright_cyan",
    "Vue": "green",
    "Svelte": "bright_red",
    "Dockerfile": "bright_blue",
    "Other": "dim",
}


def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def _make_bar(fraction: float, width: int = 30) -> Text:
    filled = int(fraction * width)
    bar = Text()
    bar.append("█" * filled, style="bright_cyan")
    bar.append("░" * (width - filled), style="dim")
    return bar


def display_results(result: AnalysisResult) -> None:
    """Print analysis results to the terminal."""
    console.print()

    # Header
    header = Text()
    header.append("  CODEPULSE  ", style="bold white on blue")
    header.append(f"  {result.root.name}", style="bold bright_white")
    console.print(Panel(header, border_style="blue", padding=(0, 1)))
    console.print()

    # Summary stats
    summary_table = Table(show_header=False, box=None, padding=(0, 3))
    summary_table.add_column(style="bold bright_cyan")
    summary_table.add_column(style="bold white")
    summary_table.add_column(style="bold bright_cyan")
    summary_table.add_column(style="bold white")

    summary_table.add_row(
        "Files", f"{result.total_files:,}",
        "Total Lines", f"{result.total_lines:,}",
    )
    summary_table.add_row(
        "Code Lines", f"{result.total_code_lines:,}",
        "Blank Lines", f"{result.total_blank_lines:,}",
    )
    summary_table.add_row(
        "Comments", f"{result.total_comment_lines:,}",
        "Total Size", _format_size(result.total_size_bytes),
    )
    summary_table.add_row(
        "Languages", f"{len(result.languages):,}",
        "Skipped", f"{result.skipped_files + result.skipped_binary:,}",
    )

    console.print(Panel(summary_table, title="[bold]Summary[/bold]", border_style="bright_cyan", padding=(1, 2)))
    console.print()

    # Language breakdown
    lang_table = Table(title="Language Breakdown", border_style="blue", header_style="bold bright_white")
    lang_table.add_column("Language", style="bold")
    lang_table.add_column("Files", justify="right")
    lang_table.add_column("Code Lines", justify="right")
    lang_table.add_column("Comments", justify="right")
    lang_table.add_column("Blanks", justify="right")
    lang_table.add_column("Total Lines", justify="right")
    lang_table.add_column("Share", justify="right")
    lang_table.add_column("Bar")

    sorted_langs = sorted(
        result.languages.values(),
        key=lambda s: s.code_lines,
        reverse=True,
    )

    for stats in sorted_langs:
        color = LANG_COLORS.get(stats.name, "white")
        share = stats.code_lines / max(result.total_code_lines, 1)
        lang_table.add_row(
            Text(stats.name, style=f"bold {color}"),
            f"{stats.files:,}",
            f"{stats.code_lines:,}",
            f"{stats.comment_lines:,}",
            f"{stats.blank_lines:,}",
            f"{stats.lines:,}",
            f"{share:.1%}",
            _make_bar(share, 20),
        )

    console.print(lang_table)
    console.print()

    # Largest files
    if result.largest_files:
        files_table = Table(title="Largest Files (by lines)", border_style="yellow", header_style="bold bright_white")
        files_table.add_column("File", style="bright_white")
        files_table.add_column("Language")
        files_table.add_column("Lines", justify="right", style="bold")
        files_table.add_column("Code", justify="right")
        files_table.add_column("Size", justify="right")

        for fi in result.largest_files[:10]:
            color = LANG_COLORS.get(fi.language, "white")
            files_table.add_row(
                str(fi.path),
                Text(fi.language, style=color),
                f"{fi.lines:,}",
                f"{fi.code_lines:,}",
                _format_size(fi.size_bytes),
            )

        console.print(files_table)
        console.print()

    # Directory breakdown
    if result.directory_sizes:
        dir_table = Table(title="Top Directories (by lines)", border_style="green", header_style="bold bright_white")
        dir_table.add_column("Directory", style="bold bright_green")
        dir_table.add_column("Lines", justify="right", style="bold")
        dir_table.add_column("Share")

        for dirname, lines in list(result.directory_sizes.items())[:10]:
            share = lines / max(result.total_lines, 1)
            dir_table.add_row(dirname, f"{lines:,}", _make_bar(share, 25))

        console.print(dir_table)
        console.print()

    # Code vs comments ratio
    if result.total_code_lines > 0:
        ratio = result.total_comment_lines / result.total_code_lines
        code_pct = result.total_code_lines / max(result.total_lines, 1)
        comment_pct = result.total_comment_lines / max(result.total_lines, 1)
        blank_pct = result.total_blank_lines / max(result.total_lines, 1)

        composition = Text()
        composition.append(f"  Code: {code_pct:.1%}  ", style="bold bright_cyan")
        composition.append(f"  Comments: {comment_pct:.1%}  ", style="bold bright_green")
        composition.append(f"  Blanks: {blank_pct:.1%}  ", style="bold dim")
        composition.append(f"  Comment/Code Ratio: {ratio:.2f}  ", style="bold bright_yellow")

        console.print(Panel(composition, title="[bold]Composition[/bold]", border_style="bright_magenta"))
        console.print()

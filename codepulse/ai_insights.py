"""AI-powered codebase insights and recommendations."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from .analyzer import AnalysisResult
from .ai_client import query_ai, get_provider_name

console = Console()

SYSTEM_PROMPT = """\
You are CodePulse AI, an expert code analyst. You analyze codebase statistics and provide actionable insights.
Be concise, specific, and practical. Use markdown formatting with headers and bullet points.
Focus on: code quality indicators, architecture observations, potential improvements, and best practices."""


def _build_summary(result: AnalysisResult, sample_files: list[tuple[str, str]]) -> str:
    """Build a text summary of the analysis for the AI."""
    lang_breakdown = "\n".join(
        f"  - {s.name}: {s.files} files, {s.code_lines} code lines, {s.comment_lines} comments"
        for s in sorted(result.languages.values(), key=lambda s: s.code_lines, reverse=True)
    )

    largest = "\n".join(
        f"  - {f.path} ({f.language}): {f.lines} lines"
        for f in result.largest_files[:10]
    )

    dirs = "\n".join(
        f"  - {d}: {lines} lines"
        for d, lines in list(result.directory_sizes.items())[:10]
    )

    comment_ratio = result.total_comment_lines / max(result.total_code_lines, 1)

    summary = f"""## Codebase Analysis for: {result.root.name}

**Overview:**
- Total files: {result.total_files}
- Total lines: {result.total_lines:,} (Code: {result.total_code_lines:,}, Comments: {result.total_comment_lines:,}, Blank: {result.total_blank_lines:,})
- Comment-to-code ratio: {comment_ratio:.2f}
- Languages detected: {len(result.languages)}
- Total size: {result.total_size_bytes / 1024:.1f} KB

**Language Breakdown:**
{lang_breakdown}

**Largest Files:**
{largest}

**Top Directories:**
{dirs}
"""

    if sample_files:
        summary += "\n**Sample Code Snippets:**\n"
        for path, content in sample_files:
            summary += f"\n--- {path} ---\n```\n{content}\n```\n"

    return summary


def _read_sample_files(result: AnalysisResult, max_files: int = 5, max_lines: int = 50) -> list[tuple[str, str]]:
    """Read a sample of code files for AI analysis."""
    samples: list[tuple[str, str]] = []
    code_langs = {"Python", "JavaScript", "TypeScript", "Java", "Go", "Rust", "C", "C++"}

    candidates = [
        f for f in result.files
        if f.language in code_langs and 10 < f.lines < 500
    ]
    candidates.sort(key=lambda f: f.lines, reverse=True)

    for fi in candidates[:max_files]:
        filepath = result.root / fi.path
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()[:max_lines]
                content = "".join(lines)
                if len(lines) == max_lines:
                    content += f"\n... ({fi.lines - max_lines} more lines)"
                samples.append((str(fi.path), content))
        except OSError:
            continue

    return samples


def generate_insights(result: AnalysisResult) -> None:
    """Generate AI-powered insights for the codebase analysis."""
    provider = get_provider_name()
    if provider == "none":
        console.print("[red]No AI API key found.[/red]")
        console.print("Set one of: [bold]OPENAI_API_KEY[/bold], [bold]GEMINI_API_KEY[/bold], or [bold]NVIDIA_API_KEY[/bold]")
        return

    header = Text()
    header.append("  AI INSIGHTS  ", style="bold white on bright_magenta")
    header.append(f"  powered by {provider}", style="bold bright_white")
    console.print(Panel(header, border_style="bright_magenta", padding=(0, 1)))
    console.print()

    with console.status(f"[bold magenta]Analyzing with {provider}...", spinner="dots"):
        samples = _read_sample_files(result)
        summary = _build_summary(result, samples)

        prompt = f"""{summary}

Based on this analysis, provide:
1. **Code Health Score** (1-10) with brief justification
2. **Architecture Assessment** - what the project structure tells you
3. **Top 5 Improvement Suggestions** - specific, actionable items
4. **Code Quality Observations** - patterns, anti-patterns, comment quality
5. **Dependency & Complexity Risks** - based on file sizes and structure

Keep it concise and actionable."""

        response = query_ai(prompt, system_prompt=SYSTEM_PROMPT)

    console.print(Markdown(response))
    console.print()

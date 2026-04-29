"""CLI entry point for CodePulse."""

from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console

from .analyzer import analyze
from .display import display_results

console = Console()


@click.group(invoke_without_command=True)
@click.argument("path", default=".", type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option("--max-file-size", "-m", default=1_000_000, help="Skip files larger than this (bytes).")
@click.option("--json", "output_json", is_flag=True, help="Output results as JSON.")
@click.option("--ai", "use_ai", is_flag=True, help="Include AI-powered insights (requires API key).")
@click.version_option(package_name="codepulse")
@click.pass_context
def main(ctx: click.Context, path: str, max_file_size: int, output_json: bool, use_ai: bool) -> None:
    """Analyze a codebase and display beautiful stats in your terminal.

    PATH is the directory to analyze (defaults to current directory).
    """
    target = Path(path)

    with console.status("[bold cyan]Scanning codebase...", spinner="dots"):
        result = analyze(target, max_file_size=max_file_size)

    ctx.ensure_object(dict)
    ctx.obj["result"] = result

    if ctx.invoked_subcommand is not None:
        return

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

    if use_ai:
        from .ai_insights import generate_insights
        generate_insights(result)


@main.command()
@click.pass_context
def ai(ctx: click.Context) -> None:
    """Generate AI-powered insights about the codebase.

    Requires one of: OPENAI_API_KEY, GEMINI_API_KEY, or NVIDIA_API_KEY.
    """
    result = ctx.obj.get("result")
    if result is None:
        console.print("[red]Error: Run analysis first.[/red]")
        return

    from .ai_insights import generate_insights
    display_results(result)
    generate_insights(result)


@main.command()
@click.argument("file_path", type=click.Path(exists=True, dir_okay=False, resolve_path=True))
@click.pass_context
def review(ctx: click.Context, file_path: str) -> None:
    """AI-powered code review for a specific file.

    Requires one of: OPENAI_API_KEY, GEMINI_API_KEY, or NVIDIA_API_KEY.
    """
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.text import Text
    from .ai_client import query_ai, get_provider_name

    provider = get_provider_name()
    if provider == "none":
        console.print("[red]No AI API key found.[/red]")
        console.print("Set one of: [bold]OPENAI_API_KEY[/bold], [bold]GEMINI_API_KEY[/bold], or [bold]NVIDIA_API_KEY[/bold]")
        return

    target = Path(file_path)
    try:
        code = target.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        console.print(f"[red]Error reading file:[/red] {e}")
        return

    if len(code) > 15000:
        code = code[:15000] + "\n... (truncated)"

    header = Text()
    header.append("  CODE REVIEW  ", style="bold white on bright_magenta")
    header.append(f"  {target.name}  |  {provider}", style="bold bright_white")
    console.print(Panel(header, border_style="bright_magenta", padding=(0, 1)))
    console.print()

    with console.status(f"[bold magenta]Reviewing with {provider}...", spinner="dots"):
        prompt = f"""Review this code file ({target.name}) and provide:

1. **Overall Quality** (1-10)
2. **Strengths** - what's done well
3. **Issues Found** - bugs, security concerns, anti-patterns
4. **Improvement Suggestions** - specific refactoring recommendations
5. **Performance Notes** - any performance concerns

```{target.suffix.lstrip('.')}
{code}
```

Be concise, specific, and actionable."""

        system = "You are an expert code reviewer. Provide thorough but concise reviews with specific line references when possible. Use markdown formatting."
        response = query_ai(prompt, system_prompt=system)

    console.print(Markdown(response))
    console.print()


if __name__ == "__main__":
    main()

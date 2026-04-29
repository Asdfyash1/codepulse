# CodePulse

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![AI Powered](https://img.shields.io/badge/AI-Powered-blueviolet.svg)](#ai-powered-features)

**A beautiful CLI tool that analyzes codebases and visualizes stats right in your terminal — with optional AI-powered insights.**

CodePulse scans any project directory and gives you instant insights: language breakdown, lines of code, comment ratios, largest files, directory sizes — all rendered with beautiful Rich-powered terminal graphics. Plug in an AI API key to get intelligent code review and architecture recommendations.

## Features

- **Language Detection** — Automatically detects 40+ programming languages
- **Line Counting** — Separates code, comments, and blank lines
- **Visual Bar Charts** — See language distribution at a glance
- **Largest Files** — Quickly find the biggest files in your codebase
- **Directory Breakdown** — Understand which folders contain the most code
- **Composition Analysis** — Code-to-comment ratio and composition metrics
- **JSON Export** — Machine-readable output for CI/CD integration
- **Smart Filtering** — Respects `.gitignore` and skips binary/generated files
- **Fast** — Scans large codebases in seconds

### AI-Powered Features

- **AI Insights** — Get a health score, architecture assessment, and improvement suggestions powered by LLMs
- **AI Code Review** — Review any file with AI for bugs, anti-patterns, and optimization opportunities
- **Multi-Provider** — Works with OpenAI, Google Gemini, and NVIDIA APIs

## Installation

```bash
git clone https://github.com/Asdfyash1/codepulse.git
cd codepulse
pip install -e .
```

## Quick Start

Analyze the current directory:

```bash
codepulse .
```

Analyze with AI insights:

```bash
export OPENAI_API_KEY="your-key"   # or GEMINI_API_KEY or NVIDIA_API_KEY
codepulse . --ai
```

AI code review for a specific file:

```bash
codepulse . review path/to/file.py
```

Export as JSON:

```bash
codepulse . --json
```

## AI Setup

Set one of these environment variables to enable AI features:

| Provider | Environment Variable | Default Model |
|----------|---------------------|---------------|
| OpenAI | `OPENAI_API_KEY` | `gpt-4o-mini` |
| Google Gemini | `GEMINI_API_KEY` | `gemini-2.0-flash` |
| NVIDIA | `NVIDIA_API_KEY` | `meta/llama-3.1-8b-instruct` |

Override the model with: `OPENAI_MODEL`, `GEMINI_MODEL`, or `NVIDIA_MODEL`.

## Commands

| Command | Description |
|---------|-------------|
| `codepulse .` | Analyze codebase and show stats |
| `codepulse . --ai` | Analyze + AI insights |
| `codepulse . --json` | Output as JSON |
| `codepulse . ai` | AI insights only |
| `codepulse . review FILE` | AI code review for a file |

## Example Output

```
╭──────────────────────────────────────────╮
│   CODEPULSE   my-project                 │
╰──────────────────────────────────────────╯

╭─────────────── Summary ────────────────╮
│  Files        42    Total Lines  3,891  │
│  Code Lines   2,847  Blank Lines  612   │
│  Comments     432    Total Size   128KB │
│  Languages    5      Skipped      12    │
╰────────────────────────────────────────╯

╭────────────────────────────────────────╮
│   AI INSIGHTS   powered by OpenAI      │
╰────────────────────────────────────────╯

Code Health Score: 7/10
...
```

## Supported Languages

Python, JavaScript, TypeScript, Java, C, C++, C#, Go, Rust, Ruby, PHP, Swift, Kotlin, Scala, R, Shell, PowerShell, Lua, Perl, HTML, CSS, SCSS, SQL, Markdown, JSON, YAML, TOML, XML, Dockerfile, Makefile, Dart, Elixir, Haskell, Vue, Svelte, Astro, Zig, Nim, Julia, and more.

## Development

```bash
git clone https://github.com/Asdfyash1/codepulse.git
cd codepulse
python -m venv .venv
source .venv/bin/activate
pip install -e .
pytest tests/ -v
```

## License

MIT License — see [LICENSE](LICENSE) for details.

## Author

**Yashwanth** — [GitHub](https://github.com/Asdfyash1)

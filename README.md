# CodePulse

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**A beautiful CLI tool that analyzes codebases and visualizes stats right in your terminal.**

CodePulse scans any project directory and gives you instant insights: language breakdown, lines of code, comment ratios, largest files, directory sizes — all rendered with beautiful Rich-powered terminal graphics.

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

## Installation

```bash
pip install -e .
```

Or install directly from the repo:

```bash
git clone https://github.com/Asdfyash1/codepulse.git
cd codepulse
pip install -e .
```

## Usage

Analyze the current directory:

```bash
codepulse
```

Analyze a specific project:

```bash
codepulse /path/to/your/project
```

Export as JSON:

```bash
codepulse --json /path/to/project
```

### Options

| Flag | Description |
|------|-------------|
| `--json` | Output results as JSON |
| `-m, --max-file-size` | Skip files larger than N bytes (default: 1MB) |
| `--version` | Show version |
| `--help` | Show help message |

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

         Language Breakdown
┌────────────┬───────┬──────────┬─────┐
│ Language   │ Files │ Code     │ Bar │
├────────────┼───────┼──────────┼─────┤
│ Python     │ 18    │ 1,423    │ ███ │
│ TypeScript │ 12    │ 892      │ ██  │
│ CSS        │ 5     │ 312      │ █   │
│ JSON       │ 4     │ 142      │ ▌   │
│ Markdown   │ 3     │ 78       │ ▏   │
└────────────┴───────┴──────────┴─────┘
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
```

Run on itself:

```bash
codepulse .
```

## License

MIT License — see [LICENSE](LICENSE) for details.

## Author

**Yashwanth** — [GitHub](https://github.com/Asdfyash1)

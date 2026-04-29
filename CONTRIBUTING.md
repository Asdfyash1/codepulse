# Contributing to CodePulse

Thanks for your interest in contributing! Here's how to get started.

## Setup

```bash
git clone https://github.com/Asdfyash1/codepulse.git
cd codepulse
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install pytest
```

## Running Tests

```bash
pytest tests/ -v
```

## How to Contribute

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Run tests to make sure everything passes
5. Commit: `git commit -m "Add my feature"`
6. Push: `git push origin feature/my-feature`
7. Open a Pull Request

## Ideas for Contributions

- Add support for more programming languages
- Improve comment detection (multi-line comments)
- Add complexity metrics (cyclomatic complexity)
- Add git history analysis (commit frequency, churn)
- Terminal recording/screenshot export
- Add more AI provider integrations
- Performance optimizations for very large codebases

## Code Style

- Follow PEP 8
- Use type hints
- Keep functions focused and small
- Add docstrings to public functions

## Reporting Bugs

Open an issue with:
- What you expected to happen
- What actually happened
- Steps to reproduce
- Python version and OS

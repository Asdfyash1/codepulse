"""Core codebase analysis engine."""

from __future__ import annotations

import os
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import pathspec


LANGUAGE_EXTENSIONS: dict[str, list[str]] = {
    "Python": [".py", ".pyw", ".pyi"],
    "JavaScript": [".js", ".mjs", ".cjs"],
    "TypeScript": [".ts", ".tsx"],
    "Java": [".java"],
    "C": [".c", ".h"],
    "C++": [".cpp", ".hpp", ".cc", ".hh", ".cxx", ".hxx"],
    "C#": [".cs"],
    "Go": [".go"],
    "Rust": [".rs"],
    "Ruby": [".rb"],
    "PHP": [".php"],
    "Swift": [".swift"],
    "Kotlin": [".kt", ".kts"],
    "Scala": [".scala"],
    "R": [".r", ".R"],
    "Shell": [".sh", ".bash", ".zsh", ".fish"],
    "PowerShell": [".ps1", ".psm1"],
    "Lua": [".lua"],
    "Perl": [".pl", ".pm"],
    "HTML": [".html", ".htm"],
    "CSS": [".css"],
    "SCSS": [".scss", ".sass"],
    "SQL": [".sql"],
    "Markdown": [".md", ".markdown"],
    "JSON": [".json"],
    "YAML": [".yml", ".yaml"],
    "TOML": [".toml"],
    "XML": [".xml"],
    "Dockerfile": ["Dockerfile"],
    "Makefile": ["Makefile"],
    "Dart": [".dart"],
    "Elixir": [".ex", ".exs"],
    "Haskell": [".hs"],
    "Vue": [".vue"],
    "Svelte": [".svelte"],
    "Astro": [".astro"],
    "Zig": [".zig"],
    "Nim": [".nim"],
    "Julia": [".jl"],
}

EXTENSION_TO_LANG: dict[str, str] = {}
for lang, exts in LANGUAGE_EXTENSIONS.items():
    for ext in exts:
        EXTENSION_TO_LANG[ext] = lang

BINARY_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg", ".webp",
    ".mp3", ".mp4", ".wav", ".avi", ".mov", ".mkv", ".flac",
    ".zip", ".tar", ".gz", ".bz2", ".xz", ".7z", ".rar",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".exe", ".dll", ".so", ".dylib", ".o", ".a",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    ".pyc", ".pyo", ".class", ".jar",
    ".db", ".sqlite", ".sqlite3",
    ".lock",
}


@dataclass
class FileInfo:
    path: Path
    language: str
    lines: int
    code_lines: int
    blank_lines: int
    comment_lines: int
    size_bytes: int


@dataclass
class LanguageStats:
    name: str
    files: int = 0
    lines: int = 0
    code_lines: int = 0
    blank_lines: int = 0
    comment_lines: int = 0
    size_bytes: int = 0


@dataclass
class AnalysisResult:
    root: Path
    total_files: int = 0
    total_lines: int = 0
    total_code_lines: int = 0
    total_blank_lines: int = 0
    total_comment_lines: int = 0
    total_size_bytes: int = 0
    languages: dict[str, LanguageStats] = field(default_factory=dict)
    files: list[FileInfo] = field(default_factory=list)
    largest_files: list[FileInfo] = field(default_factory=list)
    directory_sizes: dict[str, int] = field(default_factory=dict)
    skipped_files: int = 0
    skipped_binary: int = 0


COMMENT_MARKERS: dict[str, tuple[str, ...]] = {
    "Python": ("#",),
    "Ruby": ("#",),
    "Shell": ("#",),
    "R": ("#",),
    "Perl": ("#",),
    "YAML": ("#",),
    "TOML": ("#",),
    "JavaScript": ("//",),
    "TypeScript": ("//",),
    "Java": ("//",),
    "C": ("//",),
    "C++": ("//",),
    "C#": ("//",),
    "Go": ("//",),
    "Rust": ("//",),
    "Swift": ("//",),
    "Kotlin": ("//",),
    "Scala": ("//",),
    "Dart": ("//",),
    "Zig": ("//",),
    "PHP": ("//", "#"),
    "Lua": ("--",),
    "Haskell": ("--",),
    "SQL": ("--",),
    "HTML": ("<!--",),
    "CSS": ("/*",),
    "SCSS": ("//", "/*"),
}


def _count_lines(filepath: Path, language: str) -> tuple[int, int, int, int]:
    """Count total, code, blank, and comment lines."""
    total = code = blank = comment = 0
    markers = COMMENT_MARKERS.get(language, ())
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                total += 1
                stripped = line.strip()
                if not stripped:
                    blank += 1
                elif any(stripped.startswith(m) for m in markers):
                    comment += 1
                else:
                    code += 1
    except (OSError, UnicodeDecodeError):
        pass
    return total, code, blank, comment


def _load_gitignore(root: Path) -> Optional[pathspec.PathSpec]:
    gitignore = root / ".gitignore"
    if gitignore.exists():
        try:
            with open(gitignore, "r") as f:
                return pathspec.PathSpec.from_lines("gitwildmatch", f)
        except OSError:
            pass
    return None


DEFAULT_IGNORE = pathspec.PathSpec.from_lines(
    "gitignore",
    [
        ".git/",
        "node_modules/",
        "__pycache__/",
        ".venv/",
        "venv/",
        ".tox/",
        ".mypy_cache/",
        ".pytest_cache/",
        "dist/",
        "build/",
        ".next/",
        ".nuxt/",
        "target/",
        "*.egg-info/",
        ".eggs/",
        "vendor/",
        "coverage/",
        ".coverage",
        "htmlcov/",
    ],
)


def analyze(root: Path, max_file_size: int = 1_000_000) -> AnalysisResult:
    """Analyze a codebase directory and return statistics."""
    root = root.resolve()
    result = AnalysisResult(root=root)
    gitignore_spec = _load_gitignore(root)
    lang_stats: dict[str, LanguageStats] = defaultdict(lambda: LanguageStats(name=""))
    dir_sizes: dict[str, int] = defaultdict(int)

    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir == ".":
            rel_dir = ""

        # Filter ignored directories
        filtered_dirs = []
        for d in dirnames:
            check_path = os.path.join(rel_dir, d, "") if rel_dir else d + "/"
            if DEFAULT_IGNORE.match_file(check_path):
                continue
            if gitignore_spec and gitignore_spec.match_file(check_path):
                continue
            filtered_dirs.append(d)
        dirnames[:] = filtered_dirs

        for filename in filenames:
            filepath = Path(dirpath) / filename
            rel_path = filepath.relative_to(root)
            rel_str = str(rel_path)

            if DEFAULT_IGNORE.match_file(rel_str):
                result.skipped_files += 1
                continue
            if gitignore_spec and gitignore_spec.match_file(rel_str):
                result.skipped_files += 1
                continue

            ext = filepath.suffix.lower()
            if ext in BINARY_EXTENSIONS:
                result.skipped_binary += 1
                continue

            # Detect language
            language = EXTENSION_TO_LANG.get(ext)
            if not language:
                if filename in EXTENSION_TO_LANG:
                    language = EXTENSION_TO_LANG[filename]
                else:
                    language = "Other"

            try:
                size = filepath.stat().st_size
            except OSError:
                continue

            if size > max_file_size:
                result.skipped_files += 1
                continue

            total, code, blank, comment = _count_lines(filepath, language)
            file_info = FileInfo(
                path=rel_path,
                language=language,
                lines=total,
                code_lines=code,
                blank_lines=blank,
                comment_lines=comment,
                size_bytes=size,
            )
            result.files.append(file_info)
            result.total_files += 1
            result.total_lines += total
            result.total_code_lines += code
            result.total_blank_lines += blank
            result.total_comment_lines += comment
            result.total_size_bytes += size

            stats = lang_stats[language]
            stats.name = language
            stats.files += 1
            stats.lines += total
            stats.code_lines += code
            stats.blank_lines += blank
            stats.comment_lines += comment
            stats.size_bytes += size

            top_dir = str(rel_path).split(os.sep)[0] if os.sep in str(rel_path) else "."
            dir_sizes[top_dir] += total

    result.languages = dict(lang_stats)
    result.largest_files = sorted(result.files, key=lambda f: f.lines, reverse=True)[:15]
    result.directory_sizes = dict(sorted(dir_sizes.items(), key=lambda x: x[1], reverse=True)[:20])
    return result

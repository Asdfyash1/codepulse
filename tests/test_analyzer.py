"""Tests for the CodePulse analyzer."""

import tempfile
from pathlib import Path

from codepulse.analyzer import analyze


def _create_project(tmp: Path) -> None:
    (tmp / "main.py").write_text("# hello\nimport os\nprint('hi')\n")
    (tmp / "utils.py").write_text("def add(a, b):\n    return a + b\n")
    (tmp / "style.css").write_text("body {\n  margin: 0;\n}\n")
    (tmp / "README.md").write_text("# Project\n\nDescription.\n")
    (tmp / "data.json").write_text('{"key": "value"}\n')
    sub = tmp / "src"
    sub.mkdir()
    (sub / "app.py").write_text("# app\nclass App:\n    pass\n")


def test_basic_analysis():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _create_project(root)
        result = analyze(root)

        assert result.total_files == 6
        assert result.total_lines > 0
        assert result.total_code_lines > 0
        assert "Python" in result.languages
        assert result.languages["Python"].files == 3
        assert "CSS" in result.languages
        assert "JSON" in result.languages


def test_gitignore_respected():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _create_project(root)
        (root / ".gitignore").write_text("*.css\n")
        result = analyze(root)

        assert "CSS" not in result.languages


def test_binary_files_skipped():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "image.png").write_bytes(b"\x89PNG\r\n")
        (root / "main.py").write_text("x = 1\n")
        result = analyze(root)

        assert result.total_files == 1
        assert result.skipped_binary == 1


def test_empty_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = analyze(Path(tmpdir))
        assert result.total_files == 0
        assert result.total_lines == 0


def test_largest_files_sorted():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "small.py").write_text("x = 1\n")
        (root / "big.py").write_text("\n".join(f"line_{i} = {i}" for i in range(100)) + "\n")
        result = analyze(root)

        assert result.largest_files[0].path.name == "big.py"

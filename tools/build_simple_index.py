#!/usr/bin/env python3
"""Rebuild simple/, the package index GitHub Pages serves for this repository.

The index lets uv install the server by name, with no version in the command:

    uvx --index https://harmoneyes.github.io/theia-mcp-server/simple/ theia-native-mcp

so a release changes nothing for anyone who has the command (the README's, or
the HarmonEyes dashboard's). It is a PEP 503 "simple" index: one page listing
the projects, and one per project listing its wheels with their sha256, which
uv checks on download. The wheels stay in server/; the pages link to them.

To release: put the new wheel in server/, run this from the repository root,
and commit both.

    python3 tools/build_simple_index.py

Standard library only. The output depends only on the wheels, so running it
twice changes nothing.
"""

from __future__ import annotations

import hashlib
import html
import re
import sys
import zipfile
from email.parser import Parser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WHEELS = ROOT / "server"
INDEX = ROOT / "simple"


def normalized(name: str) -> str:
    """PEP 503's project name normalization: theia_native_mcp -> theia-native-mcp."""
    return re.sub(r"[-_.]+", "-", name).lower()


def requires_python(wheel: Path) -> str | None:
    """The wheel's Requires-Python, from its METADATA, so uv can skip a wheel
    the user's Python cannot run instead of failing after the download."""
    with zipfile.ZipFile(wheel) as archive:
        metadata = next(n for n in archive.namelist() if n.endswith(".dist-info/METADATA"))
        return Parser().parsestr(archive.read(metadata).decode("utf-8")).get("Requires-Python")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def page(title: str, links: list[str]) -> str:
    body = "\n".join(links)
    return (
        "<!DOCTYPE html>\n"
        f"<html><head><meta name=\"pypi:repository-version\" content=\"1.0\"><title>{html.escape(title)}</title></head>\n"
        f"<body>\n{body}\n</body></html>\n"
    )


def main() -> int:
    wheels = sorted(WHEELS.glob("*.whl"))
    if not wheels:
        print(f"no wheels in {WHEELS}", file=sys.stderr)
        return 1

    projects: dict[str, list[Path]] = {}
    for wheel in wheels:
        projects.setdefault(normalized(wheel.name.split("-", 1)[0]), []).append(wheel)

    for project, files in projects.items():
        links = []
        for wheel in files:
            # Relative: the same pages work at any Pages URL, and locally.
            href = f"../../{wheel.relative_to(ROOT).as_posix()}#sha256={sha256(wheel)}"
            python = requires_python(wheel)
            attr = f' data-requires-python="{html.escape(python)}"' if python else ""
            links.append(f'<a href="{html.escape(href)}"{attr}>{html.escape(wheel.name)}</a><br>')
        (INDEX / project).mkdir(parents=True, exist_ok=True)
        (INDEX / project / "index.html").write_text(page(f"Links for {project}", links), encoding="utf-8")

    project_links = [f'<a href="{html.escape(p)}/">{html.escape(p)}</a><br>' for p in sorted(projects)]
    (INDEX / "index.html").write_text(page("Simple index", project_links), encoding="utf-8")

    for project, files in sorted(projects.items()):
        print(f"{project}: {', '.join(w.name for w in files)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

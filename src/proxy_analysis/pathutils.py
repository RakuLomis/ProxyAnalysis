"""Filesystem helpers, including Windows long-path access."""

from __future__ import annotations

import os
from pathlib import Path


def filesystem_path(path: Path | str) -> str:
    """Return an absolute OS path suitable for I/O without changing lineage names."""
    resolved = str(Path(path).resolve())
    if os.name != "nt" or resolved.startswith("\\\\?\\"):
        return resolved
    if resolved.startswith("\\\\"):
        return "\\\\?\\UNC\\" + resolved[2:]
    return "\\\\?\\" + resolved


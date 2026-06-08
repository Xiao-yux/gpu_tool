"""negpu - async-first GPU/Server testing toolkit.

This package is a full rewrite of the original ``gpu_tool`` project.
It is built on top of asyncio, pydantic and typer, and is intended to be
distributable as both a Python wheel and a single-file Nuitka binary.
"""

from __future__ import annotations

from negpu._version import __version__

__all__ = ["__version__"]
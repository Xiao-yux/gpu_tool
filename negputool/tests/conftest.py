"""pytest configuration / shared fixtures for negpu.

Phase 1 only provides the bare minimum (no fixtures yet) so that
``pytest`` can discover the test files.  More fixtures will be added
in Phase 2+ (e.g. ``tmp_config``, ``mock_subprocess``, ``fake_screen``).
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make sure ``import negpu`` works without installing the package in
# editable mode (e.g. when running tests directly via ``pytest tests/``).
# With src-layout the package lives under ``src/``, so we add BOTH the
# project root and ``src/`` to sys.path.
_ROOT = Path(__file__).resolve().parent.parent
_SRC = _ROOT / "src"
for p in (_ROOT, _SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

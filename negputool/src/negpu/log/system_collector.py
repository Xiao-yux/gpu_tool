"""negpu.log.system_collector - async startup-time system info capture.

Per REFACTORING_TASK [6]A and [7]A: at startup we run a fixed set of
inspection commands and write their stdout to ``system/<name>.log``.
Failures of any single command are isolated — the others still run,
and the failed one is replaced by a ``# command not available: ...``
placeholder so the user can tell what happened.

Commands collected (the full set; tune via :attr:`SystemCollector.commands`):

* ``dmesg``
* ``nvidia-smi``
* ``lspci -vvv``
* ``lsblk -O``
* ``ipmitool lan print``
* ``ipmitool sdr``
* ``ipmitool fru``
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import ClassVar


class SystemCollector:
    """Collect a fixed snapshot of system info at startup."""

    # Per REFACTORING_TASK [6]A
    DEFAULT_COMMANDS: ClassVar[dict[str, tuple[str, ...]]] = {
        "dmesg": ("dmesg",),
        "nvidia-smi": ("nvidia-smi",),
        "lspci": ("lspci", "-vvv"),
        "lsblk": ("lsblk", "-O"),
        "ipmitool-lan": ("ipmitool", "lan", "print"),
        "ipmitool-sdr": ("ipmitool", "sdr"),
        "ipmitool-fru": ("ipmitool", "fru"),
    }

    def __init__(
        self,
        target_dir: Path,
        commands: dict[str, tuple[str, ...]] | None = None,
    ) -> None:
        self.target = target_dir
        self.commands: dict[str, tuple[str, ...]] = commands or dict(self.DEFAULT_COMMANDS)

    async def collect_all(self) -> dict[str, bool]:
        """Run all commands concurrently and write outputs to ``target_dir``.

        Returns a mapping of ``name -> success``. Failures of one
        command never affect the others (per REFACTORING_TASK [7]A).
        """
        self.target.mkdir(parents=True, exist_ok=True)
        results = await asyncio.gather(
            *(self._run(name) for name in self.commands),
        )
        return dict(zip(self.commands, results, strict=True))

    async def collect(self, name: str) -> bool:
        """Run a single command and write to ``target_dir/<name>.log``."""
        if name not in self.commands:
            raise KeyError(f"unknown collector: {name!r}")
        return await self._run(name)

    async def _run(self, name: str) -> bool:
        cmd = self.commands[name]
        target = self.target / f"{name}.log"
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
        except FileNotFoundError as e:
            target.write_text(
                f"# command not available: {' '.join(cmd)}\n# error: {e}\n",
                encoding="utf-8",
            )
            return False
        except PermissionError as e:
            target.write_text(
                f"# permission denied: {' '.join(cmd)}\n# error: {e}\n",
                encoding="utf-8",
            )
            return False
        try:
            stdout, _ = await proc.communicate()
        except OSError as e:
            target.write_text(
                f"# failed to read: {' '.join(cmd)}\n# error: {e}\n",
                encoding="utf-8",
            )
            return False
        target.write_bytes(stdout)
        return True
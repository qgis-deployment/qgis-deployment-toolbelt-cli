#! python3  # noqa: E265

"""Structures of reports."""

# standard library
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CleanupReport:
    """Structure to summarize a cleanup."""

    removed: list[Path] = field(default_factory=list)
    failed: list[Path] = field(default_factory=list)

    def __len__(self) -> int:
        """Number of resources actually removed (or that would be, in dry-run mode).

        Returns:
            int: count of removed resources
        """
        return len(self.removed)

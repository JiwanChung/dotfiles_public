"""Manifest file (files.yaml) parsing and management."""

from pathlib import Path
from dataclasses import dataclass
from typing import Optional

import yaml


@dataclass
class FileEntry:
    """A single file entry in the manifest."""

    source: Path  # Relative to dotfiles repo
    dest: Path  # Relative to $HOME
    type: str  # "symlink" or "copy"
    platform: Optional[str] = None  # "darwin", "linux", or None for all


@dataclass
class Manifest:
    """Manifest of tracked files."""

    entries: list[FileEntry]
    path: Path  # Path to manifest file

    @classmethod
    def load(cls, path: Path) -> "Manifest":
        """Load manifest from YAML file."""
        if not path.exists():
            return cls(entries=[], path=path)

        with open(path) as f:
            data = yaml.safe_load(f) or {}

        entries = []

        # New format: list of entries
        if "entries" in data:
            for item in data["entries"]:
                entries.append(FileEntry(
                    source=Path(item["source"]),
                    dest=Path(item["dest"]),
                    type=item.get("type", "symlink"),
                    platform=item.get("platform"),
                ))
        else:
            # Legacy format: symlinks/copies dicts
            for src, dest in data.get("symlinks", {}).items():
                entries.append(FileEntry(Path(src), Path(dest), "symlink"))

            for src, dest in data.get("copies", {}).items():
                entries.append(FileEntry(Path(src), Path(dest), "copy"))

            for platform, sections in data.get("platform", {}).items():
                for src, dest in sections.get("symlinks", {}).items():
                    entries.append(FileEntry(Path(src), Path(dest), "symlink", platform))
                for src, dest in sections.get("copies", {}).items():
                    entries.append(FileEntry(Path(src), Path(dest), "copy", platform))

        return cls(entries, path)

    def save(self):
        """Save manifest back to YAML file."""
        data: dict = {"symlinks": {}}

        for entry in self.entries:
            section = "symlinks" if entry.type == "symlink" else "copies"

            if entry.platform:
                # Platform-specific entry
                if "platform" not in data:
                    data["platform"] = {}
                if entry.platform not in data["platform"]:
                    data["platform"][entry.platform] = {}
                if section not in data["platform"][entry.platform]:
                    data["platform"][entry.platform][section] = {}
                data["platform"][entry.platform][section][str(entry.source)] = str(entry.dest)
            else:
                # Global entry
                if section not in data:
                    data[section] = {}
                data[section][str(entry.source)] = str(entry.dest)

        # Clean empty sections
        for key in list(data.keys()):
            if not data[key]:
                del data[key]
        if "platform" in data:
            for plat in list(data["platform"].keys()):
                for section in list(data["platform"][plat].keys()):
                    if not data["platform"][plat][section]:
                        del data["platform"][plat][section]
                if not data["platform"][plat]:
                    del data["platform"][plat]
            if not data["platform"]:
                del data["platform"]

        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def add(
        self,
        source: Path,
        dest: Path,
        type: str = "symlink",
        platform: Optional[str] = None,
    ):
        """Add a new entry to the manifest."""
        # Check if already exists
        for entry in self.entries:
            if entry.dest == dest:
                # Update existing
                entry.source = source
                entry.type = type
                entry.platform = platform
                self.save()
                return

        self.entries.append(FileEntry(source, dest, type, platform))
        self.save()

    def remove(self, dest: Path) -> bool:
        """Remove an entry by destination path."""
        for i, entry in enumerate(self.entries):
            if entry.dest == dest:
                self.entries.pop(i)
                self.save()
                return True
        return False

    def find_by_dest(self, dest: Path) -> Optional[FileEntry]:
        """Find entry by destination path."""
        for entry in self.entries:
            if entry.dest == dest:
                return entry
        return None

    def for_platform(self, platform: str) -> list[FileEntry]:
        """Filter entries for given platform."""
        return [
            e for e in self.entries
            if e.platform is None or e.platform == platform
        ]

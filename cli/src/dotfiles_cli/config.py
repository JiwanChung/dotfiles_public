"""Configuration and path management for dotfiles-cli."""

import os
import platform
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class Config:
    """Configuration for dotfiles-cli."""

    dotfiles_path: Path
    config_path: Path  # config/
    platform_path: Path  # platform/
    files_yaml: Path
    packages_yaml: Path
    scripts_path: Path
    git_crypt_key: Path
    publish_yaml: Path

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from environment and defaults."""
        # DOTFILES env var or default to ~/dotfiles
        dotfiles = Path(os.environ.get("DOTFILES", Path.home() / "dotfiles"))
        config = dotfiles / "config"

        return cls(
            dotfiles_path=dotfiles,
            config_path=config,
            platform_path=dotfiles / "platform",
            files_yaml=config / "files.yaml",
            packages_yaml=config / "packages.yaml",
            scripts_path=dotfiles / "scripts",
            git_crypt_key=Path.home() / ".dotfiles-key",
            publish_yaml=config / "publish.yaml",
        )

    @property
    def platform(self) -> str:
        """Get current platform: 'darwin', 'linux', or 'windows'."""
        system = platform.system().lower()
        if system == "darwin":
            return "darwin"
        elif system == "linux":
            return "linux"
        elif system == "windows":
            return "windows"
        return system

    @property
    def is_macos(self) -> bool:
        return self.platform == "darwin"

    @property
    def is_linux(self) -> bool:
        return self.platform == "linux"

    def ensure_dirs(self):
        """Ensure required directories exist."""
        self.config_path.mkdir(parents=True, exist_ok=True)
        self.scripts_path.mkdir(parents=True, exist_ok=True)
        self.platform_path.mkdir(parents=True, exist_ok=True)


# Global config instance
_config: Config | None = None


def get_config() -> Config:
    """Get or create the global config instance."""
    global _config
    if _config is None:
        _config = Config.load()
    return _config

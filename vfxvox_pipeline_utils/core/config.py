"""Configuration management for VFXVox Pipeline Utils."""

import yaml
from pathlib import Path
from typing import Any, Optional


class Config:
    """Manages configuration loading and access."""

    def __init__(self, config_path: Optional[Path] = None):
        """Load configuration from file or use defaults.

        Args:
            config_path: Path to YAML configuration file
        """
        self._config = {}

        if config_path and Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key.

        Args:
            key: Configuration key (supports dot notation like 'sequences.check_resolution')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default

            if value is None:
                return default

        return value

    @classmethod
    def from_dict(cls, data: dict) -> "Config":
        """Create config from dictionary.

        Args:
            data: Configuration dictionary

        Returns:
            Config instance
        """
        config = cls()
        config._config = data
        return config

"""Configuration management for VFXVox Pipeline Utils."""

import yaml
from pathlib import Path
from typing import Any, Optional, Dict


class Config:
    """Manages configuration loading and access."""

    def __init__(self, config_path: Optional[Path] = None):
        """Load configuration from file or use defaults.

        Args:
            config_path: Path to YAML configuration file
        """
        self._config = self._load_default_config()

        if config_path and Path(config_path).exists():
            user_config = self._load_yaml(config_path)
            self._config = self._merge_configs(self._config, user_config)

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

    def _load_yaml(self, path: Path) -> Dict:
        """Load YAML configuration file.

        Args:
            path: Path to YAML file

        Returns:
            Configuration dictionary
        """
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _load_default_config(self) -> Dict:
        """Load default configuration.

        Returns:
            Default configuration dictionary
        """
        return {
            "sequences": {
                "supported_formats": ["exr", "dpx", "png", "jpg", "tiff"],
                "check_resolution": True,
                "check_bit_depth": True,
                "check_metadata": False,
            },
            "usd": {
                "max_layer_depth": 10,
                "check_references": True,
                "check_schemas": True,
                "check_performance": True,
                "custom_rules_path": None,
            },
            "shotlint": {
                "fail_on": "error",  # 'error', 'warning', 'none'
            },
            "logging": {
                "level": "INFO",
                "file": None,
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        }

    def _merge_configs(self, base: Dict, override: Dict) -> Dict:
        """Merge two configuration dictionaries recursively.

        Args:
            base: Base configuration
            override: Configuration to merge (takes precedence)

        Returns:
            Merged configuration
        """
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

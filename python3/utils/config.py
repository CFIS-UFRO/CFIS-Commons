import json
import logging
from pathlib import Path
from typing import Any, Optional

# --------------------------------------------------------------------------------------------------
# Configuration Utility
# --------------------------------------------------------------------------------------------------

class Config:
    """Configuration manager for project settings."""

    _base_config: dict[str, Any] | None = None
    _user_config: dict[str, Any] | None = None
    _merged_config: dict[str, Any] | None = None
    _base_config_path: Path | None = None
    _user_config_path: Path | None = None
    _logger: logging.Logger = None

    @classmethod
    def init_config(cls, base_config_path: Path | str | None = None, user_config_path: Path | str | None = None, logger: Optional[logging.Logger] = None) -> None:
        """Initialize configuration paths and create files if they don't exist.

        Args:
            base_config_path: Path to the base configuration file (config.json)
            user_config_path: Path to the user configuration file (user_config.json)
            logger: Logger instance for logging. If None, no logging will occur.

        If paths are not provided, default paths relative to this module will be used.
        If files don't exist, they will be created with default empty configuration.
        """
        # Setup logger (use NullHandler if None to silently discard logs)
        if logger is None:
            cls._logger = logging.getLogger(__name__)
            cls._logger.addHandler(logging.NullHandler())
        else:
            cls._logger = logger

        # Set paths
        if base_config_path is not None:
            cls._base_config_path = Path(base_config_path)
        else:
            cls._base_config_path = Path(__file__).parent.parent / 'config.json'

        if user_config_path is not None:
            cls._user_config_path = Path(user_config_path)
        else:
            cls._user_config_path = Path(__file__).parent.parent / 'user_config.json'

        # Create base config if it doesn't exist
        if not cls._base_config_path.exists():
            cls._base_config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(cls._base_config_path, 'w') as f:
                json.dump({}, f, indent=2)
                f.write('\n')

        # Create user config if it doesn't exist
        if not cls._user_config_path.exists():
            cls._user_config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(cls._user_config_path, 'w') as f:
                json.dump({}, f, indent=2)
                f.write('\n')

        # Reset cached config to force reload with new paths
        cls._base_config = None
        cls._user_config = None
        cls._merged_config = None

    @classmethod
    def get(cls, key: str | None = None) -> dict[str, Any] | Any:
        """Get project configuration from config.json merged with user_config.json.

        Loads default configuration from config.json and merges it with user overrides
        from user_config.json if it exists.

        Args:
            key: Optional configuration key to retrieve. If None, returns entire config.

        Returns:
            If key is None: returns the entire configuration dictionary
            If key is provided: returns the value for that key

        Raises:
            KeyError: If the key does not exist in the configuration

        Usage:
            config = Config.get()  # Get entire config
            project_name = Config.get('project_name')  # Get specific value
            log_folder = Config.get('log_folder')  # Get specific value
        """
        if cls._merged_config is None:
            # Initialize paths if not already done
            if cls._base_config_path is None or cls._user_config_path is None:
                cls.init_config()

            # Load base config
            cls._logger.info(f"Loading base configuration file: {cls._base_config_path}")
            with open(cls._base_config_path, 'r') as f:
                cls._base_config = json.load(f)
            cls._merged_config = cls._base_config.copy()
            # Load user config and merge
            cls._logger.info(f"Loading user configuration file: {cls._user_config_path}")
            if cls._user_config_path.exists():
                with open(cls._user_config_path, 'r') as f:
                    cls._user_config = json.load(f)
                    cls._logger.info(f"Merging user configuration into base configuration")
                    cls._merged_config.update(cls._user_config)
            else:
                cls._user_config = {}

        if key is None:
            return cls._merged_config
        else:
            if key not in cls._merged_config:
                raise KeyError(f"Configuration key '{key}' does not exist")
            cls._logger.info(f"Retrieving configuration key '{key}' with value: {cls._merged_config[key]}")
            return cls._merged_config[key]

    @classmethod
    def update(cls, key: str, value: Any) -> None:
        """Update a configuration value and save to user_config.json.

        Only saves values that differ from default configuration.

        Args:
            key: Configuration key to update
            value: New value for the configuration key

        Raises:
            KeyError: If the key does not exist in default configuration
        """

        # Initialize merged config if not already done
        if cls._merged_config is None:
            cls.get()

        # Initialize paths if not already done
        if cls._user_config_path is None:
            cls.init_config()

        if cls._base_config is not None and key not in cls._base_config:
            raise KeyError(f"Configuration key '{key}' does not exist in default configuration")
        if cls._merged_config is not None:
            cls._logger.info(f"Updating configuration key '{key}' with new value")
            cls._merged_config[key] = value
        user_config_data: dict[str, Any] = {}
        if cls._merged_config is not None and cls._base_config is not None:
            for k, v in cls._merged_config.items():
                if k in cls._base_config and cls._base_config[k] != v:
                    user_config_data[k] = v
        with open(cls._user_config_path, 'w') as f:
            json.dump(user_config_data, f, indent=2)
            f.write('\n')
        cls._logger.info(f"User configuration saved to: {cls._user_config_path}")
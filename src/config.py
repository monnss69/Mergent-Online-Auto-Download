from pathlib import Path
from typing import Dict, Any
import json

class Config:
    """Configuration management for the scraper"""
    
    DEFAULT_CONFIG = {
        'max_requests_per_hour': 1000,
        'output_dir': 'downloads',
        'retry_attempts': 5,
        'request_timeout': 30,
        'chrome_options': {
            'headless': False,
            'disable_gpu': True,
            'no_sandbox': True,
            'disable_dev_shm_usage': True
        },
        'download_settings': {
            'chunk_size': 8192,
            'min_delay': 0.5,
            'max_delay': 2.0
        },
        'human_behavior': {
            'min_action_delay': 0.5,
            'max_action_delay': 3.0,
            'scroll_probability': 0.7,
            'mouse_movement_probability': 0.8
        }
    }

    def __init__(self, config_file: str = None):
        self.config = self.DEFAULT_CONFIG.copy()
        if config_file:
            self.load_config(config_file)
        self._validate_config()

    def load_config(self, config_file: str) -> None:
        """Load configuration from JSON file"""
        try:
            config_path = Path(config_file)
            if config_path.exists():
                with open(config_path) as f:
                    user_config = json.load(f)
                self._update_config(user_config)
        except Exception as e:
            raise ValueError(f"Error loading config file: {str(e)}")

    def _update_config(self, user_config: Dict[str, Any]) -> None:
        """Update configuration with user values"""
        def update_dict(base: dict, update: dict) -> None:
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    update_dict(base[key], value)
                else:
                    base[key] = value

        update_dict(self.config, user_config)

    def _validate_config(self) -> None:
        """Validate configuration values"""
        if self.config['max_requests_per_hour'] <= 0:
            raise ValueError("max_requests_per_hour must be positive")
            
        # Create output directory if it doesn't exist
        output_dir = Path(self.config['output_dir'])
        output_dir.mkdir(parents=True, exist_ok=True)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)

    def __getitem__(self, key: str) -> Any:
        """Get configuration value using dictionary syntax"""
        return self.config[key]

    def update(self, updates: Dict[str, Any]) -> None:
        """Update configuration with new values"""
        self._update_config(updates)
        self._validate_config()

    @property
    def chrome_options(self) -> Dict[str, Any]:
        """Get Chrome browser options"""
        return self.config['chrome_options']

    @property
    def download_settings(self) -> Dict[str, Any]:
        """Get download settings"""
        return self.config['download_settings']

    @property
    def human_behavior(self) -> Dict[str, Any]:
        """Get human behavior simulation settings"""
        return self.config['human_behavior']
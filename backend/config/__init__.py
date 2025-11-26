import os

from typing import Optional

from backend.config.settings import DevelopmentConfig, ProductionConfig, TestingConfig


def get_config(config_name: Optional[str] = None):
    env = config_name or os.getenv("APP_ENV") or os.getenv("FLASK_ENV") or "development"
    env = env.lower()
    mapping = {
        "dev": DevelopmentConfig,
        "development": DevelopmentConfig,
        "prod": ProductionConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
        "test": TestingConfig,
    }
    config_cls = mapping.get(env)
    if not config_cls:
        raise RuntimeError(f"Unknown config environment: {env}")
    return config_cls()

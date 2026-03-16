import os
import yaml

CONFIG_PATH = os.getenv('CONFIG_PATH', '/config/algorithm.yaml')


def load_config() -> dict:
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

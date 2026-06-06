import yaml
from pathlib import Path


def load_config(config_path: str | Path) -> dict:
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError(f"Конфиг-файл не найден по пути: {path}")

    config = yaml.safe_load(path.read_text(encoding='utf-8'))

    if config is None:
        raise ValueError(f"Конфиг-файл по пути {path} пустой или содержит некорректный YAML")

    return config

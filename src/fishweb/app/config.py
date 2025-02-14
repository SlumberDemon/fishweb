from __future__ import annotations

from pydantic_settings import BaseSettings
from pydantic import BaseModel
import yaml
from pathlib import Path

# idea for fishweb.yaml:
"""
backend: uvicorn # maybe
load_env: true
auto_deps: true # automatic?
public_routes:
  - "/*"
public: true # maybe
crons:
  - id: "cleanup"
    interval: "0/15 * * * *"
"""


class Cron(BaseModel):
    id: str
    interval: str


class FishwebConfig(BaseSettings):
    git_reloading: bool = False
    load_env: bool = True
    public_routes: list[str] = []
    auto_deps: dict[str, Path] = {}
    crons: list[Cron] = []


def load_config(app_dir: Path) -> FishwebConfig | None:
    config_file = app_dir / "fishweb.yaml"

    if config_file.exists():
        with config_file.open("r") as file:
            config_data = yaml.safe_load(file)

            return FishwebConfig().model_validate(config_data)
    return None

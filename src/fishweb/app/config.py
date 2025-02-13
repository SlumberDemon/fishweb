from pydantic_settings import BaseSettings
from pydantic import BaseModel
import yaml
from pathlib import Path
from typing import List

# idea for fishweb.yaml:
"""
favicon: icon.png # maybe
backend: uvicorn # maybe
load_env: true
auto_deps:
  path: requirements.txt # allow for pyproject?
auto_deps: requirements.txt # simplier?
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
    load_env: bool = True
    public_routes: List[str] = []
    auto_deps: dict[str, Path] = {}
    crons: List[Cron] = []


def load_config(app_dir: Path) -> FishwebConfig:
    config_file = app_dir / "fishweb.yaml"

    if config_file.exists():
        with config_file.open("r") as file:
            config_data = yaml.safe_load(file)

            return FishwebConfig().model_validate(config_data)

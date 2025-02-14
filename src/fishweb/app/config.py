from enum import Enum
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, YamlConfigSettingsSource


class AppType(Enum):
    ASGI = "asgi"
    STATIC = "static"


class Cron(BaseModel):
    id: str
    interval: str


class AppConfig(BaseSettings):
    app_type: AppType = AppType.ASGI
    entry: str = "main:app"
    venv_path: Path = Path(".venv")
    reload: bool = False
    crons: list[Cron] = []

    def __init__(self, app_dir: Path, /) -> None:
        original_yaml_file = self.model_config.get("yaml_file")
        self.model_config["yaml_file"] = app_dir / "fishweb.yaml"
        super().__init__()
        self.model_config["yaml_file"] = original_yaml_file

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        dotenv_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        file_secret_settings: PydanticBaseSettingsSource,  # noqa: ARG003
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            YamlConfigSettingsSource(settings_cls),
        )

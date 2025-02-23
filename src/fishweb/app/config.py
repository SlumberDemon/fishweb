from enum import Enum
from pathlib import Path

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource


class AppType(Enum):
    ASGI = "asgi"
    WSGI = "wsgi"
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

    @classmethod
    def load_from_dir(cls, app_dir: Path, /) -> "AppConfig":
        file_path = app_dir / "fishweb.yaml"
        if file_path.is_file():
            with file_path.open() as file:
                return cls.model_validate(yaml.safe_load(file) or {})
        return cls.model_validate({})

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],  # noqa: ARG003
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        dotenv_settings: PydanticBaseSettingsSource,  # noqa: ARG003
        file_secret_settings: PydanticBaseSettingsSource,  # noqa: ARG003
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (init_settings,)

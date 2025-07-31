from __future__ import annotations

import sys
from enum import Enum
from pathlib import Path

import yaml
from platformdirs import user_runtime_dir
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


class AppType(Enum):
    STATIC = "static"
    PROCESS = "process"


class Cron(BaseModel):
    id: str
    interval: str
    # name and description for a frontend?


class AppConfig(BaseSettings):
    app_type: AppType = Field(
        default=AppType.STATIC,
        alias="type",
    )
    run_cmd: str = Field(default="", alias="run")
    port: int | None = None
    reload: bool = False
    crons: list[Cron] = []

    @classmethod
    def load_from_dir(cls, app_dir: Path, /) -> AppConfig:
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


class Serve(BaseModel):
    host: str = "localhost"
    port: int = 8888


class Logging(BaseModel):
    path: Path = Path(user_runtime_dir("fishweb", appauthor=False)) / "logs"


class GlobalConfig(BaseSettings):
    root_dir: Path = Path.home() / "fishweb"
    reload: bool = False
    serve: Serve = Field(default_factory=Serve)
    logging: Logging = Field(default_factory=Logging)

    @classmethod
    def load_from_dir(cls, root_dir: Path, /) -> GlobalConfig:
        file_path = root_dir / "config.toml"

        if file_path.is_file():
            with file_path.open("rb") as file:
                return cls.model_validate(tomllib.load(file) or {})
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

"""Configuration management with hot reload support."""

import logging
from pathlib import Path
from typing import Any, Literal, Union

import yaml
from pydantic import BaseModel, Field, field_validator, model_validator
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class LLMConfig(BaseModel):
    provider: str
    model: str
    api_key: str
    api_base: str | None = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, gt=0)

    @field_validator("api_base")
    @classmethod
    def api_base_must_be_url(cls, v: str | None) -> str | None:
        if v is not None and not v.startswith(("http://", "https://")):
            raise ValueError("api_base must be a valid URL")
        return v


class TelegramConfig(BaseModel):
    enabled: bool = True
    bot_token: str
    allowed_user_ids: list[str] = Field(default_factory=list)


class DiscordConfig(BaseModel):
    enabled: bool = True
    bot_token: str
    channel_ids: list[str] = Field(default_factory=list)
    allowed_user_ids: list[str] = Field(default_factory=list)


class BraveWebSearchConfig(BaseModel):
    provider: Literal["brave"] = "brave"
    api_key: str


class TavilyWebSearchConfig(BaseModel):
    provider: Literal["tavily"] = "tavily"
    api_key: str


class Crawl4AIWebReadConfig(BaseModel):
    provider: Literal["crawl4ai"] = "crawl4ai"


class ApiConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = Field(default=8000, gt=0, lt=65536)


class SourceSessionConfig(BaseModel):
    session_id: str


class ChannelConfig(BaseModel):
    enabled: bool = False
    telegram: TelegramConfig | None = None
    discord: DiscordConfig | None = None


class Config(BaseModel):
    workspace: Path
    llm: LLMConfig
    default_agent: str
    agents_path: Path = Field(default=Path("agents"))
    skills_path: Path = Field(default=Path("skills"))
    crons_path: Path = Field(default=Path("crons"))
    logging_path: Path = Field(default=Path(".logs"))
    history_path: Path = Field(default=Path(".history"))
    event_path: Path = Field(default=Path(".event"))
    websearch: Union[BraveWebSearchConfig, TavilyWebSearchConfig, None] = None
    webread: Crawl4AIWebReadConfig | None = None
    channels: ChannelConfig = Field(default_factory=ChannelConfig)
    api: ApiConfig = Field(default_factory=ApiConfig)
    sources: dict[str, SourceSessionConfig] = Field(default_factory=dict)
    routing: dict = Field(default_factory=lambda: {"bindings": []})
    default_delivery_source: str | None = None

    @model_validator(mode="after")
    def resolve_paths(self) -> "Config":
        for field_name in (
            "agents_path", "skills_path", "crons_path",
            "logging_path", "history_path", "event_path",
        ):
            path = getattr(self, field_name)
            if not path.is_absolute():
                setattr(self, field_name, self.workspace / path)
        return self

    @classmethod
    def load(cls, workspace_dir: Path) -> "Config":
        config_data = cls._load_merged_configs(workspace_dir)
        config_data["workspace"] = workspace_dir
        return cls.model_validate(config_data)

    @classmethod
    def _load_merged_configs(cls, workspace_dir: Path) -> dict[str, Any]:
        config_data: dict[str, Any] = {}
        user_config = workspace_dir / "config.user.yaml"
        runtime_config = workspace_dir / "config.runtime.yaml"

        if user_config.exists():
            with open(user_config, encoding="utf-8") as f:
                config_data = cls._deep_merge(config_data, yaml.safe_load(f) or {})

        if runtime_config.exists():
            with open(runtime_config, encoding="utf-8") as f:
                config_data = cls._deep_merge(config_data, yaml.safe_load(f) or {})

        return config_data

    @staticmethod
    def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = Config._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    def _set_nested(self, obj: dict, key: str, value: Any) -> None:
        keys = key.split(".")
        for k in keys[:-1]:
            if k not in obj or not isinstance(obj[k], dict):
                obj[k] = {}
            obj = obj[k]
        obj[keys[-1]] = value

    def _set_config_value(self, config_path: Path, key: str, value: Any) -> None:
        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {}

        if isinstance(value, BaseModel):
            value = value.model_dump()

        self._set_nested(data, key, value)

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f)

    def set_user(self, key: str, value: Any) -> None:
        self._set_config_value(self.workspace / "config.user.yaml", key, value)

    def set_runtime(self, key: str, value: Any) -> None:
        self._set_config_value(self.workspace / "config.runtime.yaml", key, value)

    def reload(self) -> bool:
        try:
            config_data = self._load_merged_configs(self.workspace)
            config_data["workspace"] = self.workspace
            new_config = Config.model_validate(config_data)
            for field_name in Config.model_fields:
                setattr(self, field_name, getattr(new_config, field_name))
            return True
        except Exception as e:
            logging.debug("Config reload failed: %s", e)
            return False


class ConfigHandler(FileSystemEventHandler):
    def __init__(self, config: Config):
        self._config = config

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith("config.user.yaml"):
            self._config.reload()


class ConfigReloader:
    def __init__(self, config: Config):
        self._config = config
        self._observer = Observer()

    def start(self) -> None:
        handler = ConfigHandler(self._config)
        self._observer.schedule(handler, str(self._config.workspace), recursive=False)
        self._observer.start()

    def stop(self) -> None:
        self._observer.stop()
        self._observer.join()
        del self._observer
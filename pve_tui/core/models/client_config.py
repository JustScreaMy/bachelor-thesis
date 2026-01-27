import tomllib
from typing import Self, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ApplicationConfig:
    contexts: dict[str, ContextConfig]

    @classmethod
    def from_toml(cls, path: Path) -> Self:
        file = Path(path)
        if not file.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        with file.open("rb") as f:
            data = tomllib.load(f)
        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict[Any, Any]) -> Self:
        try:
            contexts = {
                name: ContextConfig.from_dict(ctx_data)
                for name, ctx_data in data.get("contexts", {}).items()
            }
            return cls(contexts=contexts)
        except KeyError:
            raise ValueError("Invalid application configuration data")


@dataclass(frozen=True)
class ContextConfig:
    base_url: str
    token_id: str
    token: str

    @classmethod
    def from_dict(cls, data: dict[Any, Any]) -> Self:
        try:
            return cls(
                base_url=data["base_url"],
                token_id=data["token_id"],
                token=data["token"],
            )
        except KeyError:
            raise ValueError("Missing required context configuration fields")
